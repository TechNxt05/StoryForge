"""Asset Planner Capability Unit Tests."""

import pytest
from runtime.capabilities import MediaAssetPlannerCapability, AssetPlanArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_asset_planner_execution() -> None:
    cap = MediaAssetPlannerCapability()
    storyboard_data = {
        "title": "Space Exploration",
        "frames": [
            {"frame_id": "frame-s1", "image_prompt": "Rocket launching", "video_prompt": "Smoke billowing"},
            {"frame_id": "frame-s2", "image_prompt": "Astronaut in orbit", "video_prompt": "Earth spinning"},
        ],
    }

    result = await cap.execute(storyboard_data=storyboard_data)

    assert result["title"] == "Space Exploration"
    assert len(result["image_jobs"]) == 2
    assert len(result["video_jobs"]) == 2
    assert result["total_assets_required"] >= 5
    assert result["artifact_type"] == "asset_plan"

    assert result["image_jobs"][0]["provider"] == "flux"
    assert result["video_jobs"][0]["provider"] == "veo"


@pytest.mark.asyncio
async def test_asset_planner_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("asset_planner")
    assert resolved.name == "asset_planner"

    result = await resolved.execute(preferred_image_provider="gemini", preferred_voice_provider="voicebox")
    assert result["image_jobs"][0]["provider"] == "gemini"
    assert result["audio_jobs"][0]["provider"] == "voicebox"
