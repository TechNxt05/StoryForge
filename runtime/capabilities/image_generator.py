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
    """Generates keyframe images with the free provider chain in runtime.media."""

    @property
    def name(self) -> str:
        return "image_generator"

    async def execute(
        self,
        image_jobs: List[Dict[str, Any]] | None = None,
        aspect_ratio: str = "9:16",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate one image per job and publish it (Cloudinary or local /media)."""
        from .. import media

        artifact_id = f"imgart-{uuid.uuid4().hex[:8]}"
        if not image_jobs:
            image_jobs = [{"frame_id": "frame-s1", "prompt": "Cinematic glowing neural network particles"}]

        width, height = media.dimensions(aspect_ratio)
        out_dir = media.MEDIA_DIR / "capabilities" / artifact_id
        rendered_images: List[Dict[str, Any]] = []
        for job in image_jobs:
            frame_id = job.get("frame_id", f"frame-{len(rendered_images) + 1}")
            prompt = job.get("prompt", "Default scene visual prompt")
            seed = random.randint(1, 2_000_000_000)
            image = await media.generate_image(prompt, aspect_ratio, seed, out_dir / f"{frame_id}.jpg")
            published = await media.publish_file(image.path, "image")
            rendered_images.append(
                {
                    "image_id": f"img-{uuid.uuid4().hex[:6]}",
                    "frame_id": frame_id,
                    "provider": image.provider,
                    "prompt": prompt,
                    "url": published["url"],
                    "seed": seed,
                    "aspect_ratio": aspect_ratio,
                    "width": width,
                    "height": height,
                    "status": "completed",
                }
            )

        artifact = ImageAssetsArtifact(
            artifact_id=artifact_id,
            images=rendered_images,
            provider_used=", ".join(sorted({img["provider"] for img in rendered_images})),
            total_images_generated=len(rendered_images),
        )
        return artifact.to_dict()
