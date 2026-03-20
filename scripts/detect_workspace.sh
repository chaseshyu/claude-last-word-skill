#!/usr/bin/env bash
# detect_workspace.sh
# Auto-detects the Cowork workspace root (the directory containing CLAUDE.md).
# Usage:  bash detect_workspace.sh
# Output: absolute path to workspace (or error message on stderr, exit 1)

set -eo pipefail

# Strategy 1: infer from this script's own location (most reliable).
# When installed, this script lives at <workspace>/.skills/skills/last-word/scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANDIDATE="${SCRIPT_DIR%/.skills/skills/last-word/scripts}"
if [ -f "$CANDIDATE/CLAUDE.md" ]; then
    echo "$CANDIDATE"
    exit 0
fi

# Strategy 2: scan /sessions/*/mnt/*/ for a directory that contains CLAUDE.md.
# Use grep -m1 instead of head -1 to avoid SIGPIPE with pipefail.
FOUND=$(find /sessions -maxdepth 4 -name "CLAUDE.md" \
    -not -path "*/.skills/*" \
    -not -path "*/node_modules/*" \
    2>/dev/null | grep -m1 . || true)

if [ -n "$FOUND" ]; then
    dirname "$FOUND"
    exit 0
fi

echo "ERROR: Could not find a workspace (no CLAUDE.md found)" >&2
echo "Pass the path manually: bash detect_workspace.sh /path/to/workspace" >&2
exit 1
