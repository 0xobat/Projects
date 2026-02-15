#!/usr/bin/env bash
# test-x402-sell verification
set -euo pipefail

echo "test-x402-sell: checking Python syntax..."
uv run python -c "import py_compile; py_compile.compile('main.py', doraise=True)"

echo "test-x402-sell: verification passed"
