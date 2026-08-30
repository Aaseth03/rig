#!/usr/bin/env python3
"""
PostToolUse hook: flags oversized CONTEXT.md files after a Write/Edit.

Reads the Claude Code hook JSON payload from stdin. If the tool just wrote or
edited a file anywhere under a `.context/` directory and that file is now
over the line threshold, its path is upserted into a log file under
`.context/logs/` so a later context-doctor pass can find and split/compress
it. Files under `.context/logs/` are themselves excluded from this check -
a log growing past the threshold isn't a card that needs splitting.
"""

import json
import os
import sys
from datetime import date

LINE_THRESHOLD = 300
LOG_RELATIVE_PATH = os.path.join(".context", "logs", "CONTEXT_SIZE_LOG.md")
LOG_HEADER = (
    "# Context File Size Log\n\n"
    "Files below are over {threshold} lines and need review by the "
    "context-doctor pipeline (split, compress, or restructure).\n\n"
).format(threshold=LINE_THRESHOLD)


def load_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def resolve_file_path(payload):
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    if not file_path:
        return None
    if not os.path.isabs(file_path):
        cwd = payload.get("cwd") or os.getcwd()
        file_path = os.path.join(cwd, file_path)
    return os.path.normpath(file_path)


def is_under_context_dir(file_path, project_root):
    try:
        rel_path = os.path.relpath(file_path, project_root)
    except ValueError:
        return False
    return ".context" in rel_path.split(os.sep)[:-1]


def is_under_logs_dir(file_path, project_root):
    try:
        rel_path = os.path.relpath(file_path, project_root)
    except ValueError:
        return False
    parts = rel_path.split(os.sep)
    return len(parts) > 2 and parts[0] == ".context" and parts[1] == "logs"


def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return None


def parse_log_entries(log_path):
    entries = {}
    if not os.path.exists(log_path):
        return entries
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("- `"):
                continue
            try:
                path_part = line.split("`")[1]
                rest = line.split("`", 2)[2]
                lines_count = int(rest.split("—")[1].strip().split()[0])
            except (IndexError, ValueError):
                continue
            entries[path_part] = lines_count
    return entries


def write_log(log_path, entries):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(LOG_HEADER)
        for path_part in sorted(entries):
            f.write(
                "- `{path}` — {lines} lines (last checked {today})\n".format(
                    path=path_part, lines=entries[path_part], today=date.today().isoformat()
                )
            )


def main():
    payload = load_payload()
    if payload.get("tool_name") not in ("Write", "Edit"):
        return

    file_path = resolve_file_path(payload)
    if not file_path:
        return

    project_root = payload.get("cwd") or os.getcwd()
    if not is_under_context_dir(file_path, project_root):
        return
    if is_under_logs_dir(file_path, project_root):
        return

    line_count = count_lines(file_path)
    if line_count is None:
        return

    log_path = os.path.join(project_root, LOG_RELATIVE_PATH)
    rel_path = os.path.relpath(file_path, project_root)

    entries = parse_log_entries(log_path)

    if line_count > LINE_THRESHOLD:
        entries[rel_path] = line_count
    elif rel_path in entries:
        del entries[rel_path]
    else:
        return

    write_log(log_path, entries)


if __name__ == "__main__":
    main()
