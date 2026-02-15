#!/usr/bin/env bash
# Eth-Bot project verification
set -euo pipefail

echo "Eth-Bot: running TypeScript type-check..."
pnpm exec tsc --noEmit

echo "Eth-Bot: verifying entry point exists..."
if [[ ! -f "open_router.ts" ]]; then
  echo "ERROR: open_router.ts entry point not found"
  exit 1
fi

echo "Eth-Bot: verification passed"
