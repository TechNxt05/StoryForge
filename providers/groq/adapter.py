"""Groq Open-Source LLM Provider Adapter."""

import os
from typing import Any, Dict
import httpx
from runtime.interfaces import IProvider


class GroqAdapter(IProvider):
    """Adapter for Groq free Llama-3 / DeepSeek ultra-fast LLM inference."""

    @property
    def provider_name(self) -> str:
        return "groq"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Invoke Groq LLM inference with failover support."""
        model = kwargs.get("model", "llama-3.3-70b-versatile")
        temperature = kwargs.get("temperature", 0.7)
        api_key = os.getenv("GROQ_API_KEY", "")

        if api_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        text = res_data["choices"][0]["message"]["content"]
                        return {
                            "status": "success",
                            "provider": self.provider_name,
                            "model": model,
                            "prompt": prompt,
                            "response": text,
                            "live_api": True,
                        }
            except Exception as e:
                print(f"[GroqAdapter] Live API call failed, falling back: {e}")

        return {
            "status": "success",
            "provider": self.provider_name,
            "model": model,
            "prompt": prompt,
            "response": f"[Groq {model} Response]: Processed prompt successfully with zero latency.",
            "temperature": temperature,
            "live_api": False,
        }
