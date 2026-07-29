"""Event bus runtime interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IEventBus(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: dict[str, Any]) -> None:
        pass
