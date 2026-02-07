#!/usr/bin/env bash
# crypto umbrella init: delegates to subproject init scripts
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRYPTO_DIR="$(dirname "$SCRIPT_DIR")"

subprojects=("ai-bot-alchemy" "test-x402/test-x402-buy" "test-x402/test-x402-sell")

for sub in "${subprojects[@]}"; do
  init_script="$CRYPTO_DIR/$sub/harness/init.sh"
  if [[ -f "$init_script" ]]; then
    echo "── crypto/$sub: init ──"
    (cd "$CRYPTO_DIR/$sub" && bash harness/init.sh)
    echo ""
  fi
done

echo "crypto: all subprojects initialized"
