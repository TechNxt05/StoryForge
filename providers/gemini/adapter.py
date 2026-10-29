"""Google Gemini Provider Adapter (delegates to runtime.llm)."""

from typing import Any, Dict
from runtime import llm
from runtime.interfaces import IProvider


class GeminiAdapter(IProvider):
    """Google Gemini LLM adapter. Configure with GEMINI_API_KEY."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        result = await llm.complete(
            prompt,
            system=kwargs.get("system", "You are a helpful assistant."),
            temperature=kwargs.get("temperature", 0.7),
            only=["gemini"],
        )
        return {"status": "success", "provider": result.provider, "model": result.model, "text": result.text}
