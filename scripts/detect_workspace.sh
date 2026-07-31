#!/usr/bin/env bash
# detect_workspace.sh
# Detects the workspace root (the directory containing CLAUDE.md).
# Usage:  bash detect_workspace.sh [workspace_path]
# Output: absolute path to workspace (or error message on stderr, exit 1)

set -eo pipefail

# Strategy 0: explicit path argument wins.
if [ -n "${1:-}" ]; then
    if [ -f "$1/CLAUDE.md" ]; then
        cd "$1" && pwd
        exit 0
    fi
    echo "ERROR: $1 has no CLAUDE.md" >&2
    exit 1
fi

# Strategy 1: walk up from the current working directory (local CLI — most common).
DIR="$(pwd)"
while [ "$DIR" != "/" ] && [ "$DIR" != "$HOME" ]; do
    if [ -f "$DIR/CLAUDE.md" ]; then
        echo "$DIR"
        exit 0
    fi
    DIR="$(dirname "$DIR")"
done

# Strategy 2 (Cowork containers): infer from this script's own location,
# which lives at <workspace>/.skills/skills/last-word/scripts/ when installed there.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE="${SCRIPT_DIR%/.skills/skills/last-word/scripts}"
if [ "$CANDIDATE" != "$SCRIPT_DIR" ] && [ -f "$CANDIDATE/CLAUDE.md" ]; then
    echo "$CANDIDATE"
    exit 0
fi

# Strategy 3 (Cowork containers): scan /sessions/*/mnt/*/ for CLAUDE.md.
# Use grep -m1 instead of head -1 to avoid SIGPIPE with pipefail.
if [ -d /sessions ]; then
    FOUND=$(find /sessions -maxdepth 4 -name "CLAUDE.md" \
        -not -path "*/.skills/*" \
        -not -path "*/node_modules/*" \
        2>/dev/null | grep -m1 . || true)
    if [ -n "$FOUND" ]; then
        dirname "$FOUND"
        exit 0
    fi
fi

echo "ERROR: Could not find a workspace (no CLAUDE.md found)" >&2
echo "Pass the path explicitly: bash detect_workspace.sh /path/to/workspace" >&2
exit 1
