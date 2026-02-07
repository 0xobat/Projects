#!/usr/bin/env bash
# val project verification: lint + build
set -euo pipefail
cd "$(dirname "$0")/.."

echo "val: running lint..."
pnpm lint
echo "val: lint passed"

echo "val: running build..."
pnpm build
echo "val: build passed"

echo "val: all checks passed"
