#!/usr/bin/env python3
"""
Stop hook for do skill workflow.

Checks if the do loop is complete before allowing exit.
Uses the new task directory structure under .codex/do-tasks/.
"""

import glob
import json
import os
import re
import sys

DIR_TASKS = ".codex/do-tasks"
FILE_CURRENT_TASK = ".current-task"
FILE_TASK_MD = "task.md"

PHASE_NAMES = {
    1: "Understand",
    2: "Clarify",
    3: "Design",
    4: "Implement",
    5: "Complete",
}


def phase_name_for(n: int) -> str:
    return PHASE_NAMES.get(n, f"Phase {n}")


def get_current_task(project_dir: str) -> str | None:
    """Read current task directory path."""
    current_task_file = os.path.join(project_dir, DIR_TASKS, FILE_CURRENT_TASK)
    if not os.path.exists(current_task_file):
        return None
    try:
        with open(current_task_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else None
    except Exception:
        return None


def get_task_info(project_dir: str, task_dir: str) -> dict | None:
    """Read task.md YAML frontmatter as task metadata."""
    task_md_path = os.path.join(project_dir, task_dir, FILE_TASK_MD)
    if not os.path.exists(task_md_path):
        return None
    try:
        with open(task_md_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None

    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return None

    frontmatter = {}
    for line in match.group(1).split("\n"):
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value == "true":
            value = True
        elif value == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        frontmatter[key] = value

    return frontmatter


def check_task_complete(project_dir: str, task_dir: str) -> str:
    """Check if task is complete. Returns blocking reason or empty string."""
    task_info = get_task_info(project_dir, task_dir)
    if not task_info:
        return ""

    status = task_info.get("status", "")
    if status == "completed":
        return ""

    current_phase = task_info.get("current_phase", 1)
    max_phases = task_info.get("max_phases", 5)
    phase_name = task_info.get("phase_name", phase_name_for(current_phase))
    completion_promise = task_info.get("completion_promise", "<promise>DO_COMPLETE</promise>")

    if current_phase >= max_phases:
        # Task is at final phase, allow exit
        return ""

    return (
        f"do loop incomplete: current phase {current_phase}/{max_phases} ({phase_name}). "
        f"Continue with remaining phases; use 'task.py update-phase <N>' after each phase. "
        f"Include completion_promise in final output when done: {completion_promise}. "
        f"To exit early, set status to 'completed' in task.md frontmatter."
    )


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    task_dir = get_current_task(project_dir)
    if not task_dir:
        # No active task, allow exit
        sys.exit(0)

    stdin_payload = ""
    if not sys.stdin.isatty():
        try:
            stdin_payload = sys.stdin.read()
        except Exception:
            pass

    reason = check_task_complete(project_dir, task_dir)
    if not reason:
        sys.exit(0)

    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
