"""API Gateway Router Integration Tests."""

import uuid

import httpx
import pytest
from apps.api.src.main import app


def client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def signup(c: httpx.AsyncClient, email: str | None = None) -> dict:
    email = email or f"user-{uuid.uuid4().hex[:8]}@test.dev"
    res = await c.post("/api/v1/auth/signup", json={"email": email, "password": "password123", "full_name": "Test User"})
    assert res.status_code == 201, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


PROJECT = {
    "title": "History of Printing",
    "topic": "Gutenberg press impact",
    "content_pack_name": "history",
    "aspect_ratio": "9:16",
    "auto_generate": False,
}


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    async with client() as c:
        response = await c.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_projects_require_auth() -> None:
    async with client() as c:
        assert (await c.get("/api/v1/projects")).status_code == 401
        assert (await c.post("/api/v1/projects", json=PROJECT)).status_code == 401
        bad = {"Authorization": "Bearer not.a.token"}
        assert (await c.get("/api/v1/projects", headers=bad)).status_code == 401


@pytest.mark.asyncio
async def test_create_get_list_project() -> None:
    async with client() as c:
        headers = await signup(c)
        response = await c.post("/api/v1/projects", json=PROJECT, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "History of Printing"
        assert data["status"] == "draft"
        assert data["settings"]["aspect_ratio"] == "9:16"

        get_res = await c.get(f"/api/v1/projects/{data['id']}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["id"] == data["id"]

        list_res = await c.get("/api/v1/projects", headers=headers)
        assert [p["id"] for p in list_res.json()["projects"]] == [data["id"]]


@pytest.mark.asyncio
async def test_projects_are_private_to_their_owner() -> None:
    async with client() as c:
        owner = await signup(c)
        intruder = await signup(c)
        project_id = (await c.post("/api/v1/projects", json=PROJECT, headers=owner)).json()["id"]

        assert (await c.get(f"/api/v1/projects/{project_id}", headers=intruder)).status_code == 404
        assert (await c.delete(f"/api/v1/projects/{project_id}", headers=intruder)).status_code == 404
        assert (await c.get("/api/v1/projects", headers=intruder)).json()["total_count"] == 0


@pytest.mark.asyncio
async def test_project_validation() -> None:
    async with client() as c:
        headers = await signup(c)
        for bad in ({"aspect_ratio": "4:3"}, {"content_pack_name": "nope"}, {"voice": "robot"}, {"target_seconds": 5}):
            res = await c.post("/api/v1/projects", json={**PROJECT, **bad}, headers=headers)
            assert res.status_code == 422, bad


@pytest.mark.asyncio
async def test_scene_edits_keep_images_for_unchanged_prompts() -> None:
    from apps.api.src import jobs

    async with client() as c:
        headers = await signup(c)
        project_id = (await c.post("/api/v1/projects", json=PROJECT, headers=headers)).json()["id"]

        def seed_script(meta):
            meta["script"] = {
                "title": "t",
                "scenes": [
                    {"heading": "A", "narration": "one", "visual_prompt": "p1", "on_screen_text": "", "image_url": "/media/a.jpg", "image_path": "/srv/a.jpg"},
                    {"heading": "B", "narration": "two", "visual_prompt": "p2", "on_screen_text": "", "image_url": "/media/b.jpg", "image_path": "/srv/b.jpg"},
                ],
            }

        await jobs.update_project(project_id, seed_script)
        edited = [
            {"heading": "A", "narration": "one, edited", "visual_prompt": "p1", "on_screen_text": ""},
            {"heading": "B", "narration": "two", "visual_prompt": "a new prompt", "on_screen_text": ""},
        ]
        res = await c.put(f"/api/v1/projects/{project_id}/scenes", json={"scenes": edited}, headers=headers)
        assert res.status_code == 200
        body = res.json()
        scenes = body["script"]["scenes"]
        assert body["stale"] is True
        assert scenes[0]["narration"] == "one, edited"
        assert scenes[0]["image_url"] == "/media/a.jpg"  # prompt unchanged -> image reused
        assert "image_url" not in scenes[1]  # prompt changed -> regenerated on render
        assert all("image_path" not in s for s in scenes)  # server paths never leak


@pytest.mark.asyncio
async def test_meta_endpoint_lists_packs_and_voices() -> None:
    async with client() as c:
        data = (await c.get("/api/v1/meta")).json()
        assert {p["id"] for p in data["content_packs"]} >= {"history", "technology", "science"}
        assert data["default_voice"] in {v["id"] for v in data["voices"]}


@pytest.mark.asyncio
async def test_runtime_router_requires_auth_and_plans() -> None:
    async with client() as c:
        plan_payload = {"goal": "Explain Quantum Computers in 60s", "content_pack": "technology", "aspect_ratio": "9:16"}
        assert (await c.post("/api/v1/runtime/plan", json=plan_payload)).status_code == 401

        headers = await signup(c)
        response = await c.post("/api/v1/runtime/plan", json=plan_payload, headers=headers)
        assert response.status_code == 200
        assert len(response.json()["steps"]) >= 4

        unknown = await c.post("/api/v1/runtime/execute", json={"capability_name": "nope"}, headers=headers)
        assert unknown.status_code == 404
