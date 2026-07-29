"""Execution runtime module interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IExecutionEngine(ABC):
    @abstractmethod
    async def execute_step(self, step_id: str, payload: dict[str, Any]) -> Any:
        pass
