# StoryForge AI

> **AI Agentic Storytelling Platform Monorepo**

StoryForge is a production-grade AI platform designed to automate documentary-quality short-form video creation—from raw topic research and scriptwriting to voice synthesis, image/video generation, and video composition.

---

## 🌟 StoryForge Architecture

StoryForge is architected as an extensible, multi-tenant monorepo decoupling runtime engine interfaces from UI, backend services, worker pipelines, and third-party AI provider adapters.

```
StoryForge/
├── apps/
│   ├── web/           (Next.js 15, React 19, TailwindCSS v4, Zustand, TanStack Query)
│   ├── api/           (FastAPI, Python 3.12, Pydantic v2)
│   ├── worker/        (Celery / Background Async Processing Engine)
│   └── docs/          (Platform Documentation Hub)
├── runtime/           (Core AI Orchestration Engine & Abstract Interfaces)
│   ├── planner/       (Agent Planning & Reasoning Interfaces)
│   ├── execution/     (Workflow Execution Engine)
│   ├── gateway/       (Runtime API & Protocol Gateway)
│   ├── memory/        (Episodic & Vector Memory Interfaces)
│   ├── scheduler/     (Task Scheduling & Queue Management)
│   ├── registry/      (Capability & Agent Registries)
│   ├── events/        (Event Bus & Pub/Sub Specs)
│   ├── sdk/           (Developer SDK Contract)
│   └── shared/        (Runtime Utilities & Base Types)
├── packages/          (Shared TypeScript & Python Packages)
│   ├── ui/            (Design System & Core UI Components)
│   ├── database/      (ORM, Schemas & Connections)
│   ├── types/         (TypeScript Types & Contracts)
│   ├── config/        (Shared Constants & Configuration)
│   ├── auth/          (Authentication & Authorization)
│   ├── media/         (Media Assembly & Processing Helpers)
│   ├── observability/ (Tracing, Metrics & Structured Logging)
│   ├── utils/         (Utility Functions)
│   └── ai/            (Prompt Templates & Common AI Schemas)
├── providers/         (Provider Adapter Skeletons)
│   ├── openrouter/    (LLM Gateway Adapter)
│   ├── gemini/        (Google Gemini Adapter)
│   ├── veo/           (Google Veo Video Gen Adapter)
│   ├── flux/          (FLUX Image Gen Adapter)
│   ├── nanobanana/    (NanoBanana Adapter)
│   ├── kokoro/        (Kokoro TTS Adapter)
│   ├── voicebox/      (VoiceBox Audio Adapter)
│   └── cloudinary/    (Cloudinary Storage Adapter)
├── content-packs/     (Domain-Specific Content Kits)
│   ├── cricket/
│   ├── travel/
│   ├── history/
│   ├── technology/
│   └── chess/
├── docker/            (Multi-stage Dockerfiles & Compose Specs)
├── scripts/           (Dev, Build, Test & Lint Executables)
└── tests/             (Unit, Integration & End-to-End Test Suites)
```

---

## 🛠 Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, TailwindCSS v4, shadcn/ui, Zustand, TanStack Query
- **Backend & Workers**: FastAPI, Python 3.12, `uv`, Pydantic v2, Celery / Asyncio
- **Infrastructure & Containerization**: Docker, Docker Compose, Turborepo, pnpm
- **Databases & Vector Search**: PostgreSQL, MongoDB, Redis, Qdrant
- **Storage**: Cloudinary / S3 Compatible Object Storage

---

## 🚀 Development Quickstart

### Prerequisites
- Node.js >= 20.0.0
- `pnpm` >= 9.0.0
- Python >= 3.12 & `uv` package manager
- Docker & Docker Compose

### Commands

```bash
# Install Node dependencies across workspace
pnpm install

# Run dev environment across all apps
./scripts/dev.sh

# Run linting across repository
./scripts/lint.sh

# Run type checks across web & Python services
./scripts/build.sh

# Execute unit and integration tests
./scripts/test.sh
```

---

## 🗺 Platform Roadmap

- [x] **P00: Monorepo Foundation & Architecture Initialization**
- [ ] **P01: Authentication & User Management Systems**
- [ ] **P02: Core Database Architecture & Migrations**
- [ ] **P03: Runtime Engine & Execution Bus**
- [ ] **P04: AI Provider Adapters Implementation**
- [ ] **P05: Content Pack Orchestration Engine**
- [ ] **P06: Web Studio & Interactive Canvas UI**
- [ ] **P07: Automated Media Rendering & Composition Pipeline**

---

## 📄 License

StoryForge is proprietary software. All rights reserved.
