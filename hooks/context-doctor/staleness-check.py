#!/usr/bin/env python3
"""
PostToolUse hook: flags .context/ cards as stale after a Write/Edit.

Reads the Claude Code hook JSON payload from stdin. Parses
`.context/effects/UPKEEP.md`'s write-back table (source pattern -> card to
refresh). If the tool just wrote or edited a file matching one of those
source patterns, the mapped card is upserted into a project-root log file
so a later context-doctor pass can re-verify it. If the tool just wrote or
edited one of the mapped cards itself, any pending entry naming it is
cleared - it was just refreshed.
"""

import fnmatch
import json
import os
import re
import sys
from datetime import date

LOG_FILENAME = "CONTEXT_STALE_LOG.md"
UPKEEP_REL_PATH = os.path.join(".context", "effects", "UPKEEP.md")
LOG_HEADER = (
    "# Context Staleness Log\n\n"
    "Cards below need re-verifying (status, date, citations) against the "
    "source that changed, per .context/effects/UPKEEP.md. Resolved by the "
    "context-doctor maintenance pass.\n\n"
)

BACKTICK_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LOG_LINE_RE = re.compile(
    r"^- `([^`]+)` — stale after change to `([^`]+)` \(flagged ([\d-]+)\)$"
)


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


def parse_upkeep_table(project_root):
    upkeep_path = os.path.join(project_root, UPKEEP_REL_PATH)
    if not os.path.exists(upkeep_path):
        return []

    effects_dir = os.path.dirname(upkeep_path)
    rows = []
    with open(upkeep_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or not line.endswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 2:
                continue
            source_cell, card_cell = cells
            if set(source_cell) <= {"-", " "}:
                continue  # separator row
            patterns = BACKTICK_RE.findall(source_cell)
            link_match = LINK_RE.search(card_cell)
            if not patterns or not link_match:
                continue  # header row or malformed row
            card_abs = os.path.normpath(os.path.join(effects_dir, link_match.group(1)))
            card_rel = os.path.relpath(card_abs, project_root)
            rows.append((patterns, card_rel))
    return rows


def matches_pattern(pattern, rel_path):
    pattern = pattern.replace("<name>", "*")
    rel_path = rel_path.replace(os.sep, "/")

    if "/" not in pattern:
        return fnmatch.fnmatchcase(rel_path.rsplit("/", 1)[-1], pattern)

    is_prefix = pattern.endswith("/")
    pattern = pattern.rstrip("/")
    pattern_parts = pattern.split("/")
    path_parts = rel_path.split("/")

    if is_prefix:
        if len(path_parts) <= len(pattern_parts):
            return False
        path_parts = path_parts[: len(pattern_parts)]
    elif len(path_parts) != len(pattern_parts):
        return False

    return all(fnmatch.fnmatchcase(p, seg) for p, seg in zip(path_parts, pattern_parts))


def parse_log_entries(log_path):
    entries = {}
    if not os.path.exists(log_path):
        return entries
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            match = LOG_LINE_RE.match(line.strip())
            if not match:
                continue
            card, source, flagged = match.groups()
            entries[card] = {"source": source, "date": flagged}
    return entries


def write_log(log_path, entries):
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(LOG_HEADER)
        for card in sorted(entries):
            info = entries[card]
            f.write(
                "- `{card}` — stale after change to `{source}` (flagged {date})\n".format(
                    card=card, source=info["source"], date=info["date"]
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
    rows = parse_upkeep_table(project_root)
    if not rows:
        return

    rel_path = os.path.relpath(file_path, project_root)
    log_path = os.path.join(project_root, LOG_FILENAME)
    entries = parse_log_entries(log_path)
    card_paths = {card for _, card in rows}
    changed = False

    if rel_path in card_paths:
        if rel_path in entries:
            del entries[rel_path]
            changed = True
    else:
        for patterns, card_rel in rows:
            if card_rel in entries:
                continue  # already pending, nothing to upsert
            if any(matches_pattern(p, rel_path) for p in patterns):
                entries[card_rel] = {"source": rel_path, "date": date.today().isoformat()}
                changed = True

    if changed:
        write_log(log_path, entries)


if __name__ == "__main__":
    main()
