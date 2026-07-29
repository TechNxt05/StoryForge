#!/usr/bin/env bash
set -e

echo "=== Bootstrapping StoryForge Environment ==="
./scripts/setup.sh
cp -n .env.example .env || true
cp -n .env.local.example .env.local || true
echo "=== StoryForge Ready for Development ==="
