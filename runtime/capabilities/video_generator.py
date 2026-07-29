"""Video Generation Pipeline Capability for StoryForge Runtime."""

import random
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class VideoAssetsArtifact(IArtifact):
    """Artifact containing generated video clip assets."""

    def __init__(
        self,
        artifact_id: str,
        video_clips: List[Dict[str, Any]],
        provider_used: str,
        total_clips_generated: int,
    ):
        self._id = artifact_id
        self.video_clips = video_clips
        self.provider_used = provider_used
        self.total_clips_generated = total_clips_generated

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "video_assets"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "video_clips": self.video_clips,
            "provider_used": self.provider_used,
            "total_clips_generated": self.total_clips_generated,
        }


class VideoGenerationPipelineCapability(ICapability):
    """Capability orchestrating Google Veo provider adapter for video clip synthesis."""

    @property
    def name(self) -> str:
        return "video_generator"

    async def execute(
        self,
        video_jobs: List[Dict[str, Any]] | None = None,
        provider: str = "veo",
        aspect_ratio: str = "9:16",
        fps: int = 60,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute video clip generation jobs."""
        artifact_id = f"vidart-{uuid.uuid4().hex[:8]}"

        if not video_jobs:
            video_jobs = [
                {"job_id": "vid-s1", "frame_id": "frame-s1", "prompt": "Fluid cinematic camera movement over neural network"}
            ]

        rendered_clips: List[Dict[str, Any]] = []

        for job in video_jobs:
            frame_id = job.get("frame_id", "frame-1")
            prompt = job.get("prompt", "Default video motion prompt")
            clip_duration = job.get("duration_seconds", 5.0)
            seed = random.randint(100000, 999999)

            # Simulated Cloudinary / CDN video URL format
            video_url = f"https://cdn.storyforge.ai/videos/{provider}/{frame_id}_{seed}.mp4"

            rendered_clips.append(
                {
                    "video_id": f"vid-{uuid.uuid4().hex[:6]}",
                    "frame_id": frame_id,
                    "provider": provider,
                    "prompt": prompt,
                    "url": video_url,
                    "duration_seconds": clip_duration,
                    "fps": fps,
                    "aspect_ratio": aspect_ratio,
                    "format": "mp4",
                    "status": "completed",
                }
            )

        artifact = VideoAssetsArtifact(
            artifact_id=artifact_id,
            video_clips=rendered_clips,
            provider_used=provider,
            total_clips_generated=len(rendered_clips),
        )

        return artifact.to_dict()
