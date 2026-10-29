"""StoryForge FastAPI Application Entry Point."""

import logging
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

# Add monorepo root and subpackages to Python module search path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "content-packs" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "content-packs" / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import runtime.capabilities  # noqa: F401  registers capabilities for the runtime router
from runtime import CapabilityRegistry, llm, media
from runtime.providers import ProviderFallbackEngine

from providers.gemini.adapter import GeminiAdapter
from providers.groq.adapter import GroqAdapter
from providers.openrouter.adapter import OpenRouterAdapter
from providers.pollinations.adapter import PollinationsAdapter
from providers.cloudinary.adapter import CloudinaryAdapter

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("storyforge.api")

# Provider registry used by runtime capabilities (e.g. vision_analyzer).
fallback_engine = ProviderFallbackEngine()
fallback_engine.register_provider("llm", "gemini", GeminiAdapter())
fallback_engine.register_provider("llm", "groq", GroqAdapter())
fallback_engine.register_provider("llm", "openrouter", OpenRouterAdapter())
fallback_engine.register_provider("image", "pollinations", PollinationsAdapter())
fallback_engine.register_provider("storage", "cloudinary", CloudinaryAdapter())

media.MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup & Shutdown Lifecycle hook for StoryForge Gateway."""
    from .database.postgres import Base, engine
    from . import jobs

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    recovered = await jobs.recover_interrupted_jobs()
    if recovered:
        logger.info("Marked %d interrupted generation(s) as failed", recovered)
    logger.info("LLM providers in order: %s", llm.configured_providers())
    logger.info("Storage: %s, media dir: %s", "cloudinary" if media.cloudinary_configured() else "local", media.MEDIA_DIR)
    yield


app = FastAPI(
    title="StoryForge AI API",
    description="Turns a topic into a narrated, captioned short video using free AI providers.",
    version="2.0.0",
    lifespan=lifespan,
)

# Auth uses bearer tokens (not cookies), so credentials are not needed for CORS.
_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX") or None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routes.auth import router as auth_router
from .routes.projects import router as projects_router
from .routes.runtime import router as runtime_router
from .routes.settings import router as settings_router
from .routes.assets import router as assets_router
from .routes.meta import router as meta_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(runtime_router)
app.include_router(settings_router)
app.include_router(assets_router)
app.include_router(meta_router)

# Generated media (used when Cloudinary is not configured).
app.mount("/media", StaticFiles(directory=media.MEDIA_DIR), name="media")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "storyforge-api", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Liveness check; also reports which free providers are active."""
    return {
        "status": "ok",
        "service": "storyforge-api",
        "llm_providers": llm.configured_providers(),
        "storage": "cloudinary" if media.cloudinary_configured() else "local",
        "registered_capabilities_count": len(CapabilityRegistry.list_capabilities()),
    }
