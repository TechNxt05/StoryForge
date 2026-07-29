"""Memory runtime module interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IMemoryStore(ABC):
    @abstractmethod
    async def query_vector(self, vector: list[float], top_k: int) -> list[Any]:
        pass
