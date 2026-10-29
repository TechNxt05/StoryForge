"""OpenRouter Provider Adapter (delegates to runtime.llm)."""

from typing import Any, Dict
from runtime import llm
from runtime.interfaces import IProvider


class OpenRouterAdapter(IProvider):
    """OpenRouter LLM adapter. Configure with OPENROUTER_API_KEY."""

    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        result = await llm.complete(
            prompt,
            system=kwargs.get("system", "You are a helpful assistant."),
            temperature=kwargs.get("temperature", 0.7),
            only=["openrouter"],
        )
        return {"status": "success", "provider": result.provider, "model": result.model, "text": result.text}
