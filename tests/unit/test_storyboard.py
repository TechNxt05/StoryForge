"""Storyboard Generator Capability Unit Tests."""

import pytest
from runtime.capabilities import StoryboardGeneratorCapability, StoryboardArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_storyboard_execution() -> None:
    cap = StoryboardGeneratorCapability()
    script_data = {
        "title": "Quantum Physics Revolution",
        "scenes": [
            {
                "scene_number": 1,
                "visual_prompt": "Futuristic quantum processor glowing in dark laboratory",
                "camera_direction": "Zoom in shot",
            }
        ],
    }

    result = await cap.execute(script_data=script_data, aspect_ratio="9:16")

    assert result["title"] == "Quantum Physics Revolution"
    assert len(result["frames"]) == 1
    assert result["aspect_ratio"] == "9:16"
    assert result["artifact_type"] == "storyboard_spec"

    frame_1 = result["frames"][0]
    assert frame_1["frame_id"] == "frame-s1"
    assert "quantum processor" in frame_1["image_prompt"]
    assert "Zoom in shot" in frame_1["video_prompt"]


@pytest.mark.asyncio
async def test_storyboard_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("storyboard_generator")
    assert resolved.name == "storyboard_generator"

    result = await resolved.execute(aspect_ratio="16:9")
    assert result["aspect_ratio"] == "16:9"
    assert len(result["frames"]) >= 2
