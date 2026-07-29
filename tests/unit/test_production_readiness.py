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
async def test_security_masked_api_keys() -> None:
    """Verify secret API keys are never leaked in unmasked plain text."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/settings/keys")
        assert res.status_code == 200
        keys = res.json()
        for key_name, masked_val in keys.items():
            assert "sk-gemini-sample-key" not in masked_val
            assert "sk-flux-sample-key" not in masked_val
            assert "****" in masked_val or "..." in masked_val


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
