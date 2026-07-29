"""Video Generator Capability Unit Tests."""

import pytest
from runtime.capabilities import VideoGenerationPipelineCapability, VideoAssetsArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_video_generator_execution() -> None:
    cap = VideoGenerationPipelineCapability()
    video_jobs = [
        {"frame_id": "frame-s1", "prompt": "Rocket launching into sky", "duration_seconds": 6.0},
        {"frame_id": "frame-s2", "prompt": "Earth spinning in space", "duration_seconds": 4.0},
    ]

    result = await cap.execute(video_jobs=video_jobs, provider="veo", aspect_ratio="9:16", fps=60)

    assert result["total_clips_generated"] == 2
    assert result["provider_used"] == "veo"
    assert result["artifact_type"] == "video_assets"

    clip_1 = result["video_clips"][0]
    assert clip_1["frame_id"] == "frame-s1"
    assert "veo" in clip_1["url"]
    assert clip_1["format"] == "mp4"
    assert clip_1["fps"] == 60


@pytest.mark.asyncio
async def test_video_generator_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("video_generator")
    assert resolved.name == "video_generator"

    result = await resolved.execute(aspect_ratio="16:9")
    assert result["video_clips"][0]["aspect_ratio"] == "16:9"
