#!/usr/bin/env python3
"""
PreToolUse hook: denies the agent from writing to any `*.allow.json` file
(the exception lists used by deny-remove and deny-non-rel-path), so those
files can only be edited by a human working directly on disk - never by
the agent granting itself an exception.

Exact for Write/Edit/NotebookEdit, whose file_path names the target file
directly. For Bash, best-effort: blocks only when the command both names
an `*.allow.json` path and looks like a write (redirection, tee, sed/perl
-i, or an inline script's file-write call) - a plain `cat` or `grep` on
the file still passes. Like the other hooks here, this is a blocklist
over command text, not a sandbox.
"""

import json
import re
import sys

ALLOWLIST_SUFFIX = ".allow.json"
PATH_FIELDS = ("file_path", "notebook_path")

WRITE_PATTERNS = [
    re.compile(r">>?\s*\S*" + re.escape(ALLOWLIST_SUFFIX)),  # > file / >> file
    re.compile(r"\btee\b[^|;&]*" + re.escape(ALLOWLIST_SUFFIX)),  # tee file
    re.compile(r"\bsed\b[^|;&]*-i[^|;&]*" + re.escape(ALLOWLIST_SUFFIX)),  # sed -i ... file
    re.compile(r"\bperl\b[^|;&]*-i[^|;&]*" + re.escape(ALLOWLIST_SUFFIX)),  # perl -i ... file
    re.compile(  # python open(..., "w"/"a")
        r"open\s*\(\s*[\"'][^\"']*"
        + re.escape(ALLOWLIST_SUFFIX)
        + r"[\"']\s*,\s*[\"'][wa]"
    ),
    re.compile(  # node fs.writeFile(Sync)/appendFile(Sync)
        r"fs\.(writeFile|writeFileSync|appendFile|appendFileSync)\s*\(\s*[\"'][^\"']*"
        + re.escape(ALLOWLIST_SUFFIX)
    ),
    re.compile(r"\bcp\b[^|;&]*" + re.escape(ALLOWLIST_SUFFIX) + r"\s*$"),  # cp ... file (dest)
    re.compile(r"\bmv\b[^|;&]*" + re.escape(ALLOWLIST_SUFFIX) + r"\s*$"),  # mv ... file (dest)
]


def load_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def check_structured(payload):
    tool_input = payload.get("tool_input") or {}
    for field in PATH_FIELDS:
        value = tool_input.get(field)
        if isinstance(value, str) and value.endswith(ALLOWLIST_SUFFIX):
            return value
    return None


def check_bash(payload):
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if not command or ALLOWLIST_SUFFIX not in command:
        return None
    for pattern in WRITE_PATTERNS:
        if pattern.search(command):
            return command
    return None


def main():
    payload = load_payload()
    tool_name = payload.get("tool_name")

    offender = None
    if tool_name == "Bash":
        offender = check_bash(payload)
    elif tool_name in ("Write", "Edit", "NotebookEdit"):
        offender = check_structured(payload)

    if offender:
        print(
            "Editing *.allow.json is denied. Only a human may grant an "
            "exception by editing the allowlist file directly.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
