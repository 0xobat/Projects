#!/usr/bin/env bash
# ai-bot-alchemy init: install Python deps with UV
set -euo pipefail

echo "ai-bot-alchemy: checking for uv..."
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "ai-bot-alchemy: syncing dependencies..."
uv sync

echo "ai-bot-alchemy: init complete"
