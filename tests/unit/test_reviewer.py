"""Quality Reviewer Capability Unit Tests."""

import pytest
from runtime.capabilities import QualityReviewerCapability, ReviewReportArtifact
from runtime import CapabilityRegistry


@pytest.mark.asyncio
async def test_reviewer_execution() -> None:
    cap = QualityReviewerCapability()
    result = await cap.execute(pass_threshold=0.85)

    assert result["overall_score"] >= 0.85
    assert result["passed"] is True
    assert "visual_coherence" in result["metrics"]
    assert len(result["recommendations"]) >= 2
    assert result["artifact_type"] == "quality_review_report"


@pytest.mark.asyncio
async def test_reviewer_high_threshold_fail() -> None:
    cap = QualityReviewerCapability()
    result = await cap.execute(pass_threshold=0.99)

    assert result["passed"] is False
    assert any("pacing" in rec for rec in result["recommendations"])


@pytest.mark.asyncio
async def test_reviewer_registry_resolution() -> None:
    resolved = CapabilityRegistry.get_capability("quality_reviewer")
    assert resolved.name == "quality_reviewer"
