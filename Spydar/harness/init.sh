#!/usr/bin/env bash
# Spydar project init: verify build tools are available
set -euo pipefail

echo "Spydar: checking for cmake..."
if ! command -v cmake &>/dev/null; then
  echo "ERROR: cmake is not installed. Install it with: brew install cmake"
  exit 1
fi

echo "Spydar: checking for arm-none-eabi-gcc (Pico SDK toolchain)..."
if ! command -v arm-none-eabi-gcc &>/dev/null; then
  echo "WARNING: arm-none-eabi-gcc not found — cross-compilation will not work"
  echo "Install with: brew install --cask gcc-arm-embedded"
fi

echo "Spydar: init complete"
