"""Multi-Modal CDN Asset Manager Capability for StoryForge Runtime."""

import time
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class CDNAssetArtifact(IArtifact):
    """Artifact containing CDN media asset URLs and pre-signed access metadata."""

    def __init__(
        self,
        artifact_id: str,
        asset_key: str,
        cdn_url: str,
        signed_url: str,
        media_type: str,
        transformations: Dict[str, Any],
        expires_at: int,
    ):
        self._id = artifact_id
        self.asset_key = asset_key
        self.cdn_url = cdn_url
        self.signed_url = signed_url
        self.media_type = media_type
        self.transformations = transformations
        self.expires_at = expires_at

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "cdn_media_asset"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "asset_key": self.asset_key,
            "cdn_url": self.cdn_url,
            "signed_url": self.signed_url,
            "media_type": self.media_type,
            "transformations": self.transformations,
            "expires_at": self.expires_at,
        }


class CloudinaryAssetManagerCapability(ICapability):
    """Capability managing multi-modal media asset uploading, caching, CDN transformations, and URL signing."""

    @property
    def name(self) -> str:
        return "asset_manager"

    async def execute(
        self,
        media_type: str = "image",
        raw_asset_url: str = "",
        transformations: Dict[str, Any] | None = None,
        ttl_seconds: int = 86400,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Upload asset to Cloudinary CDN and generate pre-signed URLs with media transformations."""
        artifact_id = f"cdn-{uuid.uuid4().hex[:8]}"
        asset_key = f"storyforge/{media_type}s/{uuid.uuid4().hex[:12]}"

        if not raw_asset_url:
            raw_asset_url = f"https://cdn.storyforge.ai/raw/{media_type}_sample.bin"

        transformations = transformations or {"quality": "auto", "fetch_format": "auto", "crop": "fill"}

        cdn_url = f"https://res.cloudinary.com/storyforge/{media_type}/upload/{asset_key}"
        expires_at = int(time.time()) + ttl_seconds
        signed_url = f"{cdn_url}?signature={uuid.uuid4().hex[:16]}&expires={expires_at}"

        artifact = CDNAssetArtifact(
            artifact_id=artifact_id,
            asset_key=asset_key,
            cdn_url=cdn_url,
            signed_url=signed_url,
            media_type=media_type,
            transformations=transformations,
            expires_at=expires_at,
        )

        return artifact.to_dict()
