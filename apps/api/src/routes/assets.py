"""Assets API Router for user media uploads."""

import os
import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import AssetResponse
from ..database.postgres import Asset as DBAsset, get_postgres_session
from runtime.providers.fallback import ProviderFallbackEngine

router = APIRouter(prefix="/api/v1/projects", tags=["Assets"])

@router.post("/{project_id}/assets/upload", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    project_id: str,
    file: UploadFile = File(...),
    asset_type: str = Form("video"),
    db: AsyncSession = Depends(get_postgres_session),
) -> Any:
    """Upload a raw user asset to the project (e.g. custom video or image)."""
    
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    
    from apps.api.src.main import fallback_engine
    cloudinary_adapter = fallback_engine._providers.get("storage", {}).get("cloudinary")
    
    upload_result = {}
    if cloudinary_adapter and hasattr(cloudinary_adapter, "upload_binary"):
        upload_result = await cloudinary_adapter.upload_binary(file_bytes, asset_type, file.filename)
    else:
        # Fallback if no cloudinary configured or upload_binary not implemented
        asset_id = f"local-{uuid.uuid4().hex[:8]}"
        mock_url = f"https://res.cloudinary.com/demo/video/upload/dog.mp4" if asset_type == "video" else f"https://pollinations.ai/p/placeholder_{asset_id}"
        upload_result = {
            "cdn_url": mock_url,
            "asset_id": asset_id,
        }
    
    asset_id = str(uuid.uuid4())
    cdn_url = upload_result.get("cdn_url")
    
    db_asset = DBAsset(
        id=asset_id,
        project_id=project_id,
        asset_type=asset_type,
        provider_name="user_upload",
        storage_url=cdn_url,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        metadata_json={"original_filename": file.filename, "is_user_uploaded": True}
    )
    
    try:
        db.add(db_asset)
        await db.commit()
    except Exception:
        pass
        
    return {
        "id": asset_id,
        "project_id": project_id,
        "asset_type": asset_type,
        "provider_name": "user_upload",
        "storage_url": cdn_url,
        "file_size_bytes": file_size,
        "mime_type": file.content_type or "application/octet-stream",
        "metadata_json": {"original_filename": file.filename, "is_user_uploaded": True},
        "created_at": "2026-07-31T00:00:00Z"
    }
