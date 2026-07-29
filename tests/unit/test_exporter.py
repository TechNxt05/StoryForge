"""Multi-Platform Exporter Capability Unit Tests."""

import pytest
from runtime.capabilities import MultiPlatformExporterCapability, ExportAssetsArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_exporter_execution() -> None:
    cap = MultiPlatformExporterCapability()
    render_data = {"output_url": "https://cdn.storyforge.ai/exports/final_render.mp4"}

    result = await cap.execute(render_data=render_data, title="Quantum Computing Reel")

    assert result["title"] == "Quantum Computing Reel"
    assert result["total_platforms_exported"] == 4
    assert result["artifact_type"] == "platform_export_package"

    reels = result["platform_exports"]["instagram_reels"]
    assert reels["aspect_ratio"] == "9:16"
    assert reels["resolution"] == "1080x1920"
    assert "Quantum Computing Reel" in reels["caption"]

    landscape = result["platform_exports"]["youtube_landscape"]
    assert landscape["aspect_ratio"] == "16:9"
    assert landscape["resolution"] == "1920x1080"


@pytest.mark.asyncio
async def test_exporter_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("media_exporter")
    assert resolved.name == "media_exporter"
