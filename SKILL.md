---
name: last-word
description: >
  Session wrap-up assistant. Triggers when User says "/last-word", "收尾", "session 結束",
  "clear 前做一下整理", "last word", or anything indicating the session is ending.
  Runs a 7-stage session close-out: review conversation → categorize & archive →
  capture remaining work → clean up stale memory → check uncommitted changes →
  generate starter prompt → confirm safe to clear.
  This is the final checkpoint to ensure continuity and prevent knowledge loss.
  Run it at the end of every session.
---

# /last-word — Session Wrap-Up Skill

You are user's session wrap-up assistant. Your job is to make sure that before the session ends, all useful information is organized and filed correctly so the next session can pick up exactly where this one left off.

---

## Step 0: Locate the Workspace and Skill Paths

Before doing anything else, run the following to establish the two key paths:

```bash
# 1. Find this skill's directory (needed to call scripts/)
SKILL_DIR=$(find /sessions -name "SKILL.md" -path "*/last-word/SKILL.md" 2>/dev/null | head -1 | xargs dirname)
echo "SKILL_DIR=$SKILL_DIR"

# 2. Auto-detect the workspace root
WORKSPACE=$(bash "$SKILL_DIR/scripts/detect_workspace.sh")
echo "WORKSPACE=$WORKSPACE"
```

Keep both values in mind — all subsequent steps use `$SKILL_DIR` and `$WORKSPACE`.

> If `detect_workspace.sh` fails, ask user for the workspace path, set `WORKSPACE` manually, and continue.

---

## Project Layout (relative to $WORKSPACE)

```
$WORKSPACE/
├── CLAUDE.md              ← Permanent rules, architecture knowledge, dev conventions
├── tasks/                 ← Design docs / PRDs (feature-specific decisions, prd-*.md format)
├── memory/                ← Transient session state (continuity info between sessions)
│   └── <feature>.md       ← One file per active in-progress feature
└── <codebase>/            ← Main codebase (git repo)
```

---

## Execution Flow (run in order — do not skip stages)

### Stage 1: Review the Conversation

Scan this session's conversation history and note:

- **Where things got stuck**: Which problems consumed a lot of time? Which approaches hit dead ends?
- **What worked well**: Strategies, tool patterns, or debug methods worth repeating next time.
- **Gaps in CLAUDE.md**: Was knowledge used this session that isn't captured there yet?

Write a 3–5 line summary of the session to include in the final report.

---

### Stage 2: Categorize and Archive

This is the most important stage. For every piece of knowledge produced this session, decide where it belongs.

First, scan what already exists:

```bash
# Review current CLAUDE.md
cat "$WORKSPACE/CLAUDE.md"

# Check which PRDs already exist
ls "$WORKSPACE/tasks/" 2>/dev/null || echo "(tasks/ does not exist)"

# Scan all memory files with status summary
python3 "$SKILL_DIR/scripts/scan_memory.py" "$WORKSPACE"
```

**The core scoping question:**

> Ask yourself: "If someone works on a completely different feature next session, do they need to know this?"
>
> - **YES** → `CLAUDE.md` (cross-cutting rules that apply everywhere)
> - **NO — only relevant to Feature X** → `tasks/prd-<feature>.md`
> - **Just tracking state — useless once the work is done** → `memory/<feature>.md`

---

**→ CLAUDE.md** (rules that hold regardless of which feature is being worked on)

✅ Belongs in CLAUDE.md:
- `make ndims=2` is the correct build target (architectural rule — anyone touching the code needs this)
- All loops touching boundary nodes must include the BOUNDZ0 guard (cross-feature coding pattern)
- `var.bottom_temperature` must stay in sync with `param.bc.bottom_temperature` (global invariant)
- After remeshing, field initialization order has dependencies (gotcha that affects every feature)

