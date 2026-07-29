"""Visual Storyboard Generator Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class StoryboardArtifact(IArtifact):
    """Artifact containing detailed keyframe visual storyboard frames."""

    def __init__(
        self,
        artifact_id: str,
        title: str,
        frames: List[Dict[str, Any]],
        aspect_ratio: str,
        visual_style: str,
    ):
        self._id = artifact_id
        self.title = title
        self.frames = frames
        self.aspect_ratio = aspect_ratio
        self.visual_style = visual_style

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "storyboard_spec"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "frames": self.frames,
            "aspect_ratio": self.aspect_ratio,
            "visual_style": self.visual_style,
        }


class StoryboardGeneratorCapability(ICapability):
    """Capability that maps script scenes to detailed visual prompts, camera motions, and lighting specifications."""

    @property
    def name(self) -> str:
        return "storyboard_generator"

    async def execute(
        self,
        script_data: Dict[str, Any] | None = None,
        aspect_ratio: str = "9:16",
        visual_style: str = "cinematic_dark",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate keyframe storyboard specifications from script scenes."""
        title = script_data.get("title", "AI Storytelling") if script_data else "AI Storytelling"
        scenes = script_data.get("scenes", []) if script_data else []

        artifact_id = f"stb-{uuid.uuid4().hex[:8]}"

        frames: List[Dict[str, Any]] = []

        if not scenes:
            # Fallback default frames if no script_data provided
            scenes = [
                {
                    "scene_number": 1,
                    "visual_prompt": "Glowing neural network particles shaping a video frame",
                    "camera_direction": "Slow push-in zoom",
                },
                {
                    "scene_number": 2,
                    "visual_prompt": "High-tech editing workspace transitioning into code streams",
                    "camera_direction": "Pan right across timeline",
                },
            ]

        for scene in scenes:
            scene_num = scene.get("scene_number", len(frames) + 1)
            raw_prompt = scene.get("visual_prompt", f"Visual representation of scene {scene_num}")
            cam_dir = scene.get("camera_direction", "Static shot")

            # Enrich image and video prompts for generative AI models
            image_prompt = (
                f"Masterpiece, ultra-detailed 8k resolution, {visual_style} aesthetic: {raw_prompt}. "
                f"Volumetric lighting, photorealistic textures, 35mm film lens, aspect ratio {aspect_ratio}."
            )

            video_prompt = (
                f"Fluid motion video clip: {raw_prompt}. Camera movement: {cam_dir}. "
                f"Smooth 60fps render, cinematic grading."
            )

            frame = {
                "frame_id": f"frame-s{scene_num}",
                "scene_number": scene_num,
                "raw_visual_prompt": raw_prompt,
                "image_prompt": image_prompt,
                "video_prompt": video_prompt,
                "camera_motion": cam_dir,
                "lighting_style": "volumetric_dramatic",
                "color_palette": ["#090d16", "#6366f1", "#10b981"],
                "aspect_ratio": aspect_ratio,
                "status": "pending_generation",
            }
            frames.append(frame)

        artifact = StoryboardArtifact(
            artifact_id=artifact_id,
            title=title,
            frames=frames,
            aspect_ratio=aspect_ratio,
            visual_style=visual_style,
        )

        return artifact.to_dict()
