#!/usr/bin/env bash
# test-x402-sell init: install Python deps with UV
set -euo pipefail

echo "test-x402-sell: checking for uv..."
if ! command -v uv &>/dev/null; then
  echo "ERROR: uv is not installed. Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi

echo "test-x402-sell: syncing dependencies..."
uv sync

echo "test-x402-sell: init complete"
