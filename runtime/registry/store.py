"""Dynamic Capability and Provider Registry for StoryForge Runtime."""

from typing import Dict
from ..interfaces import ICapability, IProvider


class CapabilityRegistry:
    """Registry for managing and resolving runtime capabilities and provider adapters."""

    _capabilities: Dict[str, ICapability] = {}
    _providers: Dict[str, IProvider] = {}

    @classmethod
    def register_capability(cls, name: str, capability: ICapability) -> None:
        """Register a runtime capability instance."""
        cls._capabilities[name] = capability

    @classmethod
    def get_capability(cls, name: str) -> ICapability:
        """Retrieve a registered capability by name."""
        if name not in cls._capabilities:
            raise KeyError(f"Capability '{name}' is not registered in runtime registry.")
        return cls._capabilities[name]

    @classmethod
    def list_capabilities(cls) -> Dict[str, ICapability]:
        """List all registered capabilities."""
        return cls._capabilities

    @classmethod
    def register_provider(cls, name: str, provider: IProvider) -> None:
        """Register a provider adapter instance."""
        cls._providers[name] = provider

    @classmethod
    def get_provider(cls, name: str) -> IProvider:
        """Retrieve a registered provider adapter by name."""
        if name not in cls._providers:
            raise KeyError(f"Provider '{name}' is not registered in runtime registry.")
        return cls._providers[name]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered capabilities and providers."""
        cls._capabilities.clear()
        cls._providers.clear()
