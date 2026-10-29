"""Final System Integration Test Suite."""

import sys
from pathlib import Path
import httpx
import pytest

# Add monorepo root and content-packs to Python module search path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "content-packs" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "content-packs" / "src"))

from apps.api.src.main import app


@pytest.mark.asyncio
async def test_full_system_gateway_health() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200

        data = res.json()
        assert data["status"] == "ok"
        assert data["service"] == "storyforge-api"
        assert data["registered_capabilities_count"] >= 15
        assert data["storage"] in ("local", "cloudinary")


@pytest.mark.asyncio
async def test_full_system_project_and_runtime_workflow() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Create project
        proj_req = {
            "title": "Final Integration Test Video",
            "topic": "The History of Aviation",
            "content_pack_name": "history",
            "aspect_ratio": "9:16",
        }
        signup = await client.post(
            "/api/v1/auth/signup", json={"email": "final-integration@test.dev", "password": "password123", "full_name": "F"}
        )
        headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}
        create_res = await client.post("/api/v1/projects", json={**proj_req, "auto_generate": False}, headers=headers)
        assert create_res.status_code == 201

        # Generate DAG plan
        plan_req = {"goal": "The History of Aviation", "content_pack": "history"}
        plan_res = await client.post("/api/v1/runtime/plan", json=plan_req, headers=headers)
        assert plan_res.status_code == 200
        assert len(plan_res.json()["steps"]) >= 4

        # Execute capability step via runtime engine
        exec_req = {"capability_name": "deep_research", "kwargs": {"topic": "The History of Aviation"}}
        exec_res = await client.post("/api/v1/runtime/execute", json=exec_req, headers=headers)
        assert exec_res.status_code == 200
        assert exec_res.json()["status"] == "completed"
