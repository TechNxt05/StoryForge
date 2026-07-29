"""Provider SDK Unit Tests."""

import pytest
from runtime.sdk import BaseProviderSDK, register_provider, get_registered_community_provider


@register_provider("voice")
class CustomCommunityTTSProvider(BaseProviderSDK):
    @property
    def provider_name(self) -> str:
        return "custom_community_tts"

    @property
    def provider_category(self) -> str:
        return "voice"

    async def invoke(self, prompt: str, **kwargs: dict) -> dict:
        return {
            "status": "success",
            "provider": self.provider_name,
            "prompt": prompt,
            "url": "https://cdn.storyforge.ai/custom_voice.mp3",
        }


@pytest.mark.asyncio
async def test_custom_provider_sdk_registration() -> None:
    provider_cls = get_registered_community_provider("voice", "custom_community_tts")
    assert provider_cls is not None

    instance = provider_cls()
    assert instance.provider_name == "custom_community_tts"
    assert instance.provider_category == "voice"

    res = await instance.invoke("Test custom speech")
    assert res["status"] == "success"
    assert "custom_voice.mp3" in res["url"]
