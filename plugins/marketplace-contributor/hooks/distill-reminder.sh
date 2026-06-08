#!/usr/bin/env bash
# Stop hook: gently nudge to distill a reusable workflow into a skill.
#
# Implements the "self-evolutionary" idea — the marketplace reminds you to
# capture a workflow as a skill — using the automation-hook lesson from LLM
# Wiki v2 (don't rely on remembering to do the bookkeeping; let an event do it).
#
# Reads the hook JSON on stdin, surfaces a NON-BLOCKING systemMessage at most
# once per session, and ONLY when the session did substantial multi-step work.
# Always exits 0 so it can never break a turn. Dependency-light (jq optional).
set +e

input="$(cat)"

# Pull a top-level string field from the hook JSON. Uses jq if present, else sed.
field() {
  local key="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$input" | jq -r --arg k "$key" '.[$k] // empty' 2>/dev/null
  else
    printf '%s' "$input" \
      | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -1
  fi
}

# Never re-enter a stop-hook continuation loop.
[ "$(field stop_hook_active)" = "true" ] && exit 0

transcript="$(field transcript_path)"
session="$(field session_id)"
[ -z "$transcript" ] && exit 0
[ -f "$transcript" ] || exit 0

# Fire at most once per session (marker keyed by session id).
marker="${TMPDIR:-/tmp}/.distill-nudge-${session:-unknown}"
[ -f "$marker" ] && exit 0

# Heuristic: how much real work happened? Count tool uses and concrete mutations.
tools="$(grep -Ec '"type"[[:space:]]*:[[:space:]]*"tool_use"' "$transcript" 2>/dev/null)"
edits="$(grep -Eoc '"name"[[:space:]]*:[[:space:]]*"(Edit|Write|Bash|NotebookEdit)"' "$transcript" 2>/dev/null)"
[ -z "$tools" ] && tools=0
[ -z "$edits" ] && edits=0

# Only nudge for substantial, multi-step sessions — stay quiet otherwise.
if [ "$tools" -ge 8 ] || [ "$edits" -ge 4 ]; then
  : > "$marker" 2>/dev/null
  printf '%s\n' '{"systemMessage":"💡 This session ran a multi-step workflow. If it is worth repeating, consider distilling it into a reusable skill — run /marketplace-contributor:contribute-skill (or describe it and say \"save this as a skill\")."}'
fi

exit 0
