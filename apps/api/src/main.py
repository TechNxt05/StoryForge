"""StoryForge FastAPI Application Entry Point."""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

# Add monorepo root and subpackages to Python module search path
ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "content-packs") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "content-packs"))
if str(ROOT_DIR / "content-packs" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "content-packs" / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import runtime.capabilities  # Auto-register all 15+ capabilities
from runtime import CapabilityRegistry
from runtime.providers import ProviderFallbackEngine
from runtime.memory import VectorRAGMemoryStore
from apps.worker.src import DistributedWorkerCluster
from pack_engine import ContentPackEngine
from packages.observability.src.python_telemetry import metrics_collector

# Provider Adapters
from providers.gemini.adapter import GeminiAdapter
from providers.groq.adapter import GroqAdapter
from providers.openrouter.adapter import OpenRouterAdapter
from providers.pollinations.adapter import PollinationsAdapter
from providers.flux.adapter import FluxAdapter
from providers.veo.adapter import VeoAdapter
from providers.cloudinary.adapter import CloudinaryAdapter
from providers.voiceai.adapter import VoiceAIAdapter

# System Singletons
fallback_engine = ProviderFallbackEngine()
vector_rag_memory = VectorRAGMemoryStore()
worker_cluster = DistributedWorkerCluster()
content_pack_engine = ContentPackEngine()

# Register all provider adapters into the fallback engine
fallback_engine.register_provider("llm", "gemini", GeminiAdapter())
fallback_engine.register_provider("llm", "groq", GroqAdapter())
fallback_engine.register_provider("llm", "openrouter", OpenRouterAdapter())
fallback_engine.register_provider("image", "pollinations", PollinationsAdapter())
fallback_engine.register_provider("image", "flux", FluxAdapter())
fallback_engine.register_provider("video", "veo", VeoAdapter())
fallback_engine.register_provider("voice", "voiceai", VoiceAIAdapter())
fallback_engine.register_provider("storage", "cloudinary", CloudinaryAdapter())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup & Shutdown Lifecycle hook for StoryForge Gateway."""
    # Auto-create database tables (SQLite fallback or PostgreSQL)
    from apps.api.src.database.postgres import Base, engine, AsyncSessionLocal, User as DBUser, Workspace as DBWorkspace
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[StoryForge API] Database tables initialized.")

    try:
        async with AsyncSessionLocal() as session:
            u = await session.get(DBUser, "user-default")
            if not u:
                u = DBUser(id="user-default", email="guest@storyforge.ai", full_name="Guest Creator")
                session.add(u)
            w = await session.get(DBWorkspace, "ws-default")
            if not w:
                w = DBWorkspace(id="ws-default", name="Default Workspace", slug="ws-default", owner_id="user-default")
                session.add(w)
            await session.commit()
        print("[StoryForge API] Default user and workspace seeded.")
    except Exception as e:
        print(f"[StoryForge API] DB Seeding note: {e}")

    metrics_collector.increment("gateway_startup_total", 1.0)
    print(f"[StoryForge API] Registered Capabilities: {list(CapabilityRegistry.list_capabilities().keys())}")
    print(f"[StoryForge API] Loaded Content Packs: {len(content_pack_engine.list_packs())}")
    print(f"[StoryForge API] Provider Fallback Engine: {sum(len(v) for v in fallback_engine._providers.values())} adapters registered")
    yield
    print("[StoryForge API] Gateway shutdown complete.")


app = FastAPI(
    title="StoryForge AI API Gateway",
    description="Backend API Gateway and Runtime Router for StoryForge AI Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
from .routes.auth import router as auth_router
from .routes.projects import router as projects_router
from .routes.runtime import router as runtime_router
from .routes.settings import router as settings_router

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(runtime_router)
app.include_router(settings_router)


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Full system health check endpoint."""
    return {
        "status": "ok",
        "service": "storyforge-api-gateway",
        "registered_capabilities_count": len(CapabilityRegistry.list_capabilities()),
        "content_packs_count": len(content_pack_engine.list_packs()),
        "worker_cluster_nodes": len(worker_cluster.nodes),
        "provider_adapters_registered": sum(len(v) for v in fallback_engine._providers.values()),
    }
