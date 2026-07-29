"""Gateway runtime module interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IRuntimeGateway(ABC):
    @abstractmethod
    async def route_request(self, request_type: str, data: dict[str, Any]) -> Any:
        pass
