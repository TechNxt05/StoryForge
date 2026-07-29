"""Resilience & Multi-Provider Fallback Unit Tests."""

import pytest
from providers.voiceai import VoiceAIAdapter
from providers.pollinations import PollinationsAdapter
from providers.groq import GroqAdapter
from runtime.providers import ProviderFallbackEngine
from runtime.capabilities import VoiceSynthesizerCapability


@pytest.mark.asyncio
async def test_voiceai_adapter() -> None:
    adapter = VoiceAIAdapter()
    res = await adapter.invoke(prompt="Hello world narration", voice_id="en-US-Neural")
    assert res["provider"] == "voiceai"
    assert "api.voiceai.community" in res["url"]


@pytest.mark.asyncio
async def test_pollinations_adapter() -> None:
    adapter = PollinationsAdapter()
    res = await adapter.invoke(prompt="Futuristic city with flying cars", media_type="image")
    assert res["provider"] == "pollinations"
    assert "pollinations.ai" in res["url"]


@pytest.mark.asyncio
async def test_groq_adapter() -> None:
    adapter = GroqAdapter()
    res = await adapter.invoke(prompt="Explain quantum entanglement")
    assert res["provider"] == "groq"
    assert "Groq" in res["response"]


@pytest.mark.asyncio
async def test_provider_fallback_engine_failover() -> None:
    engine = ProviderFallbackEngine()

    class FailingProvider:
        @property
        def provider_name(self) -> str:
            return "failing"

        async def invoke(self, prompt: str, **kwargs) -> None:
            raise RuntimeError("Primary service outage!")

    class BackupProvider:
        @property
        def provider_name(self) -> str:
            return "backup_ok"

        async def invoke(self, prompt: str, **kwargs) -> dict:
            return {"status": "success", "result": "Backup output"}

    engine.register_provider("voice", "failing", FailingProvider())
    engine.register_provider("voice", "backup_ok", BackupProvider())

    res = await engine.execute_with_fallback(
        category="voice", primary_provider="failing", backup_providers=["backup_ok"], prompt="Test text"
    )

    assert res["status"] == "success"
    assert res["active_provider"] == "backup_ok"
    assert res["fallback_used"] is True
