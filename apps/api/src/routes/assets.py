"""Asset library: generated and uploaded media for the signed-in user."""

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from runtime import media
from ..auth import get_current_user
from ..database.postgres import Asset as DBAsset, Project as DBProject, get_postgres_session

router = APIRouter(prefix="/api/v1", tags=["Assets"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_TYPES = {"image": ("image/",), "video": ("video/",), "audio": ("audio/",)}


def _serialize(asset: DBAsset, project_title: str = "") -> Dict[str, Any]:
    return {
        "id": asset.id,
        "project_id": asset.project_id,
        "project_title": project_title,
        "asset_type": asset.asset_type,
        "provider_name": asset.provider_name,
        "storage_url": asset.storage_url,
        "file_size_bytes": asset.file_size_bytes,
        "mime_type": asset.mime_type,
        "metadata_json": asset.metadata_json or {},
        "created_at": asset.created_at.isoformat() + "Z" if asset.created_at else None,
    }


@router.get("/assets")
async def list_assets(
    asset_type: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    stmt = (
        select(DBAsset, DBProject.title)
        .join(DBProject, DBProject.id == DBAsset.project_id)
        .where(DBProject.creator_id == user["user_id"])
        .order_by(DBAsset.created_at.desc())
    )
    if asset_type:
        stmt = stmt.where(DBAsset.asset_type == asset_type)
    rows = (await db.execute(stmt)).all()
    return {"assets": [_serialize(a, title) for a, title in rows]}


@router.post("/projects/{project_id}/assets/upload", status_code=status.HTTP_201_CREATED)
async def upload_asset(
    project_id: str,
    file: UploadFile = File(...),
    asset_type: str = Form("image"),
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Upload a reference image/video/audio file to a project."""
    project = await db.get(DBProject, project_id)
    if not project or project.creator_id != user["user_id"]:
        raise HTTPException(status_code=404, detail="Project not found.")
    if asset_type not in ALLOWED_TYPES or not (file.content_type or "").startswith(ALLOWED_TYPES[asset_type]):
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 25 MB.")

    suffix = Path(file.filename or "").suffix.lower()[:8] or ".bin"
    dest = media.MEDIA_DIR / project_id / "uploads" / f"{uuid.uuid4().hex}{suffix}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    # Cloudinary stores audio under the "video" resource type.
    published = await media.publish_file(dest, "video" if asset_type == "audio" else asset_type)

    asset = DBAsset(
        project_id=project_id,
        asset_type=asset_type,
        provider_name="user_upload",
        storage_url=published["url"],
        file_size_bytes=len(data),
        mime_type=file.content_type or "application/octet-stream",
        metadata_json={"original_filename": file.filename},
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return _serialize(asset, project.title)
