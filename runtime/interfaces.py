from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class IArtifact(ABC):
    """Abstract interface representing a generated media or text artifact."""

    @property
    @abstractmethod
    def artifact_id(self) -> str:
        pass

    @property
    @abstractmethod
    def artifact_type(self) -> str:
        pass


class ICapability(ABC):
    """Abstract interface representing an agent capability or tool."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        pass


class IWorkflow(ABC):
    """Abstract interface representing an executable storytelling workflow."""

    @property
    @abstractmethod
    def workflow_id(self) -> str:
        pass

    @abstractmethod
    async def run(self, input_data: dict[str, Any]) -> list[IArtifact]:
        pass


class IPlanner(ABC):
    """Abstract interface representing an agent planner/reasoner."""

    @abstractmethod
    async def create_plan(self, goal: str, context: dict[str, Any]) -> Any:
        pass


class IProvider(ABC):
    """Abstract interface representing a third-party AI service provider adapter."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def invoke(self, prompt: str, **kwargs: Any) -> Any:
        pass


class IMemory(ABC, Generic[T]):
    """Abstract interface for agent episodic, semantic, or vector memory storage."""

    @abstractmethod
    async def store(self, key: str, value: T) -> None:
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> T | None:
        pass


class IEventBus(ABC):
    """Abstract interface for async Pub/Sub event broadcasting."""

    @abstractmethod
    async def publish(self, topic: str, message: dict[str, Any]) -> None:
        pass


class IScheduler(ABC):
    """Abstract interface for task scheduling."""

    @abstractmethod
    async def schedule_job(self, job_id: str, cron_or_delay: str) -> None:
        pass
