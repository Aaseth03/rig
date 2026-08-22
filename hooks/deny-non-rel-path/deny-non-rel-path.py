#!/usr/bin/env python3
"""
PreToolUse hook: denies the agent from reading or writing any path that
resolves outside the project root, without a human-approved exception.

Enforced precisely for tools with a structured path parameter (Read,
Write, Edit, NotebookEdit, Glob, Grep) by resolving the given path
(including ../ traversal) against the project root. For Bash, this
best-effort scans the command text for absolute path tokens and applies
the same check - it cannot catch every way a shell command could reach
outside the root (obfuscated paths, env var expansion resolved only at
runtime, etc.), the same caveat as hooks/deny-remove.

Nothing outside the root is allowed by default. If the agent legitimately
needs a specific external path, a human adds it - one absolute path per
entry under "allowed_paths" - to `deny-non-rel-path.allow.json`, next to
this script. A path is allowed if it equals, or is a subdirectory of, an
allowed path. The agent must never edit that file itself - see
hooks/deny-allowlist-edit.
"""

import json
import os
import re
import sys

PATH_FIELDS = ("file_path", "path", "notebook_path")
ALLOWLIST_FILENAME = "deny-non-rel-path.allow.json"
ABS_PATH_RE = re.compile(r"(?:(?<=[\s\"'=])|^)(/[^\s\"']+|~[^\s\"']*)")


def load_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def get_root(payload):
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return os.path.realpath(root)


def load_allowlist():
    allow_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ALLOWLIST_FILENAME
    )
    try:
        with open(allow_file, "r") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    paths = data.get("allowed_paths") or []
    return [os.path.realpath(os.path.expanduser(p)) for p in paths if isinstance(p, str)]


def resolve(path, root):
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    return os.path.realpath(os.path.expanduser(path))


def is_allowed(resolved, root, allowlist):
    if resolved == root or resolved.startswith(root + os.sep):
        return True
    return any(
        resolved == prefix or resolved.startswith(prefix + os.sep)
        for prefix in allowlist
    )


def check_structured(payload, root, allowlist):
    tool_input = payload.get("tool_input") or {}
    for field in PATH_FIELDS:
        value = tool_input.get(field)
        if isinstance(value, str) and value:
            resolved = resolve(value, root)
            if not is_allowed(resolved, root, allowlist):
                return value
    return None


def check_bash(payload, root, allowlist):
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if not command:
        return None
    for match in ABS_PATH_RE.finditer(command):
        candidate = match.group(0)
        resolved = resolve(candidate, root)
        if not is_allowed(resolved, root, allowlist):
            return candidate
    return None


def main():
    payload = load_payload()
    root = get_root(payload)
    allowlist = load_allowlist()
    tool_name = payload.get("tool_name")

    if tool_name == "Bash":
        offender = check_bash(payload, root, allowlist)
    else:
        offender = check_structured(payload, root, allowlist)

    if offender:
        print(
            "Path outside project root blocked by hook: "
            f"{offender}\n"
            "A human must place the needed content inside the project, "
            f"or approve the path by adding it to {ALLOWLIST_FILENAME}.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
