#!/usr/bin/env bash
# Master init: discovers and runs <project>/harness/init.sh
# Usage: ./harness/init.sh [project-name]
# If no project name given, runs init for all discovered projects.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="$(dirname "$SCRIPT_DIR")"

run_init() {
  local project="$1"
  local init_script="$PROJECTS_DIR/$project/harness/init.sh"

  if [[ ! -f "$init_script" ]]; then
    echo "⚠  $project: no harness/init.sh found — skipping"
    return 0
  fi

  echo "── Initializing: $project ──"
  (cd "$PROJECTS_DIR/$project" && bash harness/init.sh)
  echo "✓  $project initialized"
  echo ""
}

if [[ $# -ge 1 ]]; then
  # Run for a specific project
  run_init "$1"
else
  # Discover all projects with harness/init.sh
  found=0
  for dir in "$PROJECTS_DIR"/*/; do
    project="$(basename "$dir")"
    [[ "$project" == "harness" ]] && continue
    [[ "$project" == ".git" ]] && continue
    if [[ -f "$dir/harness/init.sh" ]]; then
      run_init "$project"
      found=$((found + 1))
    fi
  done

  if [[ $found -eq 0 ]]; then
    echo "No projects with harness/init.sh found."
    exit 1
  fi

  echo "═══ All $found projects initialized ═══"
fi
