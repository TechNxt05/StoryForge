"""Timeline Engine Capability Unit Tests."""

import pytest
from runtime.capabilities import TimelineEngineCapability, TimelineArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_timeline_execution() -> None:
    cap = TimelineEngineCapability()
    video_assets = [
        {"video_id": "v1", "url": "https://cdn/v1.mp4", "duration_seconds": 5.0},
        {"video_id": "v2", "url": "https://cdn/v2.mp4", "duration_seconds": 7.0},
    ]
    audio_assets = [
        {"audio_id": "a1", "url": "https://cdn/a1.mp3", "duration_seconds": 12.0},
    ]

    result = await cap.execute(video_assets=video_assets, audio_assets=audio_assets, title="Quantum Project")

    assert result["title"] == "Quantum Project"
    assert len(result["video_track"]) == 2
    assert len(result["audio_track"]) == 1
    assert len(result["music_track"]) == 1
    assert result["total_duration_seconds"] == 12.0
    assert result["is_valid"] is True
    assert result["artifact_type"] == "project_timeline"

    v2 = result["video_track"][1]
    assert v2["start_offset"] == 5.0
    assert v2["end_offset"] == 12.0


@pytest.mark.asyncio
async def test_timeline_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("timeline_engine")
    assert resolved.name == "timeline_engine"
