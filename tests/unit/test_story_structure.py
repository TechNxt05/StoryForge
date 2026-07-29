"""Story Structure Capability Unit Tests."""

import pytest
from runtime.capabilities import StoryStructureCapability, StoryOutlineArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_story_structure_execution() -> None:
    cap = StoryStructureCapability()
    result = await cap.execute(topic="The Industrial Revolution", target_duration=60)

    assert result["topic"] == "The Industrial Revolution"
    assert len(result["acts"]) == 5
    assert result["total_duration_seconds"] == 60
    assert result["artifact_type"] == "story_outline"

    act_names = [act["act_name"] for act in result["acts"]]
    assert act_names == ["Hook", "Setup", "Conflict", "Climax", "Resolution"]


@pytest.mark.asyncio
async def test_story_structure_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("story_structure_planner")
    assert resolved.name == "story_structure_planner"

    result = await resolved.execute(topic="Deep Sea Exploration", target_duration=30)
    assert result["total_duration_seconds"] == 30
    assert sum(act["target_duration_seconds"] for act in result["acts"]) == 30
