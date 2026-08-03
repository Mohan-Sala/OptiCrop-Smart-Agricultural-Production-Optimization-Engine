from typing import Dict, Tuple
from app.services.deployment.exceptions import CheckpointVerificationError

class SigningKeyRegistry:
    """Registry managing Ed25519 verification keys (public keys) and their revocation states."""

    _registry: Dict[str, Tuple[bytes, bool]] = {}

    @classmethod
    def register_key(cls, key_id: str, public_key_bytes: bytes, is_active: bool = True) -> None:
        """Registers a public verification key in the registry."""
        cls._registry[key_id] = (public_key_bytes, is_active)

    @classmethod
    def revoke_key(cls, key_id: str) -> None:
        """Revokes a key by setting its active state to False."""
        if key_id in cls._registry:
            public_key_bytes, _ = cls._registry[key_id]
            cls._registry[key_id] = (public_key_bytes, False)

    @classmethod
    def get_key(cls, key_id: str) -> bytes:
        """Retrieves the public key bytes if the key exists and is not revoked.
        
        Raises CheckpointVerificationError if the key is revoked or missing.
        """
        if key_id not in cls._registry:
            raise CheckpointVerificationError(f"Signing key '{key_id}' not found in registry.")

        public_key_bytes, is_active = cls._registry[key_id]
        if not is_active:
            raise CheckpointVerificationError(f"Signing key '{key_id}' has been revoked.")

        return public_key_bytes

    @classmethod
    def clear(cls) -> None:
        """Clears all keys from the registry (primarily for testing)."""
        cls._registry.clear()
