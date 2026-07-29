"""Voicebox TTS Provider Adapter."""

import uuid
from typing import Any, Dict
from runtime.interfaces import IProvider


class VoiceboxAdapter(IProvider):
    """Voicebox Speech Synthesis Provider Adapter."""

    @property
    def provider_name(self) -> str:
        return "voicebox"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Invoke Voicebox speech synthesis."""
        audio_id = f"vbox-{uuid.uuid4().hex[:8]}"
        audio_url = f"https://cdn.storyforge.ai/audio/{audio_id}.wav"

        return {
            "status": "success",
            "provider": self.provider_name,
            "prompt": prompt,
            "audio_url": audio_url,
            "duration_seconds": 5.8,
        }
