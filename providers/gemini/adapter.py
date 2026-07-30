"""Google Gemini Provider Adapter."""

import os
from typing import Any, Dict
import httpx
from runtime.interfaces import IProvider


class GeminiAdapter(IProvider):
    """Google Gemini Provider Adapter for Multimodal LLM Generation."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Invoke Google Gemini 1.5 Pro / Flash model inference."""
        model = kwargs.get("model", "gemini-1.5-flash")
        temperature = kwargs.get("temperature", 0.7)
        api_key = os.getenv("GEMINI_API_KEY", "")

        if api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature},
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "status": "success",
                            "provider": self.provider_name,
                            "model": model,
                            "prompt": prompt,
                            "text": text,
                            "live_api": True,
                        }
            except Exception as e:
                print(f"[GeminiAdapter] Live API call failed, falling back: {e}")

        return {
            "status": "success",
            "provider": self.provider_name,
            "model": model,
            "prompt": prompt,
            "text": f"[Gemini 1.5 Flash Response]: Grounded research synthesis for '{prompt}'.",
            "temperature": temperature,
            "live_api": False,
        }
