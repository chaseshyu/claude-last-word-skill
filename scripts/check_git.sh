#!/usr/bin/env bash
# check_git.sh
# Scans all git repos inside the workspace and reports uncommitted changes.
# Usage:  bash check_git.sh [workspace_path]
# Exit codes:
#   0 — all repos are clean
#   2 — one or more repos have uncommitted changes

set -eo pipefail

WORKSPACE="${1:-}"
if [ -z "$WORKSPACE" ]; then
    WORKSPACE=$(bash "$(dirname "${BASH_SOURCE[0]}")/detect_workspace.sh")
fi

echo "🔍 Scanning git status: $WORKSPACE"
echo "=========================================="

REPOS=$(find "$WORKSPACE" -maxdepth 4 -name ".git" -type d \
    -not -path "*/.skills/*" \
    2>/dev/null)

if [ -z "$REPOS" ]; then
    echo "✅ No git repositories found"
    exit 0
fi

HAS_DIRTY=0

while IFS= read -r GIT_DIR; do
    REPO=$(dirname "$GIT_DIR")
    cd "$REPO"

    REPO_RELATIVE="${REPO#$WORKSPACE/}"
    echo ""
    echo "📁 [$REPO_RELATIVE]"

    STATUS=$(git status --short 2>/dev/null)
    BRANCH=$(git branch --show-current 2>/dev/null || echo "detached HEAD")
    AHEAD=$(git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ' 2>/dev/null || echo "0")

    echo "   branch: $BRANCH"

    if [ -n "$STATUS" ]; then
        HAS_DIRTY=1
        echo "   ⚠️  Uncommitted changes:"
        # Use status --short only; avoid git diff on large repos (can crash)
        echo ""
        git status --short 2>/dev/null | sed 's/^/   /' || true
    else
        echo "   ✅ working tree clean"
    fi

    if [[ "$AHEAD" =~ ^[0-9]+$ ]] && [ "$AHEAD" -gt 0 ]; then
        echo "   ⚠️  $AHEAD commit(s) not yet pushed"
    fi
done <<< "$REPOS"

echo ""
echo "=========================================="
if [ "$HAS_DIRTY" -eq 1 ]; then
    echo "⚠️  Uncommitted changes found — confirm before clearing"
    exit 2
else
    echo "✅ All git repos are clean — safe to clear"
    exit 0
fi
