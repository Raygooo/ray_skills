#!/usr/bin/env bash
# setup_worktrees.sh — pre-create N git worktrees for parallel sub-agents.
#
# Use when Claude Code's Agent tool `isolation: "worktree"` option fails
# (no WorktreeCreate hook configured). The primary session calls this
# first, then dispatches agents pointing at each worktree.
#
# Usage:
#   ./setup_worktrees.sh <pairs-file>
#   ./setup_worktrees.sh --pair worktree_name:branch_name [--pair ...]
#   echo -e "ui:slice-01-ui\ndata:slice-04-data" | ./setup_worktrees.sh -
#
# Pairs file format: one `worktree_name:branch_name` per line.
#
# Creates worktrees under .claude/worktrees/<worktree_name>/ by default,
# each on a new branch from `main`.
#
# Idempotent: skips worktrees that already exist.

set -euo pipefail

BASE_DIR=".claude/worktrees"
BRANCH_FROM="main"
PAIRS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --base-dir)     BASE_DIR="$2";     shift 2 ;;
        --branch-from)  BRANCH_FROM="$2";  shift 2 ;;
        --pair)         PAIRS+=("$2");     shift 2 ;;
        -h|--help)
            sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        -)
            while IFS= read -r line; do
                line="${line%% *}"
                [[ -n "$line" ]] && PAIRS+=("$line")
            done
            shift
            ;;
        *)
            # assume it's a pairs file path
            while IFS= read -r line; do
                line="${line%% *}"
                [[ -n "$line" ]] && PAIRS+=("$line")
            done < "$1"
            shift
            ;;
    esac
done

if [[ ${#PAIRS[@]} -eq 0 ]]; then
    echo "no pairs given" >&2
    exit 1
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "not inside a git repository" >&2
    exit 1
fi

mkdir -p "$BASE_DIR"

for pair in "${PAIRS[@]}"; do
    wt_name="${pair%%:*}"
    branch="${pair##*:}"
    path="$BASE_DIR/$wt_name"

    if [[ "$wt_name" == "$branch" ]]; then
        echo "bad pair (use wt_name:branch_name): $pair" >&2
        continue
    fi

    if [[ -d "$path" ]]; then
        echo "skip (exists): $path"
        continue
    fi

    echo "creating worktree $path on branch $branch from $BRANCH_FROM"
    git worktree add -b "$branch" "$path" "$BRANCH_FROM"
done

echo
echo "Worktrees:"
git worktree list
