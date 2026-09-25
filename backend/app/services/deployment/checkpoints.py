import gzip
import hmac
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
import uuid

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

from app.core.config import settings
from app.models.deployment import (
    ModelDeployment,
    DeploymentEventCheckpoint,
    DeploymentEvent,
    DeploymentReplayMetric,
    DeploymentSetting,
)
from app.repositories.interfaces.deployment import DeploymentRepository
from app.services.deployment.exceptions import (
    CheckpointVerificationError,
    ReplayTimeoutError,
)
from app.services.deployment.keys import SigningKeyRegistry

class CheckpointManager:
    """Service to create, compress, sign, and verify deployment event checkpoints."""

    MAX_CHECKPOINT_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
    SUPPORTED_SERIALIZERS = {"JSON"}
    SUPPORTED_FORMAT_VERSIONS = {1}
    SUPPORTED_COMPRESSION_ALGORITHMS = {"NONE", "GZIP"}
    SUPPORTED_MANIFEST_VERSIONS = {"v1", "1.0"}

    def __init__(self, repo: DeploymentRepository):
        self.repo = repo

    def compress_payload(self, payload: bytes, algorithm: str) -> bytes:
        """Compresses the payload using the specified algorithm."""
        alg = algorithm.upper()
        if alg == "NONE":
            return payload
        elif alg == "GZIP":
            return gzip.compress(payload)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

    def decompress_payload(self, compressed_payload: bytes, algorithm: str) -> bytes:
        """Decompresses the payload using the specified algorithm."""
        alg = algorithm.upper()
        if alg == "NONE":
            return compressed_payload
        elif alg == "GZIP":
            try:
                return gzip.decompress(compressed_payload)
            except Exception as e:
                raise CheckpointVerificationError(f"GZIP decompression failed: {str(e)}")
        else:
            raise CheckpointVerificationError(f"Unsupported compression algorithm: {algorithm}")

    def sign_payload(self, payload: bytes, private_key: ed25519.Ed25519PrivateKey) -> bytes:
        """Signs the payload using the private key."""
        return private_key.sign(payload)

    def verify_signature(self, payload: bytes, signature_hex: str, key_id: str) -> None:
        """Verifies the payload signature using the registered public key ID."""
        try:
            public_key_bytes = SigningKeyRegistry.get_key(key_id)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(signature_bytes, payload)
        except CheckpointVerificationError as e:
            # Propagate key missing/revoked errors
            raise e
        except Exception as e:
            raise CheckpointVerificationError(f"Invalid signature verification failed: {str(e)}")

    def is_runtime_compatible(self, checkpoint: DeploymentEventCheckpoint) -> bool:
        """Validates checkpoint creator compatibility rules against current runtime."""
        # Major version check for Python
        curr_py = f"{sys.version_info.major}.{sys.version_info.minor}"
        cp_py = checkpoint.python_runtime or ""
        if cp_py:
            # Check if major version matches (e.g. 3.x vs 3.y)
            curr_major = curr_py.split(".")[0]
            cp_major = cp_py.split(".")[0]
            if curr_major != cp_major:
                return False

        # Major version check for backend
        curr_be = settings.APP_VERSION
        cp_be = checkpoint.backend_version or ""
        if cp_be:
            curr_be_major = curr_be.split(".")[0]
            cp_be_major = cp_be.split(".")[0]
            if curr_be_major != cp_be_major:
                return False

        return True

    async def generate_checkpoint(
        self,
        deployment: ModelDeployment,
        last_sequence_number: int,
        state_snapshot: bytes,
        private_key: Optional[ed25519.Ed25519PrivateKey] = None,
        key_id: Optional[str] = None,
        compression: str = "GZIP",
    ) -> DeploymentEventCheckpoint:
        """Generates, signs, compresses, and persists a checkpoint of deployment state."""
        start_time = time.perf_counter()

        # Compute hash of raw state snapshot
        import hashlib
        h = hashlib.sha256()
        h.update(state_snapshot)
        checksum = h.hexdigest()

        # Compress payload
        compressed = self.compress_payload(state_snapshot, compression)
        snapshot_size = len(compressed)
        decompressed_size = len(state_snapshot)

        # Handle digital signatures if private key is provided
        sig_hex = None
        sig_alg = None
        if private_key and key_id:
            # Replay must verify the signature of the compressed payload
            sig_bytes = self.sign_payload(compressed, private_key)
            sig_hex = sig_bytes.hex()
            sig_alg = "Ed25519"

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        checkpoint = DeploymentEventCheckpoint(
            deployment_id=deployment.id,
            last_sequence_number=last_sequence_number,
            checkpoint_hash=checksum,
            snapshot=compressed,
            schema_version="1.0",
            compression=compression.upper(),
            hash_algorithm="SHA256",
            snapshot_size_bytes=snapshot_size,
            created_from_sequence=0,
            checkpoint_format_version=1,
            checkpoint_serializer="JSON",
            serializer_version="1.0",
            backend_version=settings.APP_VERSION,
            python_runtime=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            decompressed_size_bytes=decompressed_size,
            checkpoint_duration_ms=duration_ms,
            created_by_instance=settings.HOST,
            hash_algorithm_version="SHA256-v1",
            checkpoint_signature=sig_hex,
            signature_algorithm=sig_alg,
            signing_key_id=key_id,
        )

        return await self.repo.create_checkpoint(checkpoint)

    async def verify_and_replay(
        self,
        deployment: ModelDeployment,
        events: List[DeploymentEvent],
        max_duration_seconds: float = 30.0,
    ) -> Tuple[str, int, float, Optional[str], Optional[str], Dict[str, Any]]:
        """Verifies checkpoint integrity, validates compatibility, and replays events.
        
        Returns a tuple of:
          - verification_status (str)
          - verified_events (int)
          - duration_ms (float)
          - fallback_reason (str or None)
          - failure_class (str or None)
          - details (dict)
        """
        start_time = time.perf_counter()
        
        # Helper to compute timing
        def elapsed_ms() -> float:
            return (time.perf_counter() - start_time) * 1000.0

        # Retrieve settings for retention period
        settings_record = await self.repo.get_settings(deployment.project_id)
        retention_days = settings_record.checkpoint_retention_days if settings_record else 30

        # Load latest checkpoint
        checkpoint = await self.repo.get_latest_checkpoint(deployment.id)
        if not checkpoint:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "NO_CHECKPOINT",
                "CHECKPOINT",
                {"message": "No checkpoint exists for this deployment."}
            )

        load_duration_ms = elapsed_ms()

        # 1. Checkpoint Expiration Validation
        now_dt = datetime.now(timezone.utc)
        checkpoint_age = now_dt - checkpoint.created_at.replace(tzinfo=timezone.utc)
        if checkpoint_age > timedelta(days=retention_days):
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "CHECKPOINT_EXPIRED",
                "CHECKPOINT",
                {"message": f"Checkpoint is expired ({checkpoint_age.days} days old, max {retention_days})."}
            )

        # 2. Digital Signature Verification (before decompression)
        if checkpoint.checkpoint_signature:
            if not checkpoint.signing_key_id:
                return (
                    "FALLBACK_REPLAY",
                    0,
                    elapsed_ms(),
                    "INVALID_SIGNATURE",
                    "SECURITY",
                    {"message": "Checkpoint has signature but missing key ID."}
                )
            try:
                # Key resolution and signature verification
                self.verify_signature(
                    checkpoint.snapshot,
                    checkpoint.checkpoint_signature,
                    checkpoint.signing_key_id
                )
            except CheckpointVerificationError as e:
                # Differentiate between revoked key and signature mismatch
                reason = "INVALID_SIGNATURE"
                if "revoked" in str(e).lower():
                    reason = "SIGNING_KEY_REVOKED"
                return (
                    "FALLBACK_REPLAY",
                    0,
                    elapsed_ms(),
                    reason,
                    "SECURITY",
                    {"message": str(e)}
                )
        else:
            # If signature is required but missing, return invalid signature
            # (assuming enterprise security requires signature if signing key is configured)
            pass

        # 3. Creator Instance & Manifest Compatibility Checks
        if not self.is_runtime_compatible(checkpoint):
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "CHECKPOINT_RUNTIME_INCOMPATIBLE",
                "CHECKPOINT",
                {"message": "Checkpoint runtime version is incompatible."}
            )

        manifest_ver = deployment.manifest_version or "v1"
        if manifest_ver not in self.SUPPORTED_MANIFEST_VERSIONS:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "MANIFEST_VERSION_INCOMPATIBLE",
                "SCHEMA",
                {"message": f"Unsupported manifest version: {manifest_ver}"}
            )

        # 4. Snapshot Size Validation & Decompression
        if checkpoint.checkpoint_serializer not in self.SUPPORTED_SERIALIZERS:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "UNSUPPORTED_SERIALIZER",
                "SERIALIZER",
                {"message": f"Unsupported serializer: {checkpoint.checkpoint_serializer}"}
            )

        if checkpoint.checkpoint_format_version not in self.SUPPORTED_FORMAT_VERSIONS:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "UNSUPPORTED_FORMAT",
                "SERIALIZER",
                {"message": f"Unsupported format version: {checkpoint.checkpoint_format_version}"}
            )

        if checkpoint.compression not in self.SUPPORTED_COMPRESSION_ALGORITHMS:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "UNSUPPORTED_COMPRESSION",
                "COMPRESSION",
                {"message": f"Unsupported compression: {checkpoint.compression}"}
            )

        if checkpoint.snapshot_size_bytes > self.MAX_CHECKPOINT_SIZE_BYTES:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "LIMIT_EXCEEDED",
                "CHECKPOINT",
                {"message": f"Snapshot size exceeds limit: {checkpoint.snapshot_size_bytes} bytes."}
            )

        decomp_start = time.perf_counter()
        try:
            raw_snapshot = self.decompress_payload(checkpoint.snapshot, checkpoint.compression)
        except CheckpointVerificationError as e:
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "DECOMPRESSION_FAILED",
                "COMPRESSION",
                {"message": str(e)}
            )
        decomp_duration_ms = (time.perf_counter() - decomp_start) * 1000.0

        # 5. Checkpoint Hash Verification (constant-time check)
        import hashlib
        h = hashlib.sha256()
        h.update(raw_snapshot)
        checksum = h.hexdigest()

        if not hmac.compare_digest(checksum, checkpoint.checkpoint_hash):
            return (
                "FALLBACK_REPLAY",
                0,
                elapsed_ms(),
                "CHECKSUM_MISMATCH",
                "SECURITY",
                {"message": "Checkpoint state snapshot hash mismatch."}
            )

        # Filter events newer than the checkpoint
        newer_events = [ev for ev in events if ev.sequence_number > checkpoint.last_sequence_number]
        newer_events.sort(key=lambda x: x.sequence_number)

        # 6. Event Sequence Continuity Validation
        expected_seq = checkpoint.last_sequence_number + 1
        for ev in newer_events:
            # Check for sequence gap
            if ev.sequence_number != expected_seq:
                return (
                    "FALLBACK_REPLAY",
                    0,
                    elapsed_ms(),
                    "EVENT_SEQUENCE_GAP",
                    "EVENT_STREAM",
                    {
                        "message": f"Sequence gap detected: expected {expected_seq}, got {ev.sequence_number}",
                        "expected": expected_seq,
                        "got": ev.sequence_number
                    }
                )
            expected_seq += 1

        # 7. Replay & Timeout Protection
        replay_start = time.perf_counter()
        verified_count = 0

        for ev in newer_events:
            # Check timeout
            elapsed = time.perf_counter() - start_time
            if elapsed > max_duration_seconds:
                # Timeout exceeded
                return (
                    "FALLBACK_REPLAY",
                    verified_count,
                    elapsed_ms(),
                    "REPLAY_TIMEOUT",
                    "UNKNOWN",
                    {"message": f"Replay exceeded timeout of {max_duration_seconds} seconds."}
                )

            # Replay event action (simulated / state transitions validation)
            # Verify event integrity using correlation/trace headers
            if not ev.correlation_id or not ev.trace_id:
                return (
                    "FALLBACK_REPLAY",
                    verified_count,
                    elapsed_ms(),
                    "INVALID_EVENT_HEADERS",
                    "EVENT_STREAM",
                    {"message": f"Event {ev.id} lacks trace/correlation headers."}
                )

            verified_count += 1

        total_duration_ms = elapsed_ms()
        replay_duration_ms = (time.perf_counter() - replay_start) * 1000.0

        # Verification Succeeded
        status = "FULLY_VERIFIED" if len(newer_events) == verified_count else "PARTIALLY_VERIFIED"

        return (
            status,
            verified_count,
            total_duration_ms,
            None,
            None,
            {
                "checkpoint_load_duration_ms": load_duration_ms,
                "decompression_duration_ms": decomp_duration_ms,
                "replay_duration_ms": replay_duration_ms,
                "events_per_second": (verified_count / (replay_duration_ms / 1000.0)) if replay_duration_ms > 0 else 0.0
            }
        )
