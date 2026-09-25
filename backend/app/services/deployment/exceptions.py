class DeploymentException(Exception):
    """Base exception for all deployment operations."""
    pass


class InvalidStateTransitionError(DeploymentException):
    """Raised when an invalid state machine transition is attempted."""
    pass


class FreezeWindowActiveError(DeploymentException):
    """Raised when a deployment action is blocked by an active freeze window."""
    pass


class IncompatibleProviderError(DeploymentException):
    """Raised when the target provider does not satisfy required capabilities."""
    pass


class LockAcquisitionError(DeploymentException):
    """Raised when a deployment lease lock cannot be acquired or refreshed."""
    pass


class CheckpointVerificationError(DeploymentException):
    """Raised when a checkpoint payload or hash verification fails."""
    pass


class ReplayTimeoutError(DeploymentException):
    """Raised when event replay exceeds the allowed timeout threshold."""
    pass


class PolicyViolationError(DeploymentException):
    """Raised when a deployment validation policy check fails."""
    pass
