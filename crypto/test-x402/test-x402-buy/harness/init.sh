#!/usr/bin/env bash
# test-x402-buy init: install pnpm deps
set -euo pipefail

echo "test-x402-buy: checking for pnpm..."
if ! command -v pnpm &>/dev/null; then
  echo "ERROR: pnpm is not installed. Install it with: npm install -g pnpm"
  exit 1
fi

echo "test-x402-buy: installing dependencies..."
pnpm install

echo "test-x402-buy: init complete"
