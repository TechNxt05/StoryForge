"""Asset Manager Capability Unit Tests."""

import pytest
from runtime.capabilities import CloudinaryAssetManagerCapability, CDNAssetArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_asset_manager_execution() -> None:
    cap = CloudinaryAssetManagerCapability()
    result = await cap.execute(media_type="video", raw_asset_url="https://source/video.mp4")

    assert result["media_type"] == "video"
    assert "res.cloudinary.com" in result["cdn_url"]
    assert "signature=" in result["signed_url"]
    assert result["artifact_type"] == "cdn_media_asset"
    assert result["expires_at"] > 0


@pytest.mark.asyncio
async def test_asset_manager_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("asset_manager")
    assert resolved.name == "asset_manager"
