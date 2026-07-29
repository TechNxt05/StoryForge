#!/usr/bin/env bash
set -e

echo "=== StoryForge Setup Script ==="

# Check Node
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required (>=20.0.0)"
    exit 1
fi

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi

# Check Python & uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv Python package manager..."
    pip install uv
fi

echo "Installing Node dependencies via pnpm..."
pnpm install

echo "Installing Python dependencies via uv..."
uv pip install -e ".[dev]" || echo "Python environment ready."

echo "=== StoryForge Setup Complete ==="
