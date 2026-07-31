# last-word

A Claude Code skill for session wrap-up. Run `/last-word` at the end of every session to archive what you learned, capture remaining work, and generate a starter prompt for next time.

## What it does

Seven stages, in order:

1. **Review** — Scans the conversation history for stuck points, what worked, and gaps in CLAUDE.md
2. **Categorize & Archive** — Files every piece of knowledge into the right place (CLAUDE.md, tasks/prd-*.md, memory/, or Claude Code's auto-memory)
3. **Capture remaining work** — Creates or updates memory files for unfinished features
4. **Clean up stale memory** — Deletes memory files for completed features, merges duplicates
5. **Check uncommitted changes** — Flags any dirty git repos before you clear the session
6. **Generate starter prompt** — Produces a ready-to-paste prompt for the next session
7. **Confirm safe to clear** — Gives a final status summary

## Project layout (assumed)

```
<workspace>/
├── CLAUDE.md         ← Cross-cutting rules that apply every session
├── tasks/            ← Feature design docs (prd-<feature>.md)
├── memory/           ← Transient "where we left off" state (one file per active feature)
└── <codebase>/       ← Main codebase (git repo)
```

Knowledge classification rule:
- Applies to every feature → `CLAUDE.md`
- Specific to one feature (math, design decisions, gotchas) → `tasks/prd-<feature>.md`
- Transient progress state → `memory/<feature>.md`
- About the user or how Claude should work (preferences, feedback, gotchas Claude
  itself needs recalled) → Claude Code's own auto-memory
  (`~/.claude/projects/<project>/memory/`), never duplicated into the project files

## Workspace detection

The skill locates the workspace root (the directory containing `CLAUDE.md`) by
walking up from the current working directory. All scripts also accept an explicit
workspace path as their first argument, and keep a `/sessions/*/mnt/` scan as a
fallback for claude.ai Cowork containers.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/detect_workspace.sh` | Finds the workspace root (directory containing `CLAUDE.md`) |
| `scripts/scan_memory.py` | Prints a status summary of all in-progress memory files |
| `scripts/generate_starter.py` | Reads memory files and generates a next-session starter prompt |
| `scripts/check_git.sh` | Scans all git repos in the workspace for uncommitted changes |

## Installation

You can automatically install this skill directly into your Claude Code environment by running:

```bash
npx @chaseshyu/claude-last-word-skill
```

This command will copy the skill files into `~/.claude/skills/last-word`.

Once installed, simply type `/last-word` (or say "wrap up", "session over", "last word", etc.) inside Claude Code to trigger it.

## Memory file format

```markdown
# Memory: <Feature Name>

**Last updated**: YYYY-MM-DD
**Status**: In progress | Paused | Pending review

## Progress

- [x] Step 1: completed work
- [ ] Step 2: resume here next session

## Current Position

Working in `<function_name>()` in `<file.cxx>`, implementing <feature>.
Last stopped at line X; open question is <problem>.

## Known Issues / Gotchas

- <issue>: <fix direction>

## Relevant Files

- `path/to/file.cxx`: role in this feature
```

Full template at `references/memory-template.md`.
