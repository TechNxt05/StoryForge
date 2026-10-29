"""Authentication API Router for StoryForge Gateway."""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import create_access_token, get_current_user, hash_password, is_admin_email, verify_password
from ..database.postgres import User as DBUser, Workspace as DBWorkspace, get_postgres_session

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    email: str = Field(..., max_length=255, examples=["creator@storyforge.ai"])
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255, examples=["Jane Creator"])

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


def _user_payload(user: DBUser) -> Dict[str, Any]:
    role = "admin" if is_admin_email(user.email) else user.role
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": role}


def _token_response(user: DBUser) -> Dict[str, Any]:
    payload = _user_payload(user)
    return {
        "access_token": create_access_token(user_id=user.id, email=user.email, role=payload["role"]),
        "token_type": "bearer",
        "user": payload,
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest, db: AsyncSession = Depends(get_postgres_session)) -> Dict[str, Any]:
    """Register a new user and their personal workspace."""
    existing = await db.execute(select(DBUser).where(func.lower(DBUser.email) == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user_id = str(uuid.uuid4())
    user = DBUser(
        id=user_id,
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name.strip(),
        role="creator",
    )
    db.add(user)
    db.add(DBWorkspace(id=f"ws-{user_id}", name=f"{user.full_name}'s Workspace", slug=f"ws-{user_id}", owner_id=user_id))
    await db.commit()
    return _token_response(user)


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_postgres_session)) -> Dict[str, Any]:
    """Authenticate user and return a JWT bearer token."""
    result = await db.execute(select(DBUser).where(func.lower(DBUser.email) == req.email.strip().lower()))
    user = result.scalar_one_or_none()
    if not user or not user.is_active or not verify_password(req.password, user.hashed_password or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

    # Transparently upgrade legacy unsalted hashes.
    if not (user.hashed_password or "").startswith("pbkdf2$"):
        user.hashed_password = hash_password(req.password)
        await db.commit()
    return _token_response(user)


@router.get("/me")
async def get_current_user_profile(
    current: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Retrieve the signed-in user's profile."""
    user = await db.get(DBUser, current["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists.")
    return {"user": _user_payload(user)}
