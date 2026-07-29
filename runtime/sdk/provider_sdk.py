"""Provider SDK & Plug-and-Play Decorator System for StoryForge Runtime."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type
from ..interfaces import IProvider

_COMMUNITY_PROVIDERS_REGISTRY: Dict[str, Dict[str, Type[IProvider]]] = {
    "llm": {},
    "image": {},
    "video": {},
    "voice": {},
}


class BaseProviderSDK(IProvider, ABC):
    """Abstract base class for custom third-party provider adapters."""

    @property
    @abstractmethod
    def provider_category(self) -> str:
        """Return provider category: 'llm', 'image', 'video', or 'voice'."""
        pass

    @abstractmethod
    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Invoke custom provider API."""
        pass


def register_provider(category: str) -> Callable[[Type[IProvider]], Type[IProvider]]:
    """Decorator for plug-and-play third-party provider registration."""

    def decorator(cls: Type[IProvider]) -> Type[IProvider]:
        instance = cls()
        provider_name = getattr(instance, "provider_name", cls.__name__.lower())

        if category not in _COMMUNITY_PROVIDERS_REGISTRY:
            _COMMUNITY_PROVIDERS_REGISTRY[category] = {}

        _COMMUNITY_PROVIDERS_REGISTRY[category][provider_name] = cls
        return cls

    return decorator


def get_registered_community_provider(category: str, name: str) -> Optional[Type[IProvider]]:
    """Retrieve registered third-party community provider class."""
    return _COMMUNITY_PROVIDERS_REGISTRY.get(category, {}).get(name)
