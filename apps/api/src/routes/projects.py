"""Projects API Router for StoryForge Gateway."""

from datetime import datetime
import uuid
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import ProjectCreateRequest, ProjectListResponse, ProjectResponse
from ..database.postgres import Project as DBProject, get_postgres_session

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

# Fallback transient memory store when PostgreSQL is offline
_PROJECTS_DB: Dict[str, ProjectResponse] = {}


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    req: ProjectCreateRequest,
    db: AsyncSession = Depends(get_postgres_session),
) -> ProjectResponse:
    """Create a new story project with database persistence."""
    project_id = f"proj-{uuid.uuid4().hex[:8]}"
    workspace_id = "ws-default"
    creator_id = "user-default"
    now_iso = datetime.utcnow().isoformat()

    project_dto = ProjectResponse(
        id=project_id,
        workspace_id=workspace_id,
        creator_id=creator_id,
        title=req.title,
        topic=req.topic,
        content_pack_name=req.content_pack_name,
        status="draft",
        created_at=now_iso,
    )

    try:
        # Attempt PostgreSQL DB insertion
        db_project = DBProject(
            id=project_id,
            workspace_id=workspace_id,
            creator_id=creator_id,
            title=req.title,
            topic=req.topic,
            content_pack_name=req.content_pack_name,
            status="draft",
        )
        db.add(db_project)
        await db.commit()
    except Exception:
        # Fallback to in-memory cache if DB container offline
        _PROJECTS_DB[project_id] = project_dto

    _PROJECTS_DB[project_id] = project_dto
    return project_dto


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    db: AsyncSession = Depends(get_postgres_session),
) -> ProjectListResponse:
    """List all story projects."""
    try:
        stmt = select(DBProject).order_by(DBProject.created_at.desc())
        result = await db.execute(stmt)
        db_projects = result.scalars().all()

        if db_projects:
            dtos = [
                ProjectResponse(
                    id=p.id,
                    workspace_id=p.workspace_id,
                    creator_id=p.creator_id,
                    title=p.title,
                    topic=p.topic,
                    content_pack_name=p.content_pack_name,
                    status=p.status,
                    created_at=p.created_at.isoformat() if isinstance(p.created_at, datetime) else str(p.created_at),
                )
                for p in db_projects
            ]
            return ProjectListResponse(projects=dtos, total_count=len(dtos))
    except Exception:
        pass

    # Fallback to transient memory store
    projects = list(_PROJECTS_DB.values())
    return ProjectListResponse(projects=projects, total_count=len(projects))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_postgres_session),
) -> ProjectResponse:
    """Retrieve project details by ID."""
    try:
        stmt = select(DBProject).where(DBProject.id == project_id)
        result = await db.execute(stmt)
        p = result.scalar_one_or_none()
        if p:
            return ProjectResponse(
                id=p.id,
                workspace_id=p.workspace_id,
                creator_id=p.creator_id,
                title=p.title,
                topic=p.topic,
                content_pack_name=p.content_pack_name,
                status=p.status,
                created_at=p.created_at.isoformat() if isinstance(p.created_at, datetime) else str(p.created_at),
            )
    except Exception:
        pass

    if project_id not in _PROJECTS_DB:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return _PROJECTS_DB[project_id]
