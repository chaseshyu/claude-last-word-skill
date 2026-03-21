#!/usr/bin/env python3
"""
scan_memory.py
Scans the workspace's memory/ directory and prints a status summary
of all in-progress features.
Usage: python3 scan_memory.py [workspace_path]
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def detect_workspace() -> Path:
    """Scan /sessions/*/mnt/ to find the workspace containing CLAUDE.md."""
    sessions_root = Path("/sessions")
    if sessions_root.exists():
        for session_dir in sessions_root.iterdir():
            mnt = session_dir / "mnt"
            if mnt.exists():
                for ws in mnt.iterdir():
                    if ws.is_dir() and (ws / "CLAUDE.md").exists() and ws.name != ".skills":
                        return ws
    raise RuntimeError("Could not find a workspace with CLAUDE.md")


def parse_memory_file(path: Path) -> dict:
    """Parse a memory file and extract key fields."""
    content = path.read_text(encoding="utf-8", errors="replace")
    result = {
        "name": path.stem,
        "path": str(path),
        "status": "unknown",
        "last_updated": "unknown",
        "next_step": "",
        "known_issues": [],
        "raw_size": len(content),
    }

    # Status — supports both English and Chinese field names
    m = re.search(r"\*\*(?:Status|狀態)\*\*\s*[:：]\s*(.+)", content)
    if m:
        result["status"] = m.group(1).strip()

    # Last updated — supports both English and Chinese field names
    m = re.search(r"\*\*(?:Last updated|最後更新)\*\*\s*[:：]\s*(.+)", content)
    if m:
        result["last_updated"] = m.group(1).strip()

    # Current position — first paragraph under the heading
    m = re.search(
        r"##\s*(?:Current Position|目前所在位置)\s*\n+(.+?)(?:\n#|$)",
        content, re.DOTALL
    )
    if m:
        result["next_step"] = m.group(1).strip()[:200]

    # Known issues — first few bullets under the heading
    m = re.search(
        r"##\s*(?:Known Issues.*?|已知問題.*?)\n+((?:[-*].+\n?)+)",
        content
    )
    if m:
        bullets = re.findall(r"[-*]\s*(.+)", m.group(1))
        result["known_issues"] = bullets[:3]

    # Progress: count checked vs total checkboxes
    done = len(re.findall(r"- \[x\]", content, re.IGNORECASE))
    total = len(re.findall(r"- \[[x ]\]", content, re.IGNORECASE))
    result["progress"] = f"{done}/{total}" if total > 0 else "N/A"

    return result


def main():
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else detect_workspace()
    memory_dir = workspace / "memory"

    print(f"📂 Workspace: {workspace}")
    print(f"📅 Scanned at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    if not memory_dir.exists():
        print("✅ memory/ directory does not exist — no in-progress features")
        return

    files = sorted(memory_dir.glob("*.md"))
    if not files:
        print("✅ memory/ directory is empty — no in-progress features")
        return

    active = []
    stale = []

    DONE_KEYWORDS = ["complete", "done", "merged", "archived", "完成", "已 merge"]

    for f in files:
        info = parse_memory_file(f)
        if any(kw in info["status"].lower() for kw in DONE_KEYWORDS):
            stale.append(info)
        else:
            active.append(info)

    if active:
        print(f"\n🔄 In-progress features ({len(active)}):\n")
        for info in active:
            print(f"  📌 {info['name']}")
            print(f"     Status: {info['status']}  |  Progress: {info['progress']}  |  Last updated: {info['last_updated']}")
            if info["next_step"]:
                print(f"     Resume at: {info['next_step'][:100]}")
            if info["known_issues"]:
                print(f"     ⚠️  Known issue: {info['known_issues'][0]}")
            print()

    if stale:
        print(f"\n🗑️  Possibly stale memory ({len(stale)} — status looks complete):")
        for info in stale:
            print(f"  - {info['name']} (status: {info['status']})")
        print("  → Confirm whether these should be deleted\n")

    print("=" * 60)
    print(f"Total: {len(active)} in progress, {len(stale)} possibly stale")


if __name__ == "__main__":
    main()
