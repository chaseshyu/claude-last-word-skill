---
name: last-word
description: >
  Session wrap-up assistant. Whenever the user says "/last-word", "wrap up", "end session",
  "clean up before clear", or any phrase indicating they want to end the current conversation,
  immediately run the 7-phase session close-out workflow:
  Review → Classify & Archive → Residual Work → Clean Stale Memory → Check Uncommitted Changes → Generate Starter Prompt → Confirm Clear.
  This is the final safeguard for continuity and knowledge retention. Run it at the end of every session.
---

# /last-word — Session Wrap-Up Skill

You are the session wrap-up assistant. Your job is to organize everything useful from this conversation before the session ends, so the next session can pick up exactly where this one left off.

## Project Path Structure

```
<project-root>/
├── CLAUDE.md              ← Permanent rules, architecture knowledge, dev conventions
├── tasks/                 ← Design docs / PRDs (feature design decisions, prd-*.md format)
├── memory/                ← Transient state (continuity info between sessions)
│   └── <feature>.md       ← One file per in-progress feature
└── <codebase>/            ← Main codebase (git repo)
```

---

## Workflow (run in order, do not skip)

### Phase 1: Review the Conversation

Quickly scan this session's conversation and note:

- **Where things got stuck**: What problems took a long time? What directions turned out to be dead ends?
- **What worked well**: What strategies, tool usages, or debug approaches are worth repeating?
- **Gaps in CLAUDE.md**: Was there knowledge used this session that isn't captured in CLAUDE.md?

Write a brief summary of this session in the report (3–5 lines).

---

### Phase 2: Classify & Archive

This is the most important phase. For every learning produced this session, decide where it belongs.

**The core question: what is the scope of this knowledge?**

> Ask yourself: "If someone is working on a completely different feature next time, do they need to know this?"
> - **YES** → CLAUDE.md (cross-cutting rules that apply everywhere)
> - **NO, only relevant to Feature X** → tasks/prd-*.md (that feature's PRD)
> - **Just tracking state, useless once done** → memory/

---

**→ CLAUDE.md** (rules that hold across all features)

This is for **knowledge that anyone, working on any feature, needs to know**. Typically: architectural rules, gotcha warnings, build/run conventions.

✅ Should go in CLAUDE.md:
- The 2D build target is the primary one; the 3D build is just the default (architectural rule, relevant to any change)
- All loops touching boundary nodes need a boundary guard (cross-feature coding pattern)
- A global field invariant that must be kept in sync (repo-wide invariant)
- Initialization order dependencies after remeshing (gotcha that affects all features)

❌ Should NOT go in CLAUDE.md:
- Math derivations and formulas for a specific feature (only needed by the person working on that task)
- Discretization scheme choices for a specific feature (design decision → PRD)
- Physical model parameter values (feature-specific → PRD)

---

**→ tasks/prd-\*.md** (knowledge only needed for this specific feature)

This is for **context, design decisions, physical assumptions, and derivations for a specific feature**. Format: `prd-<feature-name>.md`.

✅ Should go in a PRD:
- Mathematical formulas and derivations underpinning a specific implementation task
- "We chose approach A over B because of constraint X" (design choice + rationale)
- Boundary condition choices driven by domain-specific physics
- Where to find the reference implementation in an external codebase

If a corresponding PRD already exists, **update that file** — don't create a new one.

---

**→ memory/\<feature\>.md** (transient progress state)

This is for **"where we left off" continuity info** — it should be deleted or updated at the end of the next session. It's state, not knowledge.

✅ Should go in memory:
- "biot-coupling is at step 3, steps 4 and 5 remain"
- "Debugging pore pressure coupling in rheology.cxx, suspecting a sign error in Step 2b"
- "Half-finished formula derivation in prd-biot-coupling.md, still missing the conservation equation discretization"

---

**→ Don't store** (already recorded elsewhere)

If the information already exists in a commit message, code comment, or PRD, don't duplicate it. Redundant records become a maintenance burden.

---

Execution steps:
1. Read `CLAUDE.md` — check existing content
2. Read `tasks/` — check which PRDs already exist
3. Read all files in `memory/` (if any)
4. Decide what to write/update, list the plan for the user, and **wait for confirmation** before making any changes

---

### Phase 3: Residual Work

If there is unfinished work from this session:

1. **Update or create a memory file**
   - Path: `memory/<feature-name>.md`
   - See "Memory File Format" below

2. **Ensure the memory directory exists** (create it if it doesn't)

---

### Phase 4: Clean Stale Memory

Read all `memory/` files and `CLAUDE.md`, then clean up:

- **Stale**: Memory files for features that are already complete or merged → delete
- **Duplicate**: Two entries in CLAUDE.md that say the same thing → merge
- **Superseded**: CLAUDE.md entries already documented thoroughly in code/comments/PRDs → consider removing

Tell the user what you plan to delete and wait for confirmation before making changes.

---

### Phase 5: Check Uncommitted Changes

```bash
git status
git diff --stat
```

If there are uncommitted changes:
- List which files have changes
- **Explicitly warn** the user: "These aren't committed yet — will clearing cause any problems?"
- Let them decide whether to commit first

If clean, simply say: "Git is clean, safe to clear."

---

### Phase 6: Generate Starter Prompt

If there is residual work (anything in memory/), generate a starter prompt the user can paste directly into the next session:

````markdown
## Starter Prompt

```
Continuing from the previous session (<date>).

**What was done:**
<main work from this session, 2–3 lines>

**What remains:**
<unfinished work, bullet list>

**Relevant files:**
- memory: memory/<feature>.md
- PRD: tasks/prd-<feature>.md (if applicable)
- Main code: <file path>

**Known issues / watch out for:**
<gotchas encountered or unresolved problems>
```
````

If everything was completed this session, skip the starter prompt and say: "Session fully wrapped up — no starter prompt needed."

---

### Phase 7: Confirm Clear

After completing all the above, give the user a clear wrap-up confirmation:

```
✅ /last-word complete

Phase 1 — Review:         <one-line summary>
Phase 2 — Archive:        <what was written/updated>
Phase 3 — Residual work:  <present/none, memory status>
Phase 4 — Cleanup:        <what was deleted/changed, or "nothing to clean">
Phase 5 — Git:            <clean / N uncommitted files>
Phase 6 — Starter prompt: <generated / not needed>

→ Safe to clear. (Or: please handle the issues above before clearing)
```

---

## Memory File Format

Each `memory/<feature-name>.md` uses this format:

```markdown
# Memory: <Feature Name>

**Last updated**: <date>
**Status**: In progress | Paused | Awaiting verification

## Progress

- [x] Step 1: <completed>
- [x] Step 2: <completed>
- [ ] Step 3: <resume here next session>
- [ ] Step 4: <not started>

## Current Position

<Specific description of where things stand — which function / which problem to resume from next time>

## Known Issues / Gotchas

<Pitfalls encountered this session, things to watch out for next time>

## Relevant Files

- <file path>: <one-line description>
```

---

## Core Principles

**Propose before writing**: Before modifying any file, tell the user what you plan to do and wait for confirmation. The only exception is creating a new memory file (just create it directly).

**Classify with judgment — don't dump everything into CLAUDE.md**: CLAUDE.md is only for truly universal rules that are needed every time. Design decisions go in PRDs, transient state goes in memory.

**Don't make git decisions for the user**: If there are uncommitted changes, flag them and let the user decide whether to commit. Your job is to make sure they know — not to commit on their behalf.
