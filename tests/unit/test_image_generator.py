"""Image Generator Capability Unit Tests."""

import pytest
from runtime.capabilities import ImageGenerationPipelineCapability, ImageAssetsArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_image_generator_execution() -> None:
    cap = ImageGenerationPipelineCapability()
    image_jobs = [
        {"frame_id": "frame-s1", "prompt": "Futuristic rocket launching into deep space"},
        {"frame_id": "frame-s2", "prompt": "Astronaut standing on alien surface"},
    ]

    result = await cap.execute(image_jobs=image_jobs, provider="flux", aspect_ratio="9:16")

    assert result["total_images_generated"] == 2
    assert result["provider_used"] == "flux"
    assert result["artifact_type"] == "image_assets"

    img_1 = result["images"][0]
    assert img_1["frame_id"] == "frame-s1"
    assert "flux" in img_1["url"]
    assert img_1["width"] == 1080
    assert img_1["height"] == 1920


@pytest.mark.asyncio
async def test_image_generator_gemini_provider() -> None:
    cap = ImageGenerationPipelineCapability()
    result = await cap.execute(provider="gemini", aspect_ratio="16:9")

    assert result["provider_used"] == "gemini"
    img = result["images"][0]
    assert "gemini" in img["url"]
    assert img["width"] == 1920
    assert img["height"] == 1080


@pytest.mark.asyncio
async def test_image_generator_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("image_generator")
    assert resolved.name == "image_generator"
