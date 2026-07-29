"""E2E Integration & System Audit Remediation Test Suite."""

import sys
from pathlib import Path
import httpx
import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.src.main import app


@pytest.mark.asyncio
async def test_e2e_user_signup_login_and_workflow() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: User Signup
        signup_req = {
            "email": "e2e_creator@storyforge.ai",
            "password": "e2e_password_123",
            "full_name": "E2E Creator User",
        }
        signup_res = await client.post("/api/v1/auth/signup", json=signup_req)
        assert signup_res.status_code == 201
        token = signup_res.json()["access_token"]
        assert token is not None

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Query Current User Profile
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["user"]["email"] == "e2e_creator@storyforge.ai"

        # Step 3: Create Project
        proj_req = {
            "title": "E2E Story Project",
            "topic": "Space Travel and Artificial Intelligence",
            "content_pack_name": "technology",
            "aspect_ratio": "9:16",
        }
        proj_res = await client.post("/api/v1/projects", json=proj_req, headers=headers)
        assert proj_res.status_code == 201
        proj_id = proj_res.json()["id"]

        # Step 4: Verify Masked Key Settings
        keys_res = await client.get("/api/v1/settings/keys", headers=headers)
        assert keys_res.status_code == 200
        keys = keys_res.json()
        assert "gemini" in keys
