#!/usr/bin/env python3
"""
PreToolUse hook: denies AskUserQuestion calls and redirects the agent to
the `interview` skill instead, so every user-facing question goes through
that skill's numbered, atomic, recommend-an-answer question format rather
than the raw AskUserQuestion UI.
"""

import json
import sys


def load_payload():
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def main():
    payload = load_payload()
    if payload.get("tool_name") != "AskUserQuestion":
        return

    print(
        "AskUserQuestion is disabled in this project. Invoke the Skill tool "
        'with skill="interview" instead, and ask the user through its '
        "question format.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
