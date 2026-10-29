"""Projects API Router for StoryForge Gateway."""

import copy
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import delete as sa_delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from runtime import llm, media, pipeline
from .. import jobs
from ..auth import get_current_user
from ..database.postgres import (
    Asset as DBAsset,
    Project as DBProject,
    Story as DBStory,
    Workspace as DBWorkspace,
    get_postgres_session,
)

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

ASPECT_RATIOS = {"9:16", "16:9", "1:1"}


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    topic: str = Field(..., min_length=3, max_length=2000)
    content_pack_name: str = Field(default="history")
    aspect_ratio: str = Field(default="9:16")
    notes: str = Field(default="", max_length=6000)
    target_seconds: int = Field(default=45, ge=15, le=120)
    voice: str = Field(default=media.DEFAULT_VOICE)
    language: str = Field(default="English", max_length=40)
    auto_generate: bool = True

    @field_validator("aspect_ratio")
    @classmethod
    def check_aspect(cls, v: str) -> str:
        if v not in ASPECT_RATIOS:
            raise ValueError(f"aspect_ratio must be one of {sorted(ASPECT_RATIOS)}")
        return v

    @field_validator("content_pack_name")
    @classmethod
    def check_pack(cls, v: str) -> str:
        v = v.lower()
        if v not in pipeline.PACK_STYLES:
            raise ValueError(f"Unknown content pack '{v}'")
        return v

    @field_validator("voice")
    @classmethod
    def check_voice(cls, v: str) -> str:
        if v not in media.VOICES:
            raise ValueError("Unknown voice")
        return v


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    topic: Optional[str] = Field(default=None, min_length=3, max_length=2000)
    notes: Optional[str] = Field(default=None, max_length=6000)
    voice: Optional[str] = None
    target_seconds: Optional[int] = Field(default=None, ge=15, le=120)


class SceneEdit(BaseModel):
    heading: str = Field(default="", max_length=200)
    narration: str = Field(..., min_length=1, max_length=1500)
    visual_prompt: str = Field(..., min_length=1, max_length=1500)
    on_screen_text: str = Field(default="", max_length=80)


class ScenesUpdateRequest(BaseModel):
    scenes: List[SceneEdit] = Field(..., min_length=1, max_length=12)


class GenerateRequest(BaseModel):
    mode: str = Field(default="full", pattern="^(full|rerender)$")
    regenerate_images: List[int] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def _iso(dt: Any) -> str:
    return dt.isoformat() + "Z" if isinstance(dt, datetime) else str(dt or "")


