"""Generic Memory Store Implementation for StoryForge Runtime."""

from typing import Dict, Optional, TypeVar
from ..interfaces import IMemory

T = TypeVar("T")


class InMemoryStore(IMemory[T]):
    """In-memory implementation of IMemory interface for testing and transient caching."""

    def __init__(self) -> None:
        self._store: Dict[str, T] = {}

    async def store(self, key: str, value: T) -> None:
        """Store a key-value pair in memory."""
        self._store[key] = value

    async def retrieve(self, key: str) -> Optional[T]:
        """Retrieve a value by key from memory."""
        return self._store.get(key)

    async def clear(self) -> None:
        """Clear all stored key-value pairs."""
        self._store.clear()
