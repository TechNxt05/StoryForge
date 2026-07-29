"""Runtime Engine Unit Tests."""

import pytest
from typing import Any, List
from runtime import (
    IArtifact,
    ICapability,
    IWorkflow,
    CapabilityRegistry,
    InMemoryStore,
    StoryForgeRuntimeEngine,
)


class DummyArtifact(IArtifact):
    def __init__(self, artifact_id: str, artifact_type: str):
        self._id = artifact_id
        self._type = artifact_type

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return self._type


class DummyCapability(ICapability):
    @property
    def name(self) -> str:
        return "dummy_capability"

    async def execute(self, text: str = "hello", **kwargs: Any) -> str:
        if text == "error":
            raise ValueError("Intentional execution error")
        return f"Processed: {text}"


class DummyWorkflow(IWorkflow):
    @property
    def workflow_id(self) -> str:
        return "dummy_workflow_01"

    async def run(self, input_data: dict[str, Any]) -> List[IArtifact]:
        return [DummyArtifact(artifact_id="art-1", artifact_type="text_script")]


@pytest.mark.asyncio
async def test_capability_registry() -> None:
    CapabilityRegistry.clear()
    cap = DummyCapability()
    CapabilityRegistry.register_capability(cap.name, cap)

    resolved = CapabilityRegistry.get_capability("dummy_capability")
    assert resolved.name == "dummy_capability"


@pytest.mark.asyncio
async def test_in_memory_store() -> None:
    store = InMemoryStore[str]()
    await store.store("key1", "value1")
    retrieved = await store.retrieve("key1")
    assert retrieved == "value1"

    missing = await store.retrieve("nonexistent")
    assert missing is None


@pytest.mark.asyncio
async def test_runtime_engine_execution() -> None:
    CapabilityRegistry.clear()
    cap = DummyCapability()
    CapabilityRegistry.register_capability(cap.name, cap)

    engine = StoryForgeRuntimeEngine()
    result = await engine.execute_capability("dummy_capability", {"text": "story_input"})

    assert result.success is True
    assert result.output == "Processed: story_input"
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_runtime_engine_error_handling() -> None:
    CapabilityRegistry.clear()
    cap = DummyCapability()
    CapabilityRegistry.register_capability(cap.name, cap)

    engine = StoryForgeRuntimeEngine()
    result = await engine.execute_capability("dummy_capability", {"text": "error"})

    assert result.success is False
    assert result.output is None
    assert "Intentional execution error" in result.error


@pytest.mark.asyncio
async def test_workflow_runner() -> None:
    engine = StoryForgeRuntimeEngine()
    wf = DummyWorkflow()

    artifacts = await engine.run_workflow(wf, {"topic": "cricket"})
    assert len(artifacts) == 1
    assert artifacts[0].artifact_id == "art-1"
    assert artifacts[0].artifact_type == "text_script"
