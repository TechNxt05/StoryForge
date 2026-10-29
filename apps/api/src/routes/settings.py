"""Platform settings: provider status, admin key management, workspace usage."""

import os
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from runtime import llm, media
from ..auth import get_current_user, require_admin
from ..database.postgres import Project as DBProject, Workspace as DBWorkspace, get_postgres_session

router = APIRouter(prefix="/api/v1/settings", tags=["Settings & Workspace"])

# Every provider the pipeline can use. All are free (or have a free tier).
PROVIDERS: List[Dict[str, Any]] = [
    {"id": "gemini", "category": "Script (LLM)", "name": "Google Gemini", "env": ["GEMINI_API_KEY"],
     "free": "Free tier via Google AI Studio", "signup": "https://aistudio.google.com/apikey"},
    {"id": "groq", "category": "Script (LLM)", "name": "Groq (gpt-oss-120b)", "env": ["GROQ_API_KEY"],
     "free": "Free tier, ~1,000 requests/day", "signup": "https://console.groq.com/keys"},
    {"id": "openrouter", "category": "Script (LLM)", "name": "OpenRouter free models", "env": ["OPENROUTER_API_KEY"],
     "free": "50 free requests/day", "signup": "https://openrouter.ai/keys"},
    {"id": "pollinations", "category": "Script + Images", "name": "Pollinations", "env": ["POLLINATIONS_API_KEY"],
     "free": "Works without a key (slow: ~1 image/45s); free key removes limits", "signup": "https://enter.pollinations.ai",
     "keyless": True},
    {"id": "cloudflare", "category": "Images", "name": "Cloudflare Workers AI (FLUX schnell)",
     "env": ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_TOKEN"], "free": "10,000 free neurons/day",
     "signup": "https://dash.cloudflare.com/profile/api-tokens"},
    {"id": "huggingface", "category": "Images", "name": "Hugging Face (FLUX.1-schnell)", "env": ["HF_TOKEN"],
     "free": "Small monthly free credit", "signup": "https://huggingface.co/settings/tokens"},
    {"id": "edge-tts", "category": "Voice", "name": "Microsoft Edge neural voices", "env": [],
     "free": "Free, no key needed", "keyless": True},
    {"id": "cloudinary", "category": "Storage", "name": "Cloudinary",
     "env": ["CLOUDINARY_URL"],
     "free": "25 free credits/month - keeps videos after server restarts", "signup": "https://cloudinary.com/users/register_free"},
]
_ALLOWED_ENV = {env for p in PROVIDERS for env in p["env"]}


def _provider_status() -> List[Dict[str, Any]]:
    out = []
    for p in PROVIDERS:
        if p["id"] == "cloudinary":
            # Also accepts the three separate CLOUDINARY_* variables.
            configured = media.cloudinary_configured()
        else:
            configured = bool(p["env"]) and all(os.getenv(e) for e in p["env"])
        out.append({**p, "configured": configured, "active": configured or p.get("keyless", False)})
    return out


@router.get("/providers")
async def get_providers(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Which providers are configured on the server. Never returns key values."""
    return {
        "providers": _provider_status(),
        "llm_order": llm.configured_providers(),
        "storage": "cloudinary" if media.cloudinary_configured() else "local",
        "can_edit": user["role"] == "admin",
    }


class APIKeyUpdateRequest(BaseModel):
    env: str = Field(..., examples=["GEMINI_API_KEY"])
    value: str = Field(..., min_length=5, max_length=500)


@router.post("/keys")
async def update_api_key(req: APIKeyUpdateRequest, admin: Dict[str, Any] = Depends(require_admin)) -> Dict[str, str]:
    """Admin-only: set a provider key for the running process (lost on restart - set it in your host's env too)."""
    if req.env not in _ALLOWED_ENV:
        raise HTTPException(status_code=400, detail="Unknown provider variable.")
    os.environ[req.env] = req.value.strip()
    return {"status": "success", "message": f"{req.env} applied until the next restart. Add it to your hosting environment to persist it."}


@router.get("/workspace")
async def get_workspace_details(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """The user's workspace with real usage counts."""
    ws = (await db.execute(select(DBWorkspace).where(DBWorkspace.owner_id == user["user_id"]))).scalars().first()
    counts = dict(
        (await db.execute(
            select(DBProject.status, func.count()).where(DBProject.creator_id == user["user_id"]).group_by(DBProject.status)
        )).all()
    )
    return {
        "id": ws.id if ws else None,
        "name": ws.name if ws else "My Workspace",
        "projects_total": sum(counts.values()),
        "projects_by_status": counts,
    }
