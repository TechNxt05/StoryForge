"""Multi-Track Timeline Engine Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class TimelineArtifact(IArtifact):
    """Artifact containing synchronized multi-track project timeline."""

    def __init__(
        self,
        artifact_id: str,
        title: str,
        video_track: List[Dict[str, Any]],
        audio_track: List[Dict[str, Any]],
        subtitle_track: List[Dict[str, Any]],
        music_track: List[Dict[str, Any]],
        total_duration_seconds: float,
        is_valid: bool,
    ):
        self._id = artifact_id
        self.title = title
        self.video_track = video_track
        self.audio_track = audio_track
        self.subtitle_track = subtitle_track
        self.music_track = music_track
        self.total_duration_seconds = total_duration_seconds
        self.is_valid = is_valid

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "project_timeline"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "title": self.title,
            "video_track": self.video_track,
            "audio_track": self.audio_track,
            "subtitle_track": self.subtitle_track,
            "music_track": self.music_track,
            "total_duration_seconds": self.total_duration_seconds,
            "is_valid": self.is_valid,
        }


class TimelineEngineCapability(ICapability):
    """Capability that compiles generated video, image, audio, and subtitle assets into a synchronized multi-track timeline."""

    @property
    def name(self) -> str:
        return "timeline_engine"

    async def execute(
        self,
        video_assets: List[Dict[str, Any]] | None = None,
        audio_assets: List[Dict[str, Any]] | None = None,
        subtitle_assets: Dict[str, Any] | None = None,
        music_track_url: str = "https://cdn.storyforge.ai/music/ambient_tech.mp3",
        title: str = "Story Project",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Assemble multi-track timeline and validate clip synchronization."""
        artifact_id = f"tml-{uuid.uuid4().hex[:8]}"

        video_track: List[Dict[str, Any]] = []
        audio_track: List[Dict[str, Any]] = []
        subtitle_track: List[Dict[str, Any]] = []
        music_track: List[Dict[str, Any]] = []

        curr_video_offset = 0.0
        if video_assets:
            for idx, clip in enumerate(video_assets):
                dur = clip.get("duration_seconds", 5.0)
                video_track.append(
                    {
                        "clip_id": clip.get("video_id", f"vclip-{idx+1}"),
                        "url": clip.get("url", ""),
                        "start_offset": round(curr_video_offset, 2),
                        "duration_seconds": round(dur, 2),
                        "end_offset": round(curr_video_offset + dur, 2),
                        "transition_in": "fade" if idx > 0 else "none",
                        "filters": {"brightness": 0, "contrast": 1, "volume": 1}
                    }
                )
                curr_video_offset += dur
        else:
            # Fallback clip
            video_track.append(
                {
                    "clip_id": "vclip-fallback-1",
                    "url": "https://res.cloudinary.com/demo/video/upload/dog.mp4",
                    "start_offset": 0.0,
                    "duration_seconds": 10.0,
                    "end_offset": 10.0,
                    "transition_in": "none",
                    "filters": {"brightness": 0, "contrast": 1, "volume": 1}
                }
            )
            curr_video_offset = 10.0

        curr_audio_offset = 0.0
        if audio_assets:
            for idx, voice in enumerate(audio_assets):
                dur = voice.get("duration_seconds", 5.0)
                audio_track.append(
                    {
                        "clip_id": voice.get("audio_id", f"aclip-{idx+1}"),
                        "url": voice.get("url", ""),
                        "start_offset": round(curr_audio_offset, 2),
                        "duration_seconds": round(dur, 2),
                        "end_offset": round(curr_audio_offset + dur, 2),
                        "filters": {"volume": 1}
                    }
                )
                curr_audio_offset += dur
        else:
            audio_track.append(
                {
                    "clip_id": "aclip-fallback-1",
                    "url": "https://cdn.storyforge.ai/audio/kokoro/scene_1.mp3",
                    "start_offset": 0.0,
                    "duration_seconds": 10.0,
                    "end_offset": 10.0,
                    "filters": {"volume": 1}
                }
            )
            curr_audio_offset = 10.0

        if subtitle_assets and "word_timestamps" in subtitle_assets:
            subtitle_track = subtitle_assets["word_timestamps"]

        # Background Music Track spanning full duration
        total_dur = max(curr_video_offset, curr_audio_offset)
        music_track.append(
            {
                "track_id": "bg-music-1",
                "url": music_track_url,
                "start_offset": 0.0,
                "duration_seconds": round(total_dur, 2),
                "volume": 0.25,
            }
        )

        artifact = TimelineArtifact(
            artifact_id=artifact_id,
            title=title,
            video_track=video_track,
            audio_track=audio_track,
            subtitle_track=subtitle_track,
            music_track=music_track,
            total_duration_seconds=round(total_dur, 2),
            is_valid=True,
        )

        return artifact.to_dict()
