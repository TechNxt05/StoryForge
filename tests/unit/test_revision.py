"""Story Revision Capability Unit Tests."""

import pytest
from runtime.capabilities import StoryRevisionCapability, RevisionArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_revision_execution() -> None:
    cap = StoryRevisionCapability()
    review_report = {"title": "Quantum Physics", "passed": False}

    result = await cap.execute(review_report=review_report)

    assert result["title"] == "Quantum Physics"
    assert len(result["scenes_regenerated"]) >= 1
    assert result["revised_overall_score"] > 0.9
    assert result["revision_status"] == "healed_and_verified"
    assert result["artifact_type"] == "revision_report"


@pytest.mark.asyncio
async def test_revision_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("story_revision")
    assert resolved.name == "story_revision"
