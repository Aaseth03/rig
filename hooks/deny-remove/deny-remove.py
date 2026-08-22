#!/usr/bin/env python3
"""
PreToolUse hook: denies Bash commands that delete files or directories,
unless every path the command targets is covered by this hook's
allowlist.

Blocks standalone delete commands (rm, unlink, shred, find -delete) and
delete calls embedded in inline scripts (node -e, python -c, ...), since
those are just another way to reach the same syscall. `git clean -f` is
always blocked - it isn't scoped to a single path argument, so there is
nothing to check an allowlist entry against.

A human can permit deletion under a specific directory by adding its
path - one absolute path per entry under "allowed_paths" - to
`deny-remove.allow.json`, next to this script. A target path is allowed
if it equals, or is a subdirectory of, an allowed path. Nothing is
allowed by default. The agent must never edit that file itself - see
hooks/deny-allowlist-edit.

This is a blocklist over command text, not a sandbox: it raises the bar
against routine and copy-pasted delete commands, but a sufficiently
obfuscated command (e.g. base64-decoded and eval'd, or `xargs rm`) can
still slip past. For airtight protection, protect specific paths at the
OS level (chmod, chattr +i) or move Bash to an allowlist.
"""

import json
import os
import re
import shlex
import sys

CHAIN_OPERATORS = {";", "&&", "||", "|"}

# Standalone commands whose entire purpose is deleting/wiping content.
DELETE_COMMAND_NAMES = {"rm", "unlink", "shred"}

ALLOWLIST_FILENAME = "deny-remove.allow.json"

# Regexes for delete calls embedded in inline scripts passed to interpreters
# (node -e, python -c, perl -e, ruby -e, ...).
EMBEDDED_DELETE_PATTERNS = [
    re.compile(r"\bos\.(remove|unlink|rmdir)\s*\("),          # python os
    re.compile(r"\bshutil\.rmtree\s*\("),                     # python shutil
    # method call on any receiver, e.g. fs.unlinkSync(...) or
    # require('fs').unlinkSync(...) - node fs / pathlib Path(...).unlink()
    re.compile(r"\.(unlink|unlinkSync|rm|rmSync|rmdir|rmdirSync|rmtree)\s*\("),
    re.compile(r"\bunlink\s*\("),                              # perl/C-style unlink()
]

QUOTED_STRING_RE = re.compile(r"""(['"])((?:(?!\1).)*)\1""")


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


def is_allowed_path(path, root, allowlist):
    resolved = resolve(path, root)
    return any(
        resolved == prefix or resolved.startswith(prefix + os.sep)
        for prefix in allowlist
    )


def command_spans(tokens):
    start = 0
    for i, token in enumerate(tokens):
        if token in CHAIN_OPERATORS:
            yield start, i
            start = i + 1
    yield start, len(tokens)


def has_blocked_delete(tokens, root, allowlist):
    for start, end in command_spans(tokens):
        segment = tokens[start:end]
        idx = 0
        while idx < len(segment) and segment[idx].rsplit("/", 1)[-1] == "sudo":
            idx += 1
        if idx >= len(segment):
            continue
        name = segment[idx].rsplit("/", 1)[-1]

        if name in DELETE_COMMAND_NAMES:
            args = [t for t in segment[idx + 1:] if not t.startswith("-")]
            if not args or any(not is_allowed_path(a, root, allowlist) for a in args):
                return True

        elif name == "find" and "-delete" in segment:
            targets = [t for t in segment[idx + 1:] if not t.startswith("-")]
            if not targets or any(not is_allowed_path(t, root, allowlist) for t in targets):
                return True

        elif name == "git" and "clean" in segment and any(
            t in ("-f", "-fd", "-df", "--force") for t in segment
        ):
            return True  # not path-scoped; always blocked

    return False


def has_blocked_embedded_delete(command, root, allowlist):
    if not any(pattern.search(command) for pattern in EMBEDDED_DELETE_PATTERNS):
        return False
    candidates = [m.group(2) for m in QUOTED_STRING_RE.finditer(command)]
    if not candidates:
        return True  # can't verify the target - fail closed
    return any(not is_allowed_path(c, root, allowlist) for c in candidates)


def is_destructive_command(payload, root, allowlist):
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command")
    if not command:
        return False

    try:
        tokens = shlex.split(command)
    except ValueError:
        # Unbalanced quotes etc. - fall back to raw text so we fail closed.
        tokens = command.split()

    if has_blocked_delete(tokens, root, allowlist):
        return True
    if has_blocked_embedded_delete(command, root, allowlist):
        return True

    return False


def main():
    payload = load_payload()
    root = get_root(payload)
    allowlist = load_allowlist()

    if not is_destructive_command(payload, root, allowlist):
        return

    print("Destructive command blocked by hook. Do not delete content", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
