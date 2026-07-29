#!/usr/bin/env bash
set -e

echo "=== Cleaning StoryForge Workspace Cache & Artifacts ==="

rm -rf node_modules
rm -rf .turbo
rm -rf .next
rm -rf apps/web/.next
rm -rf **/__pycache__
rm -rf **/*.egg-info
rm -rf .pytest_cache
rm -rf .ruff_cache

echo "=== Workspace Reset Complete ==="
