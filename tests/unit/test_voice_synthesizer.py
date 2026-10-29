"""Voice Synthesizer Capability Unit Tests."""

import pytest
from runtime.capabilities import VoiceSynthesizerCapability
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_voice_synthesizer_execution(offline_media) -> None:
    cap = VoiceSynthesizerCapability()
    audio_jobs = [
        {"scene_number": 1, "text": "What if a single topic could become a documentary in seconds?"},
        {"scene_number": 2, "text": "Intelligent agents orchestrate research, scripting and rendering."},
    ]
    result = await cap.execute(audio_jobs=audio_jobs, voice_id="en-GB-SoniaNeural")

    assert len(result["audio_clips"]) == 2
    assert result["artifact_type"] == "voiceover_audio"
    assert result["provider_used"] == "silent"
    assert result["total_audio_duration_seconds"] > 0
    clip_1 = result["audio_clips"][0]
    assert clip_1["scene_number"] == 1
    assert clip_1["url"].startswith("/media/capabilities/")
    assert clip_1["voice_id"] == "en-GB-SoniaNeural"
    assert clip_1["word_timestamps"][0]["word"] == "What"


@pytest.mark.asyncio
async def test_voice_synthesizer_unknown_voice_falls_back(offline_media) -> None:
    result = await VoiceSynthesizerCapability().execute(voice_id="narrator-female-2")
    assert result["audio_clips"][0]["voice_id"] == offline_media.DEFAULT_VOICE


@pytest.mark.asyncio
async def test_voice_synthesizer_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("voice_synthesizer")
    assert resolved.name == "voice_synthesizer"
