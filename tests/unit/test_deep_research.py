"""Deep Research Capability Unit Tests."""

import pytest
from runtime.capabilities import DeepResearchCapability, ResearchArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_deep_research_execution() -> None:
    cap = DeepResearchCapability()
    result = await cap.execute(topic="Quantum Computing", content_pack="technology")

    assert result["topic"] == "Quantum Computing"
    assert len(result["facts"]) >= 3
    assert len(result["timeline_events"]) >= 3
    assert result["confidence_score"] == 0.95
    assert result["artifact_type"] == "research_data"


@pytest.mark.asyncio
async def test_deep_research_registry_resolution() -> None:
    # Ensure capability is registered
    resolved = CapabilityRegistry.get_capability("deep_research")
    assert resolved.name == "deep_research"

    result = await resolved.execute(topic="Ancient Rome", content_pack="history")
    assert result["topic"] == "Ancient Rome"
    assert "research_data" in result["artifact_type"]
