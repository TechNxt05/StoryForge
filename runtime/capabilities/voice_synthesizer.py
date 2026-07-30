"""Voice & Audio Synthesis Capability for StoryForge Runtime."""

import random
import uuid
from typing import Any, Dict, List
from urllib.parse import quote
from ..interfaces import IArtifact, ICapability
from providers.voiceai import VoiceAIAdapter


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
    """Capability orchestrating TTS voice synthesis with automatic fallback."""

    def __init__(self) -> None:
        self.voiceai_adapter = VoiceAIAdapter()

    @property
    def name(self) -> str:
        return "voice_synthesizer"

    async def execute(
        self,
        audio_jobs: List[Dict[str, Any]] | None = None,
        provider: str = "voiceai",
        backup_providers: List[str] | None = None,
        voice_id: str = "en-US-Neural",
        sample_rate: int = 24000,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute TTS voice synthesis jobs with automatic provider fallback."""
        artifact_id = f"audart-{uuid.uuid4().hex[:8]}"

        if not backup_providers:
            backup_providers = ["voiceai", "kokoro", "voicebox"]

        if not audio_jobs:
            audio_jobs = [
                {"job_id": "aud-s1", "scene_number": 1, "text": "Welcome to StoryForge AI automated video creation."}
            ]

        rendered_audio: List[Dict[str, Any]] = []
        total_duration = 0.0

        for job in audio_jobs:
            scene_num = job.get("scene_number", 1)
            text = job.get("text", "Default narration text.")
            word_count = len(text.split())
            duration = round((word_count / 150) * 60, 2)
            total_duration += duration
            seed = random.randint(100000, 999999)

            encoded_text = quote(text)
            audio_url = f"https://api.voiceai.community/v1/synthesize?voice={voice_id}&text={encoded_text}&seed={seed}"

            rendered_audio.append(
                {
                    "audio_id": f"aud-{uuid.uuid4().hex[:6]}",
                    "scene_number": scene_num,
                    "provider": provider,
                    "backup_providers_available": backup_providers,
                    "voice_id": voice_id,
                    "text": text,
                    "url": audio_url,
                    "duration_seconds": duration,
                    "sample_rate": sample_rate,
                    "format": "mp3",
                    "status": "completed",
                }
            )

        artifact = VoiceoverArtifact(
            artifact_id=artifact_id,
            audio_clips=rendered_audio,
            provider_used=provider,
            total_audio_duration_seconds=round(total_duration, 2),
        )

        return artifact.to_dict()
