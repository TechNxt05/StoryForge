"""Authentication API Router for StoryForge Gateway."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import (
    _USERS_DB,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..database.postgres import User as DBUser, Workspace as DBWorkspace, get_postgres_session

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    email: str = Field(..., example="creator@storyforge.ai")
    password: str = Field(..., min_length=6, example="password123")
    full_name: str = Field(..., example="Jane Creator")


class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@storyforge.ai")
    password: str = Field(..., example="admin123storyforge")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    req: SignupRequest,
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Register a new user account with database persistence."""
    hashed = hash_password(req.password)
    user_id = f"usr-{hash(req.email) & 0xffffff:06x}"

    # Try DB lookup first
    try:
        stmt = select(DBUser).where(DBUser.email == req.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        # Persist to database
        db_user = DBUser(
            id=user_id,
            email=req.email,
            hashed_password=hashed,
            full_name=req.full_name,
            role="creator",
        )
        db.add(db_user)

        # Create user's personal workspace
        ws_id = f"ws-{user_id}"
        db_ws = DBWorkspace(
            id=ws_id,
            name=f"{req.full_name}'s Workspace",
            slug=f"ws-{user_id}",
            owner_id=user_id,
        )
        db.add(db_ws)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth Signup] DB insert note: {e}")

    # Also update in-memory fallback cache
    _USERS_DB[req.email] = {
        "id": user_id,
        "email": req.email,
        "full_name": req.full_name,
        "password_hash": hashed,
        "role": "creator",
    }

    token = create_access_token(user_id=user_id, email=req.email, role="creator")
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": req.email, "full_name": req.full_name, "role": "creator"},
    }


@router.post("/login")
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_postgres_session),
) -> Dict[str, Any]:
    """Authenticate user and return JWT bearer token."""
    user_id = None
    email = req.email
    full_name = ""
    role = "creator"
    password_hash = None

    # Try DB lookup first
    try:
        stmt = select(DBUser).where(DBUser.email == req.email)
        result = await db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:
            user_id = db_user.id
            email = db_user.email
            full_name = db_user.full_name
            role = db_user.role
            password_hash = db_user.hashed_password
    except Exception:
        pass

    # Fallback to in-memory store
    if not password_hash and req.email in _USERS_DB:
        mem_user = _USERS_DB[req.email]
        user_id = mem_user["id"]
        email = mem_user["email"]
        full_name = mem_user["full_name"]
        role = mem_user["role"]
        password_hash = mem_user["password_hash"]

    if not password_hash or not verify_password(req.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(user_id=user_id, email=email, role=role)
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": email, "full_name": full_name, "role": role},
    }


@router.get("/me")
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Retrieve currently authenticated user profile."""
    return {"user": user}
