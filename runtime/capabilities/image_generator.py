"""Image Generation Pipeline Capability for StoryForge Runtime."""

import random
import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class ImageAssetsArtifact(IArtifact):
    """Artifact containing generated keyframe image assets."""

    def __init__(
        self,
        artifact_id: str,
        images: List[Dict[str, Any]],
        provider_used: str,
        total_images_generated: int,
    ):
        self._id = artifact_id
        self.images = images
        self.provider_used = provider_used
        self.total_images_generated = total_images_generated

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "image_assets"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "images": self.images,
            "provider_used": self.provider_used,
            "total_images_generated": self.total_images_generated,
        }


class ImageGenerationPipelineCapability(ICapability):
    """Capability orchestrating FLUX and Gemini provider adapters for keyframe image synthesis."""

    @property
    def name(self) -> str:
        return "image_generator"

    async def execute(
        self,
        image_jobs: List[Dict[str, Any]] | None = None,
        provider: str = "flux",
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute keyframe image generation jobs."""
        artifact_id = f"imgart-{uuid.uuid4().hex[:8]}"

        if not image_jobs:
            image_jobs = [
                {"job_id": "img-s1", "frame_id": "frame-s1", "prompt": "Cinematic glowing neural network particles"}
            ]

        rendered_images: List[Dict[str, Any]] = []

        for job in image_jobs:
            frame_id = job.get("frame_id", "frame-1")
            prompt = job.get("prompt", "Default scene visual prompt")
            seed = random.randint(100000, 999999)

            # Simulated Cloudinary / CDN asset URL format
            image_url = f"https://cdn.storyforge.ai/images/{provider}/{frame_id}_{seed}.png"

            rendered_images.append(
                {
                    "image_id": f"img-{uuid.uuid4().hex[:6]}",
                    "frame_id": frame_id,
                    "provider": provider,
                    "prompt": prompt,
                    "url": image_url,
                    "seed": seed,
                    "aspect_ratio": aspect_ratio,
                    "width": 1080 if aspect_ratio == "9:16" else 1920,
                    "height": 1920 if aspect_ratio == "9:16" else 1080,
                    "status": "completed",
                }
            )

        artifact = ImageAssetsArtifact(
            artifact_id=artifact_id,
            images=rendered_images,
            provider_used=provider,
            total_images_generated=len(rendered_images),
        )

        return artifact.to_dict()
