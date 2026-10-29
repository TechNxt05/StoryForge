"""Settings API tests: provider status never leaks secrets; only admins can set keys."""

import os

import httpx
import pytest
from apps.api.src.main import app


async def _token(c: httpx.AsyncClient, email: str) -> dict:
    res = await c.post("/api/v1/auth/signup", json={"email": email, "password": "password123", "full_name": "X"})
    assert res.status_code == 201, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.mark.asyncio
async def test_provider_status_has_no_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "gsk_super_secret_value")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        headers = await _token(c, "settings-reader@test.dev")
        res = await c.get("/api/v1/settings/providers", headers=headers)
        assert res.status_code == 200
        assert "gsk_super_secret_value" not in res.text
        groq = next(p for p in res.json()["providers"] if p["id"] == "groq")
        assert groq["configured"] is True
        assert res.json()["can_edit"] is False


@pytest.mark.asyncio
async def test_only_admin_can_set_keys(monkeypatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        creator = await _token(c, "creator-keys@test.dev")
        payload = {"env": "HF_TOKEN", "value": "hf_test_token_value"}
        assert (await c.post("/api/v1/settings/keys", json=payload, headers=creator)).status_code == 403

        admin = await _token(c, "admin@test.dev")  # listed in ADMIN_EMAILS by conftest
        assert (await c.post("/api/v1/settings/keys", json={"env": "PATH", "value": "x" * 10}, headers=admin)).status_code == 400
        res = await c.post("/api/v1/settings/keys", json=payload, headers=admin)
        assert res.status_code == 200
        assert os.environ["HF_TOKEN"] == "hf_test_token_value"


@pytest.mark.asyncio
async def test_workspace_counts_real_projects() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        headers = await _token(c, "workspace-owner@test.dev")
        project = {"title": "T", "topic": "Some topic", "auto_generate": False}
        await c.post("/api/v1/projects", json=project, headers=headers)
        data = (await c.get("/api/v1/settings/workspace", headers=headers)).json()
        assert data["projects_total"] == 1
        assert data["projects_by_status"] == {"draft": 1}
