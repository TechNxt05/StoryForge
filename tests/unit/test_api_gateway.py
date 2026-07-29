"""API Gateway Router Integration Tests."""

import pytest
import httpx
from apps.api.src.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_and_get_project() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_payload = {
            "title": "History of Printing",
            "topic": "Gutenberg press impact",
            "content_pack_name": "history",
            "aspect_ratio": "9:16",
        }
        response = await client.post("/api/v1/projects", json=create_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "History of Printing"
        project_id = data["id"]

        # Get single project
        get_res = await client.get(f"/api/v1/projects/{project_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == project_id

        # List projects
        list_res = await client.get("/api/v1/projects")
        assert list_res.status_code == 200
        assert list_res.json()["total_count"] >= 1


@pytest.mark.asyncio
async def test_runtime_plan_generation() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        plan_payload = {
            "goal": "Explain Quantum Computers in 60s",
            "content_pack": "technology",
            "aspect_ratio": "9:16",
        }
        response = await client.post("/api/v1/runtime/plan", json=plan_payload)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert len(data["steps"]) >= 4


@pytest.mark.asyncio
async def test_runtime_execute_background_task() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        exec_payload = {
            "capability_name": "deep_research",
            "kwargs": {"topic": "AI Agents"},
            "run_in_background": True,
        }
        response = await client.post("/api/v1/runtime/execute", json=exec_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enqueued"
        task_id = data["task_id"]

        # Query status
        status_res = await client.get(f"/api/v1/runtime/tasks/{task_id}")
        assert status_res.status_code == 200
        assert status_res.json()["task_id"] == task_id