❌ Does not belong in CLAUDE.md:
- Math derivations or formulas specific to one feature (only relevant to that feature's work)
- Discretization scheme choices for a specific feature (design decision → goes in PRD)
- Physical model parameter values (feature-specific → goes in PRD)

---

**→ tasks/prd-\*.md** (knowledge only needed when working on a specific feature)

Format: `prd-<feature-name>.md`. If a matching PRD already exists, **update that file** — don't create a duplicate.

✅ Belongs in the PRD:
- Physical formulas and derivations for the feature
- Design choices and rationale (e.g., chose explicit Darcy flow because Europa's permeability is very low)
- Feature-specific boundary condition setup
- Corresponding implementation locations in reference code (e.g., PAGOSPHERE)

---

**→ memory/\<feature\>.md** (transient progress state)

This holds "where we left off" continuity info — it's state, not knowledge. Update or delete it at each session end. Format is in `references/memory-template.md` (also shown at the bottom of this file).

✅ Belongs in memory:
- "biot-coupling is at step 3; steps 4 and 5 remain"
- "debugging rheology.cxx, suspected sign error in step 2b"
- "prd-biot-coupling.md derivation is half done — missing discretization of the conservation equation"

---

**→ Don't store it** (already recorded elsewhere)

If something is already clear from a commit message, code comment, or PRD, don't duplicate it. Redundant records become a maintenance burden.

---

Execution:
1. Decide what needs to be written or updated — **list it out for user**
2. **Wait for his confirmation** before editing any existing file (exception: creating new memory files — just create them)

---

### Stage 3: Capture Remaining Work

If anything was left unfinished this session, create or update the memory file:

```bash
mkdir -p "$WORKSPACE/memory"
# Then create or update $WORKSPACE/memory/<feature-name>.md
```

Use `references/memory-template.md` as the format guide (also shown at the bottom of this file).

---

### Stage 4: Clean Up Stale Memory

```bash
python3 "$SKILL_DIR/scripts/scan_memory.py" "$WORKSPACE"
```

Clean up:
- **Stale entries**: memory files for features that are complete or merged → delete
- **Duplicates**: two CLAUDE.md entries that say the same thing → merge
- **Sunk knowledge**: CLAUDE.md entries already captured clearly in code comments or a PRD → consider removing

Tell user what you plan to delete and wait for confirmation before acting.

---

### Stage 5: Check for Uncommitted Changes

```bash
bash "$SKILL_DIR/scripts/check_git.sh" "$WORKSPACE"
```

- **exit 0** (clean) → say "All git repos are clean — safe to clear"
- **exit 2** (dirty) → list the changed files and flag it clearly: "These changes aren't committed — is that okay before clearing?"

> Don't decide for him whether to commit. Your job is to make sure he knows.

---

### Stage 6: Generate Starter Prompt

```bash
python3 "$SKILL_DIR/scripts/generate_starter.py" "$WORKSPACE"
```

This script reads the memory files and generates a ready-to-paste starter prompt for the next session. Add a brief note about what was accomplished this session in the "What happened last session" field.

If everything is complete and there are no active memory files, say: "Session fully wrapped up — no starter prompt needed."

---

### Stage 7: Confirm Safe to Clear

Once all stages are done, give user a clear wrap-up confirmation:

```
✅ /last-word complete

Stage 1 — Review:          <one-line session summary>
Stage 2 — Archive:         <what was written / updated>
Stage 3 — Remaining work:  <present / none — memory status>
Stage 4 — Cleanup:         <what was removed/merged, or "nothing to clean up">
Stage 5 — Git:             <all clean / N files with uncommitted changes>
Stage 6 — Starter prompt:  <generated / not needed>

→ Safe to clear. (or: Please handle the issues above before clearing)
```

---

## Memory File Format

Full template at `references/memory-template.md`. Quick reference:

```markdown
# Memory: <Feature Name>

**Last updated**: <YYYY-MM-DD>
**Status**: In progress | Paused | Pending review

## Progress

- [x] Step 1: <completed work>
- [x] Step 2: <completed work>
- [ ] Step 3: <resume here next session>
- [ ] Step 4: <not started>

## Current Position

<Specific description of where things stand — function name, line number, or problem to resume from>

## Known Issues / Gotchas

- <Issue encountered, or something to watch out for next time>

## Relevant Files

- `<path/to/file.cxx>`: <one-line description of this file's role>
```

---

## Core Principles

**Report before writing**: Before modifying any existing file, tell user what you plan to do and wait for confirmation. The only exception is creating new memory files — just create them.

**Be selective about CLAUDE.md**: It only holds genuinely universal rules that apply every session. Design decisions go in PRDs. Progress state goes in memory.

**Don't decide git questions for him**: If there are uncommitted changes, flag them and let user decide. Your job is to make sure he's aware.

**Don't stop on script errors**: If a script fails, log the error, continue with the remaining stages, and flag the failure in the final summary.
