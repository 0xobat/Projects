#!/usr/bin/env bash
# test-x402-buy verification
set -euo pipefail

echo "test-x402-buy: checking entry point exists..."
if [[ ! -f "index.ts" ]]; then
  echo "ERROR: index.ts not found"
  exit 1
fi

echo "test-x402-buy: verification passed"
