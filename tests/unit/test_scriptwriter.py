"""Scriptwriter Capability Unit Tests."""

import pytest
from runtime.capabilities import ScriptwriterCapability, ScriptArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_scriptwriter_execution() -> None:
    cap = ScriptwriterCapability()
    result = await cap.execute(title="Quantum Leap in AI")

    assert result["title"] == "Quantum Leap in AI"
    assert len(result["scenes"]) == 4
    assert result["total_word_count"] > 20
    assert result["estimated_total_duration_seconds"] > 0
    assert result["artifact_type"] == "script_text"

    scene_1 = result["scenes"][0]
    assert scene_1["scene_number"] == 1
    assert "Quantum Leap in AI" in scene_1["narration_text"]


@pytest.mark.asyncio
async def test_scriptwriter_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("scriptwriter")
    assert resolved.name == "scriptwriter"

    result = await resolved.execute(title="History of Spaceflight")
    assert result["title"] == "History of Spaceflight"
    assert result["scenes"][0]["word_count"] > 0
