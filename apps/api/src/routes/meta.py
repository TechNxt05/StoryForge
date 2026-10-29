"""Public metadata used to build the UI (content packs, voices, formats)."""

from typing import Any, Dict

from fastapi import APIRouter

from runtime import media, pipeline

router = APIRouter(prefix="/api/v1/meta", tags=["Metadata"])


@router.get("")
async def get_meta() -> Dict[str, Any]:
    return {
        "content_packs": [{"id": k, "label": v["label"], "style": v["style"]} for k, v in pipeline.PACK_STYLES.items()],
        "voices": [{"id": k, "label": v} for k, v in media.VOICES.items()],
        "default_voice": media.DEFAULT_VOICE,
        "aspect_ratios": [
            {"id": "9:16", "label": "9:16 Vertical (Reels, Shorts, TikTok)"},
            {"id": "16:9", "label": "16:9 Landscape (YouTube)"},
            {"id": "1:1", "label": "1:1 Square (Feed)"},
        ],
        "steps": [{"id": k, "label": v} for k, v in pipeline.STEPS],
    }
