"""Shared test setup: isolated SQLite DB + media dir, no network LLM calls, clean registries."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
for extra in (ROOT_DIR, ROOT_DIR / "content-packs" / "src"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

# Must be set before the API modules are imported (they read env at import time).
_TMP = Path(tempfile.mkdtemp(prefix="storyforge-tests-"))
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{(_TMP / 'test.db').as_posix()}"
os.environ["MEDIA_DIR"] = str(_TMP / "media")
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["ADMIN_EMAILS"] = "admin@test.dev"
# Keep the suite offline and deterministic: every LLM provider is disabled.
os.environ["LLM_DISABLED_PROVIDERS"] = "gemini,groq,openrouter,pollinations"
for key in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "POLLINATIONS_API_KEY", "HF_TOKEN",
            "CLOUDFLARE_API_TOKEN", "CLOUDINARY_CLOUD_NAME"):
    os.environ.pop(key, None)


def _create_tables() -> None:
    from sqlalchemy import create_engine
    from apps.api.src.database.postgres import Base

    engine = create_engine(f"sqlite:///{(_TMP / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    engine.dispose()


_create_tables()


@pytest.fixture(autouse=True)
def _restore_capability_registry():
    """Some tests clear the global registry; restore it so later tests can resolve capabilities."""
    from runtime.registry.store import CapabilityRegistry
    import runtime.capabilities  # noqa: F401  ensure built-ins are registered

    saved = dict(CapabilityRegistry._capabilities)
    yield
    CapabilityRegistry._capabilities.clear()
    CapabilityRegistry._capabilities.update(saved)


@pytest.fixture
def offline_media(monkeypatch):
    """Replace network image/voice providers with fast local ffmpeg fallbacks."""
    from runtime import media

    async def fake_image(prompt, aspect_ratio, seed, dest, status=None):
        dest.parent.mkdir(parents=True, exist_ok=True)
        w, h = media.dimensions(aspect_ratio)
        return media._title_card(prompt, w, h, seed, dest.with_suffix(".png"))

    async def fake_voice(text, voice, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        return media._silence(text, dest)

    monkeypatch.setattr(media, "generate_image", fake_image)
    monkeypatch.setattr(media, "synthesize_voice", fake_voice)
    return media
