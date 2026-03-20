#!/usr/bin/env python3
"""
generate_starter.py
Reads memory files and generates a ready-to-paste starter prompt
for the next session.
Usage: python3 generate_starter.py [workspace_path] [feature_name]
  - workspace_path: optional; auto-detected if omitted
  - feature_name:   optional; filter to a single feature
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def detect_workspace() -> Path:
    sessions_root = Path("/sessions")
    if sessions_root.exists():
        for session_dir in sessions_root.iterdir():
            mnt = session_dir / "mnt"
            if mnt.exists():
                for ws in mnt.iterdir():
                    if ws.is_dir() and (ws / "CLAUDE.md").exists() and ws.name != ".skills":
                        return ws
    raise RuntimeError("Could not find a workspace with CLAUDE.md")


def read_memory(path: Path) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")

    def extract(pattern, default=""):
        m = re.search(pattern, content, re.DOTALL)
        return m.group(1).strip() if m else default

    # Pending steps (unchecked checkboxes)
    pending_steps = re.findall(r"- \[ \]\s*(.+)", content)
    done_steps = re.findall(r"- \[x\]\s*(.+)", content, re.IGNORECASE)

    # Known issues section — supports English and Chinese headings
    issues_block = extract(r"##\s*(?:Known Issues.*?|已知問題.*?)\n+((?:[-*].+\n?)+)", "")
    issues = re.findall(r"[-*]\s*(.+)", issues_block)

    # Relevant files section
    files_block = extract(r"##\s*(?:Relevant Files|相關檔案).*?\n+((?:[-*].+\n?)+)", "")
    related_files = re.findall(r"[-*]\s*(.+)", files_block)

    # Current position section
    location = extract(
        r"##\s*(?:Current Position|目前所在位置)\s*\n+(.+?)(?:\n#|$)", ""
    )

    # Derive feature name from filename
    stem = path.stem
    feature_name = stem.removeprefix("memory-").removesuffix("-memory")

    # Status — supports English and Chinese
    status = extract(r"\*\*(?:Status|狀態)\*\*\s*[:：]\s*(.+)")
    last_updated = extract(r"\*\*(?:Last updated|最後更新)\*\*\s*[:：]\s*(.+)")

    return {
        "feature": feature_name,
        "path": str(path),
        "status": status,
        "last_updated": last_updated,
        "pending_steps": pending_steps,
        "done_steps": done_steps,
        "location": location,
        "issues": issues,
        "related_files": related_files,
    }


def format_starter(info: dict, session_summary: str = "", today: str = "") -> str:
    today = today or datetime.now().strftime("%Y-%m-%d")

    pending = "\n".join(f"- {s}" for s in info["pending_steps"]) \
              or "(see memory file for details)"
    issues = "\n".join(f"- {i}" for i in info["issues"]) \
             if info["issues"] else "(none known)"

    files_section = ""
    if info["related_files"]:
        files_section = "\n**Relevant files:**\n" + "\n".join(f"- {f}" for f in info["related_files"])

    location_section = ""
    if info["location"]:
        location_section = f"\n**Current position:**\n{info['location'][:300]}"

    summary_section = f"\n**What happened last session:**\n{session_summary}" \
                      if session_summary else ""

    return f"""Continuing from the previous session ({today}).

**Feature:** {info['feature']}
**Memory file:** memory/{Path(info['path']).name}
{summary_section}
**What still needs to be done:**
{pending}
{location_section}
**Known issues / watch out for:**
{issues}
{files_section}

Start by reading CLAUDE.md and the memory file above before touching any code."""


def main():
    args = sys.argv[1:]
    workspace = None
    feature_filter = None

    for arg in args:
        p = Path(arg)
        if p.exists() and p.is_dir():
            workspace = p
        else:
            feature_filter = arg

    if workspace is None:
        workspace = detect_workspace()

    memory_dir = workspace / "memory"
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"📂 Workspace: {workspace}")
    print(f"📅 {today}")
    print("=" * 60)

    if not memory_dir.exists() or not list(memory_dir.glob("*.md")):
        print("✅ No in-progress features — no starter prompt needed.")
        return

    files = sorted(memory_dir.glob("*.md"))
    if feature_filter:
        files = [f for f in files if feature_filter.lower() in f.stem.lower()]
        if not files:
            print(f"⚠️  No memory file matching '{feature_filter}' found")
            return

    DONE_KEYWORDS = ["complete", "done", "merged", "archived", "完成", "已 merge"]

    for f in files:
        info = read_memory(f)
        if any(kw in info["status"].lower() for kw in DONE_KEYWORDS):
            continue

        print(f"\n{'='*60}")
        print(f"🚀 Starter Prompt — {info['feature']}")
        print("=" * 60)
        print()
        print("```")
        print(format_starter(info, today=today))
        print("```")
        print()


if __name__ == "__main__":
    main()
