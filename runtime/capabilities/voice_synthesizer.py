"""Voice & Audio Synthesis Capability for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IArtifact, ICapability


class VoiceoverArtifact(IArtifact):
    """Artifact containing synthesized voiceover narration audio clips."""

    def __init__(
        self,
        artifact_id: str,
        audio_clips: List[Dict[str, Any]],
        provider_used: str,
        total_audio_duration_seconds: float,
    ):
        self._id = artifact_id
        self.audio_clips = audio_clips
        self.provider_used = provider_used
        self.total_audio_duration_seconds = total_audio_duration_seconds

    @property
    def artifact_id(self) -> str:
        return self._id

    @property
    def artifact_type(self) -> str:
        return "voiceover_audio"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "audio_clips": self.audio_clips,
            "provider_used": self.provider_used,
            "total_audio_duration_seconds": self.total_audio_duration_seconds,
        }


class VoiceSynthesizerCapability(ICapability):
    """Synthesizes narration with the free TTS chain in runtime.media (edge-tts -> gTTS -> silence)."""

    @property
    def name(self) -> str:
        return "voice_synthesizer"

    async def execute(
        self,
        audio_jobs: List[Dict[str, Any]] | None = None,
        voice_id: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Synthesize one audio clip per job and publish it."""
        from .. import media

        artifact_id = f"audart-{uuid.uuid4().hex[:8]}"
        voice_id = voice_id if voice_id in media.VOICES else media.DEFAULT_VOICE
        if not audio_jobs:
            audio_jobs = [{"scene_number": 1, "text": "Welcome to StoryForge AI automated video creation."}]

        out_dir = media.MEDIA_DIR / "capabilities" / artifact_id
        rendered_audio: List[Dict[str, Any]] = []
        for job in audio_jobs:
            scene_num = job.get("scene_number", len(rendered_audio) + 1)
            text = job.get("text") or "Default narration text."
            voice = await media.synthesize_voice(text, voice_id, out_dir / f"scene_{scene_num}.mp3")
            published = await media.publish_file(voice.path, "video")  # Cloudinary files audio under "video"
            rendered_audio.append(
                {
                    "audio_id": f"aud-{uuid.uuid4().hex[:6]}",
                    "scene_number": scene_num,
                    "provider": voice.provider,
                    "voice_id": voice_id,
                    "text": text,
                    "url": published["url"],
                    "duration_seconds": round(voice.duration, 2),
                    "word_timestamps": [w.__dict__ for w in voice.words],
                    "format": "mp3",
                    "status": "completed",
                }
            )

        artifact = VoiceoverArtifact(
            artifact_id=artifact_id,
            audio_clips=rendered_audio,
            provider_used=", ".join(sorted({clip["provider"] for clip in rendered_audio})),
            total_audio_duration_seconds=round(sum(c["duration_seconds"] for c in rendered_audio), 2),
        )
        return artifact.to_dict()
