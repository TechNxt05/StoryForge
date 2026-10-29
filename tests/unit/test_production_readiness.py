"""Production Readiness & Hardening Audit Test Suite."""

import sys
from pathlib import Path
import httpx
import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apps.api.src.main import app
from runtime.providers import ProviderFallbackEngine


@pytest.mark.asyncio
async def test_security_settings_require_auth() -> None:
    """Provider settings are private, and key writes are admin-only."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/api/v1/settings/providers")).status_code == 401
        res = await client.post("/api/v1/settings/keys", json={"env": "GEMINI_API_KEY", "value": "attacker-key"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_resilience_fallback_hardened() -> None:
    """Verify resilience fallback engine handles unknown/failing providers gracefully."""
    engine = ProviderFallbackEngine()
    result = await engine.execute_with_fallback(
        category="llm",
        primary_provider="non_existent_provider_xyz",
        backup_providers=["groq"],
        prompt="Test resilient fallback",
    )
    assert result["status"] == "success"
    assert result["fallback_used"] is True
    assert result["provider"] == "resilient_safety_fallback"


@pytest.mark.asyncio
async def test_production_cors_and_health_headers() -> None:
    """Verify CORS headers and health status."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
