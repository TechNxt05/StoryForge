"""SDK interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IStoryForgeSDK(ABC):
    @abstractmethod
    async def create_story(self, topic: str) -> Any:
        pass
