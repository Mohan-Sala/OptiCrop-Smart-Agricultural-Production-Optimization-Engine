from typing import Dict, Set, Optional
from dataclasses import dataclass
from app.services.deployment.exceptions import IncompatibleProviderError

@dataclass
class ProviderCapabilities:
    provider_name: str
    provider_version: str
    capability_version: str
    supported_strategies: Set[str]
    supports_traffic_shifting: bool
    supports_encrypted_vars: bool
    supports_secrets_resolution: bool


class ProviderRegistry:
    """Registry managing supported deployment providers and validating their compatibility matrices."""

    _providers: Dict[str, ProviderCapabilities] = {}

    @classmethod
    def register_provider(cls, caps: ProviderCapabilities) -> None:
        """Registers a provider and its capabilities."""
        cls._providers[caps.provider_name.upper()] = caps

    @classmethod
    def get_provider(cls, name: str) -> Optional[ProviderCapabilities]:
        """Retrieves registered provider capabilities by name."""
        return cls._providers.get(name.upper())

    @classmethod
    def validate_compatibility(
        cls,
        provider_name: str,
        strategy: str,
        requires_encryption: bool = False,
        requires_secrets: bool = False,
    ) -> ProviderCapabilities:
        """Validates that a provider supports the required features.
        
        Raises IncompatibleProviderError if check fails.
        """
        caps = cls.get_provider(provider_name)
        if not caps:
            raise IncompatibleProviderError(f"Deployment provider '{provider_name}' is not registered.")

        # Strategy compatibility
        strat = strategy.upper()
        if strat not in caps.supported_strategies:
            raise IncompatibleProviderError(
                f"Provider '{provider_name}' does not support deployment strategy '{strategy}'."
            )

        # Encrypted variables compatibility
        if requires_encryption and not caps.supports_encrypted_vars:
            raise IncompatibleProviderError(
                f"Provider '{provider_name}' does not support encrypted variables."
            )

        # Secrets resolution compatibility
        if requires_secrets and not caps.supports_secrets_resolution:
            raise IncompatibleProviderError(
                f"Provider '{provider_name}' does not support secret reference resolution."
            )

        return caps

    @classmethod
    def clear(cls) -> None:
        """Clears registered providers."""
        cls._providers.clear()


# Pre-register default mock providers for standard environments
ProviderRegistry.register_provider(
    ProviderCapabilities(
        provider_name="LOCAL",
        provider_version="1.0.0",
        capability_version="v1.0",
        supported_strategies={"ROLLING"},
        supports_traffic_shifting=False,
        supports_encrypted_vars=True,
        supports_secrets_resolution=False,
    )
)

ProviderRegistry.register_provider(
    ProviderCapabilities(
        provider_name="KUBERNETES",
        provider_version="1.28.0",
        capability_version="v1.1",
        supported_strategies={"ROLLING", "CANARY", "BLUE_GREEN"},
        supports_traffic_shifting=True,
        supports_encrypted_vars=True,
        supports_secrets_resolution=True,
    )
)

ProviderRegistry.register_provider(
    ProviderCapabilities(
        provider_name="SAGEMAKER",
        provider_version="2.140.0",
        capability_version="v1.2",
        supported_strategies={"ROLLING", "CANARY", "BLUE_GREEN", "SHADOW"},
        supports_traffic_shifting=True,
        supports_encrypted_vars=True,
        supports_secrets_resolution=True,
    )
)
