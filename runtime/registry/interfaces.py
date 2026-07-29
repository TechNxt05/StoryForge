"""Capability & Agent Registry interface skeleton."""
from abc import ABC, abstractmethod
from typing import Any


class ICapabilityRegistry(ABC):
    @abstractmethod
    def register(self, capability_name: str, capability_cls: Any) -> None:
        pass