def _public_scenes(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # image_path is a server-side file path; never send it to clients.
    return [{k: v for k, v in s.items() if k != "image_path"} for s in scenes]


def serialize(project: DBProject, full: bool = True) -> Dict[str, Any]:
    meta = project.metadata_json or {}
    settings = meta.get("settings", {})
    script = meta.get("script") or {}
    scenes = script.get("scenes", [])
    job = meta.get("job") or {}
    steps = job.get("steps", {})
    done = sum(1 for s in steps.values() if s.get("status") in ("completed", "skipped"))
    data: Dict[str, Any] = {
        "id": project.id,
        "title": project.title,
        "topic": project.topic,
        "content_pack_name": project.content_pack_name,
        "status": project.status,
        "created_at": _iso(project.created_at),
        "updated_at": _iso(project.updated_at),
        "aspect_ratio": settings.get("aspect_ratio", "9:16"),
        "thumbnail_url": next((s.get("image_url") for s in scenes if s.get("image_url")), None),
        "video": meta.get("video"),
        "progress": round(100 * done / len(steps)) if steps else 0,
        "scene_count": len(scenes),
        "providers": meta.get("providers"),
    }
    if full:
        public_script = {**script, "scenes": _public_scenes(scenes)} if script else None
        data.update(
            settings=settings,
            script=public_script,
            job=job or None,
            stale=meta.get("stale", False),
            history=meta.get("history", []),
            chat=meta.get("chat", []),
        )
    return data


async def _get_owned(project_id: str, user: Dict[str, Any], db: AsyncSession) -> DBProject:
    project = await db.get(DBProject, project_id)
    if not project or project.creator_id != user["user_id"]:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


async def _workspace_for(user_id: str, db: AsyncSession) -> str:
    ws = (await db.execute(select(DBWorkspace).where(DBWorkspace.owner_id == user_id))).scalars().first()
    if ws:
        return ws.id
    ws_id = f"ws-{user_id}"
    db.add(DBWorkspace(id=ws_id, name="My Workspace", slug=ws_id, owner_id=user_id))
    await db.flush()
    return ws_id


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Create a story project and (by default) start generating its video."""
    project = DBProject(
        id=f"proj-{uuid.uuid4().hex[:12]}",
        workspace_id=await _workspace_for(user["user_id"], db),
        creator_id=user["user_id"],
        title=req.title.strip(),
        topic=req.topic.strip(),
        content_pack_name=req.content_pack_name,
        status="draft",
        metadata_json={
            "settings": {
                "aspect_ratio": req.aspect_ratio,
                "notes": req.notes,
                "target_seconds": req.target_seconds,
                "voice": req.voice,
                "language": req.language,
            }
        },
    )
    db.add(project)
    await db.commit()
    if req.auto_generate:
        await jobs.start_generation(project.id, "full")
        await db.refresh(project)
    return serialize(project)


@router.get("")
async def list_projects(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """List the signed-in user's projects, newest first."""
    result = await db.execute(
        select(DBProject).where(DBProject.creator_id == user["user_id"]).order_by(DBProject.created_at.desc())
    )
    projects = [serialize(p, full=False) for p in result.scalars().all()]
    return {"projects": projects, "total_count": len(projects)}


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    return serialize(await _get_owned(project_id, user, db))


@router.patch("/{project_id}")
async def update_project(
    project_id: str,
    req: ProjectUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    project = await _get_owned(project_id, user, db)
    if req.title is not None:
        project.title = req.title.strip()
    if req.topic is not None:
        project.topic = req.topic.strip()
    meta = copy.deepcopy(project.metadata_json or {})
    settings = meta.setdefault("settings", {})
    if req.notes is not None:
        settings["notes"] = req.notes
    if req.voice is not None:
        if req.voice not in media.VOICES:
            raise HTTPException(status_code=422, detail="Unknown voice")
        if req.voice != settings.get("voice"):
            meta["stale"] = True
        settings["voice"] = req.voice
    if req.target_seconds is not None:
        settings["target_seconds"] = req.target_seconds
    project.metadata_json = meta
    await db.commit()
    await db.refresh(project)
    return serialize(project)


@router.put("/{project_id}/scenes")
async def update_scenes(
    project_id: str,
    req: ScenesUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Save manual edits to the script. Images are reused on re-render when prompts are unchanged."""
    project = await _get_owned(project_id, user, db)
    if jobs.is_running(project_id):
        raise HTTPException(status_code=409, detail="Wait for the current generation to finish.")
    meta = copy.deepcopy(project.metadata_json or {})
    meta["script"] = _merge_scenes(meta.get("script") or {"title": project.title}, [s.model_dump() for s in req.scenes])
    meta["stale"] = True
    project.metadata_json = meta
    await db.commit()
    await db.refresh(project)
    return serialize(project)


def _merge_scenes(script: Dict[str, Any], edited: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Carry generated media fields (image, duration) over to edited scenes at the same position."""
    old = script.get("scenes", [])
    merged = []
    for i, scene in enumerate(edited):
        prev = old[i] if i < len(old) else {}
        carry = {k: v for k, v in prev.items() if k in ("image_url", "image_path", "image_provider", "seed")}
        if prev.get("visual_prompt") != scene["visual_prompt"]:
            carry = {}  # prompt changed -> image will be regenerated
        merged.append({**carry, **scene})
    return {**script, "scenes": merged}


@router.post("/{project_id}/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate(
    project_id: str,
    req: GenerateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Start a full generation (new script) or a re-render of the current script."""
    await _get_owned(project_id, user, db)
    try:
        await jobs.start_generation(project_id, req.mode, req.regenerate_images)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    db.expire_all()
    return serialize(await _get_owned(project_id, user, db))


@router.post("/{project_id}/chat")
async def chat_edit(
    project_id: str,
    req: ChatRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Edit the script with a natural-language instruction."""
    project = await _get_owned(project_id, user, db)
    if jobs.is_running(project_id):
        raise HTTPException(status_code=409, detail="Wait for the current generation to finish.")
    meta = copy.deepcopy(project.metadata_json or {})
    script = meta.get("script")
    if not script or not script.get("scenes"):
        raise HTTPException(status_code=400, detail="Generate the video once before editing it with chat.")
    try:
        revised = await pipeline.revise_script(script["scenes"], req.message, project.title)
    except (llm.LLMUnavailableError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"The AI editor is unavailable right now: {str(exc)[:200]}")

    meta["script"] = _merge_scenes(script, revised["scenes"])
    meta["stale"] = True
    chat = meta.setdefault("chat", [])
    chat += [
        {"role": "user", "text": req.message, "at": jobs.now_iso()},
        {"role": "assistant", "text": revised["reply"], "at": jobs.now_iso(), "provider": revised["provider"]},
    ]
    del chat[:-30]
    project.metadata_json = meta
    await db.commit()
    await db.refresh(project)
    return {"reply": revised["reply"], "project": serialize(project)}


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> None:
    project = await _get_owned(project_id, user, db)
    if jobs.is_running(project_id):
        raise HTTPException(status_code=409, detail="Wait for the current generation to finish.")
    # Explicit deletes: ORM cascades would lazy-load relationships, which async sessions can't do.
    await db.execute(sa_delete(DBAsset).where(DBAsset.project_id == project_id))
    await db.execute(sa_delete(DBStory).where(DBStory.project_id == project_id))
    await db.execute(sa_delete(DBProject).where(DBProject.id == project_id))
    await db.commit()
    pipeline.cleanup_project_media(project_id)
