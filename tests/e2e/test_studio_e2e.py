"""End-to-end: sign up, generate a real MP4 (offline providers), edit, re-render, delete."""

import asyncio
from pathlib import Path

import httpx
import pytest

from apps.api.src.main import app
from runtime import media, pipeline


async def _wait_for_job(c: httpx.AsyncClient, project_id: str, headers: dict, timeout: float = 180) -> dict:
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        data = (await c.get(f"/api/v1/projects/{project_id}", headers=headers)).json()
        if data["job"]["status"] in ("completed", "failed"):
            return data
        assert asyncio.get_event_loop().time() < deadline, f"job did not finish: {data['job']}"
        await asyncio.sleep(0.5)


@pytest.mark.asyncio
async def test_e2e_signup_generate_edit_rerender(offline_media, monkeypatch) -> None:
    async def no_wikipedia(*_args, **_kwargs):
        return [{"title": "Spaceflight", "url": "https://en.wikipedia.org/wiki/Spaceflight",
                 "extract": "Spaceflight is the use of space technology to fly spacecraft into outer space. "
                            "It is used for exploration and commercial activity. Humans first flew to space in 1961."}]

    monkeypatch.setattr(pipeline, "wikipedia_context", no_wikipedia)

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        signup = await c.post(
            "/api/v1/auth/signup",
            json={"email": "E2E_Creator@StoryForge.ai", "password": "e2e_password_123", "full_name": "E2E Creator"},
        )
        assert signup.status_code == 201
        headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

        # Email is case-insensitive and normalized.
        login = await c.post("/api/v1/auth/login", json={"email": "e2e_creator@storyforge.ai", "password": "e2e_password_123"})
        assert login.status_code == 200
        me = await c.get("/api/v1/auth/me", headers=headers)
        assert me.json()["user"]["email"] == "e2e_creator@storyforge.ai"

        created = await c.post(
            "/api/v1/projects",
            json={"title": "Space Travel", "topic": "How humans reached space", "content_pack_name": "science",
                  "aspect_ratio": "16:9", "target_seconds": 20},
            headers=headers,
        )
        assert created.status_code == 201
        project_id = created.json()["id"]
        assert created.json()["job"]["status"] in ("queued", "running")

        done = await _wait_for_job(c, project_id, headers)
        assert done["status"] == "completed", done["job"]
        # No LLM is reachable in tests, so the offline template writer is used and flagged.
        assert done["script"]["provider"] == "template"
        assert done["script"]["warning"]
        video = done["video"]
        assert video["url"].startswith("/media/") and video["width"] == 1024 and video["duration"] > 3
        assert Path(media.MEDIA_DIR, video["url"].removeprefix("/media/")).stat().st_size > 1000
        assert all(s["status"] in ("completed", "skipped") for s in done["job"]["steps"].values())

        # Generated media are served and listed in the asset library.
        assert (await c.get(video["url"])).status_code == 200
        assets = (await c.get("/api/v1/assets", headers=headers)).json()["assets"]
        assert {a["asset_type"] for a in assets} == {"video", "image"}

        # Chat editing needs an LLM: it reports unavailability instead of failing silently.
        chat = await c.post(f"/api/v1/projects/{project_id}/chat", json={"message": "shorter"}, headers=headers)
        assert chat.status_code == 503

        # Manual edit + re-render reuses the script and produces a new video.
        scenes = [{k: s[k] for k in ("heading", "narration", "visual_prompt", "on_screen_text")} for s in done["script"]["scenes"]]
        scenes[0]["narration"] = "An edited opening line for the video."
        assert (await c.put(f"/api/v1/projects/{project_id}/scenes", json={"scenes": scenes}, headers=headers)).status_code == 200
        rerender = await c.post(f"/api/v1/projects/{project_id}/generate", json={"mode": "rerender"}, headers=headers)
        assert rerender.status_code == 202
        redone = await _wait_for_job(c, project_id, headers)
        assert redone["status"] == "completed"
        assert redone["job"]["steps"]["script"]["status"] == "skipped"
        assert redone["script"]["scenes"][0]["narration"] == "An edited opening line for the video."
        assert redone["stale"] is False
        assert len(redone["history"]) == 2

        assert (await c.delete(f"/api/v1/projects/{project_id}", headers=headers)).status_code == 204
        assert (await c.get(f"/api/v1/projects/{project_id}", headers=headers)).status_code == 404
        assert not (media.MEDIA_DIR / project_id).exists()
