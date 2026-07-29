"""Content Packs Engine Unit Tests."""

import sys
from pathlib import Path

# Add content-packs directory to Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "content-packs" / "src"))

from pack_engine import ContentPackEngine, ContentPack


def test_content_pack_engine_built_in_packs() -> None:
    engine = ContentPackEngine()
    packs = engine.list_packs()

    assert len(packs) >= 5
    pack_names = [p["name"] for p in packs]
    assert "cricket" in pack_names
    assert "history" in pack_names
    assert "technology" in pack_names
    assert "travel" in pack_names
    assert "chess" in pack_names


def test_content_pack_enrichment() -> None:
    engine = ContentPackEngine()
    tech_pack = engine.get_pack("technology")

    enriched = tech_pack.enrich_prompt("Quantum computing breakthrough")
    assert "Quantum computing breakthrough" in enriched
    assert "futuristic_neon" in enriched


def test_content_pack_fallback() -> None:
    engine = ContentPackEngine()
    unknown_pack = engine.get_pack("unknown_domain_xyz")

    assert unknown_pack.name == "history"
