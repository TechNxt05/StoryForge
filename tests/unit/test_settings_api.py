"""Settings API Gateway Integration Tests."""

import httpx
import pytest
from apps.api.src.main import app


@pytest.mark.asyncio
async def test_get_and_update_api_keys() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Get masked keys
        res = await client.get("/api/v1/settings/keys")
        assert res.status_code == 200
        keys = res.json()
        assert "gemini" in keys

        # Update key
        update_payload = {"provider": "openai", "api_key": "sk-test-secret-key-12345"}
        post_res = await client.post("/api/v1/settings/keys", json=update_payload)
        assert post_res.status_code == 200
        assert post_res.json()["status"] == "success"


@pytest.mark.asyncio
async def test_workspace_details_and_members() -> None:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Get workspace
        res = await client.get("/api/v1/settings/workspace")
        assert res.status_code == 200
        data = res.json()
        assert data["tier"] == "pro_agency"
        assert len(data["members"]) >= 2

        # Add member
        add_payload = {"name": "New Designer", "email": "designer@storyforge.ai", "role": "editor"}
        post_res = await client.post("/api/v1/settings/workspace/members", json=add_payload)
        assert post_res.status_code == 201
        assert post_res.json()["member"]["name"] == "New Designer"
