#!/usr/bin/env bash
# val project init: install deps and verify environment
set -euo pipefail
cd "$(dirname "$0")/.."

echo "val: installing dependencies..."
pnpm install --frozen-lockfile 2>/dev/null || pnpm install
echo "val: init complete"
