# Multi-stage Production Dockerfile for StoryForge AI Platform

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies (FFmpeg, git, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml ruff.toml Makefile ./
COPY packages/ ./packages/
COPY runtime/ ./runtime/
COPY apps/ ./apps/
COPY providers/ ./providers/
COPY content-packs/ ./content-packs/

# Install python dependencies
RUN pip install --no-cache-dir \
    fastapi uvicorn pydantic httpx \
    sqlalchemy aiosqlite asyncpg email-validator python-multipart

# Expose API Gateway port
EXPOSE 8000

# Default command runs FastAPI API Gateway
CMD ["uvicorn", "apps.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
