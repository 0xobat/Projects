#!/usr/bin/env bash
# Master verify: discovers and runs <project>/harness/verify.sh
# Usage: ./harness/verify.sh [project-name]
# If no project name given, runs verify for all discovered projects.
# Reports pass/fail per project and exits non-zero if any fail.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="$(dirname "$SCRIPT_DIR")"

passed=0
failed=0
skipped=0
results=()

run_verify() {
  local project="$1"
  local verify_script="$PROJECTS_DIR/$project/harness/verify.sh"

  if [[ ! -f "$verify_script" ]]; then
    echo "⚠  $project: no harness/verify.sh found — skipping"
    skipped=$((skipped + 1))
    results+=("SKIP  $project")
    return 0
  fi

  echo "── Verifying: $project ──"
  if (cd "$PROJECTS_DIR/$project" && bash harness/verify.sh); then
    echo "✓  $project PASSED"
    passed=$((passed + 1))
    results+=("PASS  $project")
  else
    echo "✗  $project FAILED"
    failed=$((failed + 1))
    results+=("FAIL  $project")
  fi
  echo ""
}

if [[ $# -ge 1 ]]; then
  run_verify "$1"
else
  for dir in "$PROJECTS_DIR"/*/; do
    project="$(basename "$dir")"
    [[ "$project" == "harness" ]] && continue
    [[ "$project" == ".git" ]] && continue
    if [[ -f "$dir/harness/verify.sh" ]]; then
      run_verify "$project"
    fi
  done
fi

# Summary
echo "═══ Verification Summary ═══"
for r in "${results[@]:-}"; do
  [[ -n "$r" ]] && echo "  $r"
done
echo ""
echo "Passed: $passed  Failed: $failed  Skipped: $skipped"

[[ $failed -eq 0 ]]
