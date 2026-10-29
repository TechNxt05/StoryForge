"""Authentication & Security Utilities for StoryForge API Gateway."""

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("storyforge.auth")

_DEFAULT_SECRET = "storyforge-dev-secret-change-me"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", _DEFAULT_SECRET)
if SECRET_KEY == _DEFAULT_SECRET:
    logger.warning("JWT_SECRET_KEY is not set - using an insecure development secret.")

ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 7 * 86400
PBKDF2_ITERATIONS = 200_000

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Salted PBKDF2-SHA256 hash, stored as pbkdf2$<iterations>$<salt>$<hash>."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS).hex()
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify password against a stored hash (also accepts the legacy unsalted HMAC format)."""
    if not password_hash:
        return False
    if password_hash.startswith("pbkdf2$"):
        try:
            _, iterations, salt, digest = password_hash.split("$")
        except ValueError:
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(candidate, digest)
    legacy = hmac.new(SECRET_KEY.encode(), plain_password.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(legacy, password_hash)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def create_access_token(user_id: str, email: str, role: str = "creator") -> str:
    """Generate JWT bearer token."""
    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }

    b64_header = _b64(json.dumps(header).encode())
    b64_payload = _b64(json.dumps(payload).encode())
    signature = _b64(hmac.new(SECRET_KEY.encode(), f"{b64_header}.{b64_payload}".encode(), hashlib.sha256).digest())
    return f"{b64_header}.{b64_payload}.{signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT bearer token."""
    try:
        b64_header, b64_payload, signature = token.split(".")

        # Verify the signature before trusting anything in the payload.
        expected_sig = _b64(
            hmac.new(SECRET_KEY.encode(), f"{b64_header}.{b64_payload}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(expected_sig, signature):
            return None

        payload = json.loads(base64.urlsafe_b64decode(b64_payload + "=" * (-len(b64_payload) % 4)).decode())
        if time.time() > payload.get("exp", 0):
            return None
        return payload
    except Exception:
        return None


def is_admin_email(email: str) -> bool:
    admins = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
    return email.lower() in admins


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """FastAPI security dependency validating the bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": payload["sub"],
        "email": payload["email"],
        "role": "admin" if is_admin_email(payload["email"]) else payload.get("role", "creator"),
    }


async def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return user
