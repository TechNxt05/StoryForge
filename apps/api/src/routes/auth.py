"""Authentication API Router for StoryForge Gateway."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from ..auth import (
    _USERS_DB,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class SignupRequest(BaseModel):
    email: str = Field(..., example="creator@storyforge.ai")
    password: str = Field(..., min_length=6, example="password123")
    full_name: str = Field(..., example="Jane Creator")


class LoginRequest(BaseModel):
    email: str = Field(..., example="admin@storyforge.ai")
    password: str = Field(..., example="admin123storyforge")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(req: SignupRequest) -> Dict[str, Any]:
    """Register a new user account."""
    if req.email in _USERS_DB:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    user_id = f"usr-{len(_USERS_DB) + 1}"
    user_entry = {
        "id": user_id,
        "email": req.email,
        "full_name": req.full_name,
        "password_hash": hash_password(req.password),
        "role": "creator",
    }
    _USERS_DB[req.email] = user_entry

    token = create_access_token(user_id=user_id, email=req.email, role="creator")
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": req.email, "full_name": req.full_name, "role": "creator"},
    }


@router.post("/login")
async def login(req: LoginRequest) -> Dict[str, Any]:
    """Authenticate user and return JWT bearer token."""
    user = _USERS_DB.get(req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(user_id=user["id"], email=user["email"], role=user["role"])
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"], "role": user["role"]},
    }


@router.get("/me")
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Retrieve currently authenticated user profile."""
    return {"user": user}
