#!/usr/bin/env bash
# Eth-Bot project init: install deps and verify environment
set -euo pipefail

echo "Eth-Bot: checking for pnpm..."
if ! command -v pnpm &>/dev/null; then
  echo "ERROR: pnpm is not installed. Install it with: npm install -g pnpm"
  exit 1
fi

echo "Eth-Bot: installing dependencies..."
pnpm install

echo "Eth-Bot: checking for tsx..."
if ! pnpm exec tsx --version &>/dev/null; then
  echo "ERROR: tsx not available after install"
  exit 1
fi

echo "Eth-Bot: init complete"
