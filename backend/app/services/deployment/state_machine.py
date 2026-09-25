from typing import Dict, Set
from app.services.deployment.exceptions import InvalidStateTransitionError

class DeploymentStateMachine:
    """Centralized state machine governing model deployment lifecycle transitions."""

    # Define valid transitions map
    TRANSITIONS: Dict[str, Set[str]] = {
        "DRAFT": {"PENDING_APPROVAL", "FAILED"},
        "PENDING_APPROVAL": {"APPROVED", "FAILED", "DRAFT"},
        "APPROVED": {"PROMOTING", "FAILED"},
        "PROMOTING": {"TESTING", "PRODUCTION", "FAILED"},
        "TESTING": {"PRODUCTION", "FAILED", "ROLLED_BACK"},
        "PRODUCTION": {"ROLLED_BACK", "FAILED"},
        "FAILED": {"DRAFT", "PENDING_APPROVAL"},
        "ROLLED_BACK": {"DRAFT", "PENDING_APPROVAL"},
    }

    @classmethod
    def validate_transition(cls, from_state: str, to_state: str) -> None:
        """Validates that a state transition is allowed."""
        f_state = from_state.upper()
        t_state = to_state.upper()

        if f_state not in cls.TRANSITIONS:
            raise InvalidStateTransitionError(f"Unknown source state: {from_state}")

        if t_state not in cls.TRANSITIONS[f_state]:
            raise InvalidStateTransitionError(
                f"Invalid state transition from '{from_state}' to '{to_state}'"
            )
