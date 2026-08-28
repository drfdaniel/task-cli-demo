#!/usr/bin/env python3
"""
task_cli.py — a tiny command-line task manager.

This is deliberately simple: it's meant to be a low-stakes playground
for practicing Git workflows (commits, branches, PRs) and trying out
Claude Code against a real repo.

Usage:
    python task_cli.py add "Buy milk" [--priority low|medium|high]
    python task_cli.py list [--sort priority]
    python task_cli.py done 1
    python task_cli.py remove 1

Tasks are stored in tasks.json in the current directory.
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path("tasks.json")
PRIORITIES = ("low", "medium", "high")
DEFAULT_PRIORITY = "medium"
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_tasks():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(description, priority=DEFAULT_PRIORITY):
    tasks = load_tasks()
    new_id = (max((t["id"] for t in tasks), default=0)) + 1
    tasks.append({"id": new_id, "description": description, "done": False, "priority": priority})
    save_tasks(tasks)
    print(f"Added task #{new_id} [{priority}]: {description}")


def list_tasks(sort=None):
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet. Add one with: python task_cli.py add \"Your task\"")
        return
    if sort == "priority":
        tasks = sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.get("priority", DEFAULT_PRIORITY), 1))
    for t in tasks:
        status = "✔" if t["done"] else " "
        priority = t.get("priority", DEFAULT_PRIORITY)
        print(f"[{status}] #{t['id']} ({priority}) {t['description']}")


def complete_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            print(f"Marked #{task_id} as done.")
            return
    print(f"No task with id {task_id}")


def remove_task(task_id):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        print(f"No task with id {task_id}")
        return
    save_tasks(new_tasks)
    print(f"Removed task #{task_id}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 3:
        args = sys.argv[2:]
        priority = DEFAULT_PRIORITY
        if "--priority" in args:
            idx = args.index("--priority")
            if idx + 1 >= len(args) or args[idx + 1] not in PRIORITIES:
                print(f"--priority must be one of: {', '.join(PRIORITIES)}")
                return
            priority = args[idx + 1]
            del args[idx:idx + 2]
        description = " ".join(args)
        if not description:
            print("A task description is required.")
            return
        add_task(description, priority)
    elif command == "list":
        args = sys.argv[2:]
        sort = None
        if "--sort" in args:
            idx = args.index("--sort")
            if idx + 1 >= len(args) or args[idx + 1] != "priority":
                print("--sort must be one of: priority")
                return
            sort = args[idx + 1]
        list_tasks(sort)
    elif command == "done" and len(sys.argv) == 3:
        complete_task(int(sys.argv[2]))
    elif command == "remove" and len(sys.argv) == 3:
        remove_task(int(sys.argv[2]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
