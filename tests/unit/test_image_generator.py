"""Image Generator Capability Unit Tests."""

import pytest
from runtime.capabilities import ImageGenerationPipelineCapability
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_image_generator_execution(offline_media) -> None:
    cap = ImageGenerationPipelineCapability()
    image_jobs = [
        {"frame_id": "frame-s1", "prompt": "Futuristic rocket launching into deep space"},
        {"frame_id": "frame-s2", "prompt": "Astronaut standing on alien surface"},
    ]
    result = await cap.execute(image_jobs=image_jobs, aspect_ratio="9:16")

    assert result["total_images_generated"] == 2
    assert result["artifact_type"] == "image_assets"
    assert result["provider_used"] == "local_title_card"
    img_1 = result["images"][0]
    assert img_1["frame_id"] == "frame-s1"
    assert img_1["url"].startswith("/media/capabilities/")
    assert (img_1["width"], img_1["height"]) == offline_media.dimensions("9:16")


@pytest.mark.asyncio
async def test_image_generator_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("image_generator")
    assert resolved.name == "image_generator"
