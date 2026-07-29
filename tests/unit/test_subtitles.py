"""Subtitle Capability Unit Tests."""

import pytest
from runtime.capabilities import SubtitleAlignmentCapability, SubtitleArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_subtitles_execution() -> None:
    cap = SubtitleAlignmentCapability()
    text = "Artificial intelligence transforms short-form video creation."

    result = await cap.execute(script_text=text, audio_duration=6.0, style_preset="bold_yellow_highlight")

    assert len(result["word_timestamps"]) == 6
    assert result["style_preset"] == "bold_yellow_highlight"
    assert result["artifact_type"] == "subtitle_track"

    assert "WEBVTT" in result["vtt_content"]
    assert "-->" in result["srt_content"]
    assert result["word_timestamps"][0]["word"] == "Artificial"


@pytest.mark.asyncio
async def test_subtitles_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("subtitles")
    assert resolved.name == "subtitles"
