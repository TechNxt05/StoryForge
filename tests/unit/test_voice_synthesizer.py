"""Voice Synthesizer Capability Unit Tests."""

import pytest
from runtime.capabilities import VoiceSynthesizerCapability, VoiceoverArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_voice_synthesizer_execution() -> None:
    cap = VoiceSynthesizerCapability()
    audio_jobs = [
        {"scene_number": 1, "text": "What if a single topic could transform into a cinema-quality documentary in seconds?"},
        {"scene_number": 2, "text": "Intelligent agents orchestrate research, scripting, voice synthesis, and visual rendering."},
    ]

    result = await cap.execute(audio_jobs=audio_jobs, provider="kokoro", voice_id="narrator-male-1")

    assert len(result["audio_clips"]) == 2
    assert result["provider_used"] == "kokoro"
    assert result["artifact_type"] == "voiceover_audio"
    assert result["total_audio_duration_seconds"] > 0

    clip_1 = result["audio_clips"][0]
    assert clip_1["scene_number"] == 1
    assert "kokoro" in clip_1["url"]
    assert clip_1["voice_id"] == "narrator-male-1"


@pytest.mark.asyncio
async def test_voice_synthesizer_voicebox_provider() -> None:
    cap = VoiceSynthesizerCapability()
    result = await cap.execute(provider="voicebox", voice_id="narrator-female-2")

    assert result["provider_used"] == "voicebox"
    clip = result["audio_clips"][0]
    assert "voicebox" in clip["url"]
    assert clip["voice_id"] == "narrator-female-2"


@pytest.mark.asyncio
async def test_voice_synthesizer_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("voice_synthesizer")
    assert resolved.name == "voice_synthesizer"
