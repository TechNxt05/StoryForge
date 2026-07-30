"""Authentication & Security Utilities for StoryForge API Gateway."""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Read secret from env var (set in Render dashboard), with fallback
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "storyforge_super_secret_production_key_change_me")
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 86400  # 24 hours

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash password using SHA-256 HMAC with secret key."""
    return hmac.new(SECRET_KEY.encode(), password.encode(), hashlib.sha256).hexdigest()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return hmac.compare_digest(hash_password(plain_password), password_hash)


# In-memory user store fallback — admin password hashed with the SAME function used for verification
_USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin@storyforge.ai": {
        "id": "usr-admin-1",
        "email": "admin@storyforge.ai",
        "full_name": "Admin Creator",
        "password_hash": hash_password("admin123storyforge"),
        "role": "admin",
    }
}


def create_access_token(user_id: str, email: str, role: str = "creator") -> str:
    """Generate JWT bearer token."""
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }

    b64_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    b64_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

    signature_input = f"{b64_header}.{b64_payload}".encode()
    signature = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    ).decode().rstrip("=")

    return f"{b64_header}.{b64_payload}.{signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT bearer token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        b64_header, b64_payload, signature = parts
        padding_payload = "=" * (-len(b64_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(b64_payload + padding_payload)
        payload = json.loads(payload_bytes.decode())

        if time.time() > payload.get("exp", 0):
            return None  # Expired

        # Verify signature
        signature_input = f"{b64_header}.{b64_payload}".encode()
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        ).decode().rstrip("=")

        if not hmac.compare_digest(expected_sig, signature):
            return None  # Tampered

        return payload
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """FastAPI security dependency validating bearer token."""
    if not credentials or not credentials.credentials:
        # Fallback default guest user for backward compatibility
        return {"user_id": "usr-guest-1", "email": "guest@storyforge.ai", "role": "creator"}

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": payload["sub"],
        "email": payload["email"],
        "role": payload.get("role", "creator"),
    }
