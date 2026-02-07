#!/usr/bin/env bash
# Spydar project verification: check source files and build config
set -euo pipefail

echo "Spydar: checking CMakeLists.txt exists..."
if [[ ! -f "pico_src/CMakeLists.txt" ]]; then
  echo "ERROR: pico_src/CMakeLists.txt not found"
  exit 1
fi

echo "Spydar: checking source files exist..."
src_count=$(find pico_src/sensors -name "*.c" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$src_count" -eq 0 ]]; then
  echo "ERROR: no C source files found in pico_src/sensors/"
  exit 1
fi
echo "Spydar: found $src_count source files"

echo "Spydar: verification passed"
