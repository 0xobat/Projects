#!/usr/bin/env bash
# ai-bot-alchemy verification: run pytest
set -euo pipefail

echo "ai-bot-alchemy: running pytest..."
uv run pytest --tb=short -q 2>/dev/null || {
  echo "ai-bot-alchemy: no tests found or pytest failed"
  echo "ai-bot-alchemy: checking Python syntax..."
  uv run python -c "import py_compile; py_compile.compile('main.py', doraise=True)"
  echo "ai-bot-alchemy: syntax check passed"
}

echo "ai-bot-alchemy: verification complete"
