"""Pollinations.ai Free Open-Source Image & Video Provider Adapter."""

import urllib.parse
from typing import Any, Dict
from runtime.interfaces import IProvider


class PollinationsAdapter(IProvider):
    """Adapter for Pollinations.ai free open-source image and video synthesis API."""

    @property
    def provider_name(self) -> str:
        return "pollinations"

    async def invoke(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate open-source image or video using Pollinations API."""
        media_type = kwargs.get("media_type", "image")
        width = kwargs.get("width", 1080)
        height = kwargs.get("height", 1920)
        seed = kwargs.get("seed", 42)

        encoded_prompt = urllib.parse.quote(prompt)

        if media_type == "video":
            url = f"https://pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=video"
        else:
            url = f"https://pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&seed={seed}&model=flux"

        return {
            "status": "success",
            "provider": self.provider_name,
            "media_type": media_type,
            "prompt": prompt,
            "url": url,
            "seed": seed,
            "width": width,
            "height": height,
        }
