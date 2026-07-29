"""Multi-Platform Media Exporter Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class ExportAssetsArtifact(IArtifact):
    """Artifact containing platform-formatted export packages."""

    def __init__(
        self,
        artifact_id: str,
        title: str,
        platform_exports: Dict[str, Dict[str, Any]],
        total_platforms_exported: int,
    ):
        self._id = artifact_id
        self.title = title
        self.platform_exports = platform_exports
        self.total_platforms_exported = total_platforms_exported

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "platform_export_package"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "platform_exports": self.platform_exports,
            "total_platforms_exported": self.total_platforms_exported,
        }


class MultiPlatformExporterCapability(ICapability):
    """Capability that packages rendered videos for Instagram Reels, YouTube Shorts, TikTok, and Landscape YouTube."""

    @property
    def name(self) -> str:
        return "media_exporter"

    async def execute(
        self,
        render_data: Dict[str, Any] | None = None,
        platforms: List[str] | None = None,
        title: str = "Story Project",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate platform-specific export packages."""
        if not platforms:
            platforms = ["instagram_reels", "youtube_shorts", "tiktok", "youtube_landscape"]

        artifact_id = f"exp-{uuid.uuid4().hex[:8]}"

        video_url = render_data.get("output_url", "https://cdn.storyforge.ai/exports/render_101.mp4") if render_data else "https://cdn.storyforge.ai/exports/render_101.mp4"

        platform_exports: Dict[str, Dict[str, Any]] = {}

        for platform in platforms:
            is_vertical = platform in ["instagram_reels", "youtube_shorts", "tiktok"]
            aspect_ratio = "9:16" if is_vertical else "16:9"
            resolution = "1080x1920" if is_vertical else "1920x1080"

            hashtags = ["#StoryForge", "#AIStorytelling", "#Shorts", "#Viral"]
            caption = f"✨ {title}\n\nCreated autonomously with StoryForge AI! 🚀\n\n{' '.join(hashtags)}"

            platform_exports[platform] = {
                "platform": platform,
                "video_url": video_url,
                "thumbnail_url": f"https://cdn.storyforge.ai/thumbnails/{platform}_thumb.png",
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "caption": caption,
                "hashtags": hashtags,
                "status": "ready_for_download",
            }

        artifact = ExportAssetsArtifact(
            artifact_id=artifact_id,
            title=title,
            platform_exports=platform_exports,
            total_platforms_exported=len(platform_exports),
        )

        return artifact.to_dict()
