# StoryForge AI

Type a topic → get a narrated, captioned short video (MP4). StoryForge researches the topic on
Wikipedia, writes a scene-by-scene script with an LLM, generates an image for every scene,
narrates it with a neural voice, and renders a Ken Burns-style video with burned-in captions.

Everything runs on **free** services and works with **zero API keys** — free keys just make it
faster and better.

## How it works

```
Next.js (Vercel)  ──REST──►  FastAPI (Render, Docker)
  Studio UI                    ├─ auth (JWT, PBKDF2)            apps/api/src/auth.py
  polls job progress           ├─ projects / jobs / chat edits   apps/api/src/routes/, jobs.py
                               └─ pipeline (asyncio background)  runtime/pipeline.py
                                   1. research   Wikipedia API (free, no key)
                                   2. script     runtime/llm.py: Gemini → Groq → OpenRouter → Pollinations
                                   3. images     runtime/media.py: Cloudflare FLUX → HF FLUX → Pollinations → local card
                                   4. voice      edge-tts neural voices → gTTS → silence (with word timings)
                                   5. render     ffmpeg: pan/zoom per scene + ASS captions, concat
                                   6. publish    Cloudinary (if configured) or /media on the API
Postgres (Neon/Supabase free) or SQLite stores users, projects and progress.
```

Every step has a fallback, so a run always ends in a playable MP4. The Studio shows which
provider handled each step.

## Free providers

| Purpose | Provider | Key | Notes |
|---|---|---|---|
| Script | Google Gemini (`gemini-2.5-flash`) | `GEMINI_API_KEY` | Best quality; free tier at [AI Studio](https://aistudio.google.com/apikey) |
| Script | Groq (`openai/gpt-oss-120b`) | `GROQ_API_KEY` | Very fast; [console.groq.com](https://console.groq.com/keys) |
| Script | OpenRouter (`openrouter/free`) | `OPENROUTER_API_KEY` | ~50 free requests/day |
| Script + images | Pollinations | none (optional `POLLINATIONS_API_KEY`) | Anonymous: ~1 image per 45 s per IP, small watermark |
| Images | Cloudflare Workers AI FLUX schnell | `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` | 10k free neurons/day — fastest free image option |
| Images | Hugging Face FLUX.1-schnell | `HF_TOKEN` | Small monthly free credit |
| Voice | Microsoft Edge neural voices (edge-tts) | none | Natural voices, word timings for captions |
| Storage | Cloudinary | `CLOUDINARY_URL` | Keeps videos after restarts (recommended) |

All model names are overridable (`GEMINI_MODEL`, `GROQ_MODEL`, …) because free rosters change.
See [.env.example](.env.example) for every setting.

## Run locally

Requirements: Python 3.11+, Node 20+. ffmpeg is optional (the `imageio-ffmpeg` package bundles one).

```bash
# API
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
JWT_SECRET_KEY=dev uvicorn apps.api.src.main:app --reload --port 8000

# Web (new terminal)
cd apps/web
npm install
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
npm run dev                                        # http://localhost:3000
```

Tests (offline, real ffmpeg render): `pip install pytest pytest-asyncio && python -m pytest tests -q`

## Deploy for free

### API on Render
1. New → **Web Service** → connect the repo → Runtime **Docker** (uses the root `Dockerfile`) → Instance type **Free**.
2. Environment variables:
   - `JWT_SECRET_KEY` — a long random string (required)
   - `DATABASE_URL` — a free [Neon](https://neon.tech) Postgres URL. Without it, SQLite is used and **all accounts are wiped on every restart**.
   - `CORS_ORIGINS` — your Vercel URL, e.g. `https://storyforge.vercel.app`
   - `ADMIN_EMAILS` — your email (lets you set keys from the Settings page)
   - Any free AI keys from the table above, and Cloudinary keys.
3. Note the service URL, e.g. `https://storyforge-api.onrender.com`.

### Web on Vercel
1. Import the repo, set **Root Directory** to `apps/web`.
2. Environment variable `NEXT_PUBLIC_API_URL` = your Render URL. Deploy.

### Free-tier realities
- Render free instances **sleep after 15 min idle**; the first request takes ~30–60 s (the header shows "Waking server…").
  A generation in progress is lost if the instance restarts — the project is marked failed and can be re-run.
- Render free has ~0.1 CPU: a 45 s video renders in roughly 1–3 minutes at the default 576p (`RENDER_SHORT_SIDE`).
- Without Cloudinary, videos are stored on the instance disk and vanish on restart.
- Without image keys, Pollinations' anonymous limit means ~45 s per scene image.

## Repository layout

| Path | What it is |
|---|---|
| `apps/web` | Next.js 15 studio (projects, studio editor, assets, analytics, settings) |
| `apps/api` | FastAPI app: auth, projects, background jobs, settings, assets |
| `runtime/llm.py`, `media.py`, `pipeline.py` | The generation pipeline used by the API |
| `runtime/capabilities`, `planner`, `scheduler`, … | Earlier "agent runtime" experiments exposed under `/api/v1/runtime`; most are simulated and not used by the product |
| `providers/` | Provider adapters (Gemini/Groq/OpenRouter delegate to `runtime/llm.py`; others are stubs) |
| `tests/` | pytest suite (runs offline) |
