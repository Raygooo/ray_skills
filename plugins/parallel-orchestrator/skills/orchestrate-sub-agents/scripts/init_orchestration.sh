#!/usr/bin/env bash
# init_orchestration.sh — scaffold docs/ layout for parallel-sub-agent orchestration.
#
# Usage:
#   ./init_orchestration.sh [--project-root PATH] [--slice-count N]
#
# Creates:
#   docs/AGENT_HANDBOOK.md
#   docs/TASK_TRACKER.md
#   docs/SLICES/00-overview.md
#   docs/SLICES/01-<placeholder>.md .. docs/SLICES/<N>-<placeholder>.md
#
# Copies templates from the parent skill's assets/ directory. Idempotent:
# files that already exist are left alone (prints a warning for each).

set -euo pipefail

PROJECT_ROOT="$PWD"
SLICE_COUNT=3

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root) PROJECT_ROOT="$2"; shift 2 ;;
        --slice-count)  SLICE_COUNT="$2";  shift 2 ;;
        -h|--help)
            sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "unknown flag: $1" >&2
            exit 1
            ;;
    esac
done

# Resolve assets dir (sibling to scripts/ inside the skill).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"

if [[ ! -d "$ASSETS_DIR" ]]; then
    echo "assets dir not found: $ASSETS_DIR" >&2
    exit 1
fi

DOCS_DIR="$PROJECT_ROOT/docs"
SLICES_DIR="$DOCS_DIR/SLICES"
mkdir -p "$SLICES_DIR"

install_template() {
    local src="$1" dst="$2"
    if [[ -e "$dst" ]]; then
        echo "skip (exists): $dst"
        return
    fi
    cp "$src" "$dst"
    echo "wrote: $dst"
}

install_template "$ASSETS_DIR/AGENT_HANDBOOK.md.template" "$DOCS_DIR/AGENT_HANDBOOK.md"
install_template "$ASSETS_DIR/TASK_TRACKER.md.template"   "$DOCS_DIR/TASK_TRACKER.md"
install_template "$ASSETS_DIR/slices-overview.md.template" "$SLICES_DIR/00-overview.md"

for i in $(seq 1 "$SLICE_COUNT"); do
    nn=$(printf "%02d" "$i")
    install_template "$ASSETS_DIR/slice-brief.md.template" "$SLICES_DIR/${nn}-placeholder.md"
done

echo
echo "Orchestration docs scaffolded under $DOCS_DIR"
echo "Next:"
echo "  1. Edit docs/SLICES/00-overview.md and fill the slice table."
echo "  2. Rename each docs/SLICES/NN-placeholder.md and fill in the brief."
echo "  3. Populate docs/TASK_TRACKER.md with each slice's tasks."
echo "  4. When ready to dispatch, use scripts/setup_worktrees.sh (sibling)."
