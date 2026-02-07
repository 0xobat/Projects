#!/usr/bin/env bash
# crypto umbrella verify: delegates to subproject verify scripts
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRYPTO_DIR="$(dirname "$SCRIPT_DIR")"

subprojects=("ai-bot-alchemy" "test-x402/test-x402-buy" "test-x402/test-x402-sell")

passed=0
failed=0

for sub in "${subprojects[@]}"; do
  verify_script="$CRYPTO_DIR/$sub/harness/verify.sh"
  if [[ -f "$verify_script" ]]; then
    echo "── crypto/$sub: verify ──"
    if (cd "$CRYPTO_DIR/$sub" && bash harness/verify.sh); then
      passed=$((passed + 1))
    else
      failed=$((failed + 1))
    fi
    echo ""
  fi
done

echo "crypto: $passed passed, $failed failed"
[[ $failed -eq 0 ]]
