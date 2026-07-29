"""Fact Verification Capability Unit Tests."""

import pytest
from runtime.capabilities import FactVerificationCapability, VerificationArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_fact_verification_execution() -> None:
    cap = FactVerificationCapability()
    claims = ["Quantum computing uses qubits.", "Qubits exist in superposition."]
    result = await cap.execute(claims=claims)

    assert result["claims_checked"] == 2
    assert len(result["verified_claims"]) == 2
    assert result["overall_confidence_score"] > 0.8
    assert result["artifact_type"] == "verification_report"


@pytest.mark.asyncio
async def test_fact_verification_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("fact_verification")
    assert resolved.name == "fact_verification"

    result = await resolved.execute(claims=["Python 3.12 is used in StoryForge."])
    assert result["claims_checked"] == 1
    assert result["verified_claims"][0]["is_verified"] is True
