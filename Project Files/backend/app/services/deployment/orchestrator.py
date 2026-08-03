import os
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from cryptography.fernet import Fernet

from app.models.deployment import (
    ModelDeployment,
    DeploymentEnvironment,
    DeploymentPolicy,
    DeploymentApproval,
    DeploymentEvent,
    DeploymentEnvironmentVariable,
    DeploymentVersion,
    DeploymentTag,
)
from app.repositories.interfaces.deployment import DeploymentRepository
from app.services.deployment.exceptions import (
    FreezeWindowActiveError,
    PolicyViolationError,
    IncompatibleProviderError,
    LockAcquisitionError,
)
from app.services.deployment.freeze import FreezeWindowService
from app.services.deployment.state_machine import DeploymentStateMachine
from app.services.deployment.providers import ProviderRegistry
from app.services.deployment.checkpoints import CheckpointManager

# Set up a static/in-memory key for Fernet encryption of environment variables
FERNET_KEY = Fernet.generate_key()
cipher_suite = Fernet(FERNET_KEY)

class DeploymentOrchestrator:
    """Orchestrator managing the lifecycle, policies, approvals, and secrets of model deployments."""

    def __init__(self, repo: DeploymentRepository, checkpoint_mgr: CheckpointManager):
        self.repo = repo
        self.checkpoint_mgr = checkpoint_mgr

    def encrypt_val(self, val: str) -> str:
        """Encrypts a string value using Fernet."""
        return cipher_suite.encrypt(val.encode()).decode()

    def decrypt_val(self, encrypted_val: str) -> str:
        """Decrypts a Fernet encrypted string."""
        return cipher_suite.decrypt(encrypted_val.encode()).decode()

    async def create_deployment_record(
        self,
        project_id: uuid.UUID,
        model_id: uuid.UUID,
        environment_id: uuid.UUID,
        strategy: str,
        deployment_version: str,
        user_id: uuid.UUID,
        idempotency_key: Optional[str] = None,
        variables: List[Dict[str, Any]] = None,
        tags: Dict[str, str] = None,
    ) -> ModelDeployment:
        """Validates freeze windows, permissions, and creates a deployment in DRAFT state."""
        # 1. Validate freeze windows
        now_dt = datetime.now(timezone.utc)
        freeze_windows = await self.repo.list_freeze_windows(project_id)
        if FreezeWindowService.is_frozen(now_dt, freeze_windows):
            raise FreezeWindowActiveError("Deployment blocked by active freeze window.")

        # 2. Get active policy
        policy = await self.repo.get_active_policy(project_id)
        if not policy:
            raise PolicyViolationError("No active deployment policy configured for this project.")

        # 3. Resolve environment details
        env = await self.repo.get_environment(environment_id)
        if not env:
            raise PolicyViolationError(f"Deployment environment '{environment_id}' does not exist.")

        # 4. Check Provider capabilities
        # For simplicity, assume Kubernetes or Local provider
        provider_name = "KUBERNETES" if env.is_production else "LOCAL"
        requires_enc = any(var.get("required", False) for var in (variables or []))
        # Validate compatibility
        ProviderRegistry.validate_compatibility(
            provider_name=provider_name,
            strategy=strategy,
            requires_encryption=requires_enc,
        )

        # 5. Check Idempotency
        if idempotency_key:
            existing = await self.repo.get_by_idempotency_key(user_id, idempotency_key)
            if existing:
                return existing

        # Create Model Deployment
        deployment = ModelDeployment(
            project_id=project_id,
            model_id=model_id,
            environment_id=environment_id,
            policy_version_id=policy.id,
            deployment_version=deployment_version,
            status="DRAFT",
            strategy=strategy.upper(),
            traffic_percentage=0,
            idempotency_key=idempotency_key,
            created_by=user_id,
            state_version=1,
            version_number=1,
            # Mock artifact provenance details
            artifact_repository="docker.io/opticrop/models",
            artifact_digest="sha256:d8b28f7422f293b13487c6999b17646a782b5f79aa806b12d5cf720b0bc87295",
            artifact_size_bytes=1024 * 1024 * 142, # 142 MB
            artifact_created_at=datetime.utcnow(),
            artifact_signed_by="OptiCrop-CI-Worker-04",
            manifest_version="v1",
            manifest_checksum="6e839e448fb5e443b933bf39aecd9127a462",
            manifest_schema_version="1.0",
        )

        deployment = await self.repo.create_deployment(deployment)

        # Add Variables
        if variables:
            for var in variables:
                val = var.get("value")
                enc_val = self.encrypt_val(val) if val else None
                ref = var.get("secret_reference")
                
                # Resolve secrets references (vault mock)
                if ref:
                    # In a real environment, query vault. Here, we mock it.
                    pass

                db_var = DeploymentEnvironmentVariable(
                    deployment_id=deployment.id,
                    key=var["key"],
                    encrypted_value=enc_val,
                    secret_reference=ref,
                    scope=var.get("scope", "ALL"),
                    required=var.get("required", False),
                )
                await self.repo.create_variable(db_var)

        # Add Tags
        if tags:
            for k, v in tags.items():
                tag = DeploymentTag(deployment_id=deployment.id, key=k, value=v)
                await self.repo.create_tag(tag)

        # Emit Initial Audit Event
        await self.emit_audit_event(
            deployment,
            event_type="DeploymentCreated",
            previous_state=None,
            new_state="DRAFT",
            user_id=user_id,
            reason="Initial creation of deployment record in Draft mode.",
        )

        return deployment

    async def transition_state(
        self,
        deployment_id: uuid.UUID,
        next_state: str,
        user_id: uuid.UUID,
        reason: Optional[str] = None,
        expected_state_version: Optional[int] = None,
    ) -> ModelDeployment:
        """Transitions deployment state with central validation, concurrency check, and audit log."""
        deployment = await self.repo.get_deployment(deployment_id)
        if not deployment:
            raise PolicyViolationError(f"Deployment '{deployment_id}' not found.")

        # Concurrency check
        if expected_state_version is not None and deployment.state_version != expected_state_version:
            raise PolicyViolationError(
                f"Concurrency conflict: expected state version {expected_state_version}, got {deployment.state_version}."
            )

        prev_state = deployment.status
        # Validate transition using State Machine
        DeploymentStateMachine.validate_transition(prev_state, next_state)

        # Update state
        deployment.status = next_state.upper()
        deployment.state_version += 1
        await self.repo.update_deployment(deployment)

        # Emit event
        await self.emit_audit_event(
            deployment,
            event_type="DeploymentStateTransitioned",
            previous_state=prev_state,
            new_state=next_state,
            user_id=user_id,
            reason=reason or f"Transitioned from {prev_state} to {next_state}.",
        )

        return deployment

    async def evaluate_approvals(self, deployment_id: uuid.UUID) -> bool:
        """Evaluates whether all policy-required approvals are met."""
        deployment = await self.repo.get_deployment(deployment_id)
        if not deployment:
            return False

        policy = deployment.policy_version
        approvals = await self.repo.get_approvals(deployment_id)

        approved_count = sum(1 for app in approvals if app.decision == "APPROVED")
        if approved_count >= policy.required_approvals:
            return True
        return False

    async def record_approval(
        self,
        deployment_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        decision: str,
        comments: Optional[str] = None,
    ) -> DeploymentApproval:
        """Records an approval decision and evaluates if state can transition to APPROVED."""
        deployment = await self.repo.get_deployment(deployment_id)
        if not deployment:
            raise PolicyViolationError("Deployment not found.")

        # Ensure state is PENDING_APPROVAL
        if deployment.status != "PENDING_APPROVAL":
            raise PolicyViolationError("Approvals can only be submitted for deployments in PENDING_APPROVAL status.")

        approvals = await self.repo.get_approvals(deployment_id)
        order = len(approvals) + 1

        approval = DeploymentApproval(
            deployment_id=deployment_id,
            reviewer_id=reviewer_id,
            decision=decision.upper(),
            reviewer_order=order,
            approval_stage="CORE_PROMOTION",
            comments=comments,
            approval_duration_seconds=int((datetime.now(timezone.utc) - deployment.created_at.replace(tzinfo=timezone.utc)).total_seconds()),
        )

        approval = await self.repo.create_approval(approval)

        # Transition to APPROVED if ready
        if decision.upper() == "APPROVED":
            if await self.evaluate_approvals(deployment_id):
                await self.transition_state(
                    deployment_id,
                    next_state="APPROVED",
                    user_id=reviewer_id,
                    reason="All required approvals gathered. Automatically promoting.",
                )

        return approval

    async def emit_audit_event(
        self,
        deployment: ModelDeployment,
        event_type: str,
        previous_state: Optional[str],
        new_state: str,
        user_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> DeploymentEvent:
        """Emits an event-sourced deployment lifecycle audit log."""
        # Find latest event to compute previous hash (blockchain-style ledger link)
        latest_event = await self.repo.get_latest_event(deployment.id)
        prev_hash = latest_event.current_event_hash if latest_event else "0" * 64
        seq = (latest_event.sequence_number + 1) if latest_event else 1

        # Calculate current event hash
        import hashlib
        h = hashlib.sha256()
        h.update(f"{deployment.id}-{seq}-{new_state}-{prev_hash}".encode())
        curr_hash = h.hexdigest()

        event = DeploymentEvent(
            deployment_id=deployment.id,
            event_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            trace_id=uuid.uuid4(),
            event_type=event_type,
            previous_state=previous_state,
            new_state=new_state,
            performed_by=user_id,
            reason=reason,
            sequence_number=seq,
            previous_event_hash=prev_hash,
            current_event_hash=curr_hash,
        )

        return await self.repo.create_event(event)
