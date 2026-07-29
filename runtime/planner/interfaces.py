"""Planner runtime module interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class IPlannerEngine(ABC):
    @abstractmethod
    async def generate_plan_steps(self, objective: str) -> list[Any]:
        pass
