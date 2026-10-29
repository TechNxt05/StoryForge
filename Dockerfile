# StoryForge AI API (FastAPI + ffmpeg video pipeline). Used by Render (Docker runtime).

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MEDIA_DIR=/app/media

# ffmpeg renders the videos; DejaVu fonts are used for the burned-in captions.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY runtime/ ./runtime/
COPY apps/api/ ./apps/api/
COPY apps/worker/ ./apps/worker/
COPY providers/ ./providers/
COPY content-packs/ ./content-packs/

RUN mkdir -p /app/media

EXPOSE 8000

# Render injects $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn apps.api.src.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
