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
        assert data["service"] == "storyforge-api-gateway"
        assert data["registered_capabilities_count"] >= 15
        assert data["content_packs_count"] >= 5
        assert data["worker_cluster_nodes"] >= 1


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
        create_res = await client.post("/api/v1/projects", json=proj_req)
        assert create_res.status_code == 201

        # Generate DAG plan
        plan_req = {"goal": "The History of Aviation", "content_pack_name": "history"}
        plan_res = await client.post("/api/v1/runtime/plan", json=plan_req)
        assert plan_res.status_code == 200
        assert len(plan_res.json()["steps"]) >= 4

        # Execute capability step via runtime engine
        exec_req = {"capability_name": "deep_research", "input_data": {"topic": "The History of Aviation"}}
        exec_res = await client.post("/api/v1/runtime/execute", json=exec_req)
        assert exec_res.status_code == 200
        assert exec_res.json()["status"] == "completed"
