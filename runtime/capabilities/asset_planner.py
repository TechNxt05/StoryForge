"""Media Asset Planner Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class AssetPlanArtifact(IArtifact):
    """Artifact containing media generation requirements and provider assignments."""

    def __init__(
        self,
        artifact_id: str,
        title: str,
        image_jobs: List[Dict[str, Any]],
        video_jobs: List[Dict[str, Any]],
        audio_jobs: List[Dict[str, Any]],
        total_assets_required: int,
    ):
        self._id = artifact_id
        self.title = title
        self.image_jobs = image_jobs
        self.video_jobs = video_jobs
        self.audio_jobs = audio_jobs
        self.total_assets_required = total_assets_required

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "asset_plan"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "image_jobs": self.image_jobs,
            "video_jobs": self.video_jobs,
            "audio_jobs": self.audio_jobs,
            "total_assets_required": self.total_assets_required,
        }


class MediaAssetPlannerCapability(ICapability):
    """Capability that decides asset requirements and provider routes for image, video, and audio synthesis."""

    @property
    def name(self) -> str:
        return "asset_planner"

    async def execute(
        self,
        storyboard_data: Dict[str, Any] | None = None,
        script_data: Dict[str, Any] | None = None,
        preferred_image_provider: str = "flux",
        preferred_video_provider: str = "veo",
        preferred_voice_provider: str = "kokoro",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Construct itemized asset generation jobs for a story."""
        title = storyboard_data.get("title", "Story Project") if storyboard_data else "Story Project"
        frames = storyboard_data.get("frames", []) if storyboard_data else []

        artifact_id = f"ast-{uuid.uuid4().hex[:8]}"

        image_jobs: List[Dict[str, Any]] = []
        video_jobs: List[Dict[str, Any]] = []
        audio_jobs: List[Dict[str, Any]] = []

        if not frames:
            frames = [{"frame_id": "frame-s1", "image_prompt": "Default visual prompt", "video_prompt": "Default motion"}]

        # Image and Video Jobs per Frame
        for frame in frames:
            frame_id = frame.get("frame_id", f"frame-{len(image_jobs)+1}")
            image_jobs.append(
                {
                    "job_id": f"img-{frame_id}",
                    "frame_id": frame_id,
                    "provider": preferred_image_provider,
                    "prompt": frame.get("image_prompt", "High quality scene frame"),
                    "status": "queued",
                }
            )
            video_jobs.append(
                {
                    "job_id": f"vid-{frame_id}",
                    "frame_id": frame_id,
                    "provider": preferred_video_provider,
                    "prompt": frame.get("video_prompt", "Fluid scene motion"),
                    "status": "queued",
                }
            )

        # Audio Narration Jobs
        scenes = script_data.get("scenes", []) if script_data else []
        if scenes:
            for scene in scenes:
                sc_num = scene.get("scene_number", 1)
                audio_jobs.append(
                    {
                        "job_id": f"aud-scene-{sc_num}",
                        "scene_number": sc_num,
                        "provider": preferred_voice_provider,
                        "text": scene.get("narration_text", ""),
                        "voice_id": "narrator-male-1",
                        "status": "queued",
                    }
                )
        else:
            audio_jobs.append(
                {
                    "job_id": "aud-full",
                    "scene_number": 1,
                    "provider": preferred_voice_provider,
                    "text": "Full voiceover narration for story project.",
                    "voice_id": "narrator-male-1",
                    "status": "queued",
                }
            )

        total_assets = len(image_jobs) + len(video_jobs) + len(audio_jobs)

        artifact = AssetPlanArtifact(
            artifact_id=artifact_id,
            title=title,
            image_jobs=image_jobs,
            video_jobs=video_jobs,
            audio_jobs=audio_jobs,
            total_assets_required=total_assets,
        )

        return artifact.to_dict()
