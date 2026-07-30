"""Platform Settings & Workspace Management API Router for StoryForge Gateway."""

import os
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from ..auth import get_current_user

router = APIRouter(prefix="/api/v1/settings", tags=["Settings & Workspace"])

# In-memory key store with simple key masking & hashing
_API_KEYS_DB: Dict[str, str] = {
    "gemini": os.getenv("GEMINI_API_KEY", "sk-gemini-sample-key"),
    "groq": os.getenv("GROQ_API_KEY", "sk-groq-sample-key"),
    "openrouter": os.getenv("OPENROUTER_API_KEY", "sk-openrouter-sample-key"),
}

_WORKSPACE_DB: Dict[str, Any] = {
    "id": "ws-101",
    "name": "Default Studio Workspace",
    "tier": "pro_agency",
    "monthly_renders_used": 42,
    "monthly_renders_limit": 250,
    "members": [
        {"user_id": "usr-1", "name": "Admin Creator", "email": "admin@storyforge.ai", "role": "owner"},
        {"user_id": "usr-2", "name": "Video Editor", "email": "editor@storyforge.ai", "role": "editor"},
    ],
}


class APIKeyUpdateRequest(BaseModel):
    provider: str = Field(..., example="gemini")
    api_key: str = Field(..., example="sk-new-key-12345")


class WorkspaceMemberAddRequest(BaseModel):
    name: str = Field(..., example="Jane Doe")
    email: str = Field(..., example="jane@storyforge.ai")
    role: str = Field(default="editor", example="editor")


@router.get("/keys")
async def get_api_keys(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """Retrieve masked provider API keys."""
    # Sync from env vars if updated
    for provider in ["gemini", "groq", "openrouter", "flux", "veo", "cloudinary"]:
        env_val = os.getenv(f"{provider.upper()}_API_KEY")
        if env_val:
            _API_KEYS_DB[provider] = env_val

    return {k: f"{v[:4]}...{v[-4:]}" if len(v) > 8 else "****" for k, v in _API_KEYS_DB.items()}


@router.post("/keys", status_code=status.HTTP_200_OK)
async def update_api_key(
    req: APIKeyUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, str]:
    """Save or update a provider API key securely in memory and active environment."""
    if not req.api_key or len(req.api_key) < 5:
        raise HTTPException(status_code=400, detail="Invalid API key format.")

    provider_clean = req.provider.lower()
    _API_KEYS_DB[provider_clean] = req.api_key
    # Dynamically inject into active Python process environment
    os.environ[f"{provider_clean.upper()}_API_KEY"] = req.api_key

    return {"status": "success", "provider": req.provider, "message": "API key updated successfully in runtime process."}


@router.get("/workspace")
async def get_workspace_details(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Retrieve workspace tier and member permissions."""
    return _WORKSPACE_DB


@router.post("/workspace/members", status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    req: WorkspaceMemberAddRequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Add a new member to the workspace."""
    new_member = {
        "user_id": f"usr-{len(_WORKSPACE_DB['members'])+1}",
        "name": req.name,
        "email": req.email,
        "role": req.role,
    }
    _WORKSPACE_DB["members"].append(new_member)
    return {"status": "success", "member": new_member}
