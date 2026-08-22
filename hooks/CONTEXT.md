# hooks/ contract

One script per hook, paired with a same-directory `<name>.hook.json`
descriptor that declares how it wires into a Claude Code hook event.

Hooks may be grouped into subfolders (e.g. `hooks/context/`,
`hooks/git/`) — `install.js` walks the whole tree, so nesting is purely
organizational. A script and its descriptor must live in the same directory
as each other, but that directory can be anywhere under `hooks/`.

## Format

- `<name>.py` (or `.sh`) — the hook script. Reads the Claude Code hook JSON
  payload from stdin (fields like `tool_name`, `tool_input`, `cwd`) and exits
  0 on success.
- `<name>.hook.json` — descriptor consumed by `install.js`, in the same
  directory as its script:
  ```json
  {
    "event": "PostToolUse",
    "matcher": "Write|Edit",
    "runtime": "python3",
    "script": "<name>.py"
  }
  ```
  `script` is just the filename (no path) — `install.js` resolves it relative
  to wherever the descriptor itself ends up after copying, so the pair keeps
  working no matter how deep it's nested. `runtime` defaults to `python3` if
  omitted.

`install.js` copies scripts/descriptors like any other asset (preserving
subfolder structure), then — for the `claude` target only — merges every
descriptor it finds into the target project's `.claude/settings.json` under
`hooks.<event>`, so each hook is live immediately after install with no
manual wiring. The merge is idempotent (re-running install won't duplicate
the entry) and additive (it won't touch other hooks already in that file).

Hook descriptors are Claude Code-specific (`settings.json` event/matcher
semantics). Other platforms in `manifest.json` (e.g. `github-copilot`, which
maps `hooks` to `.github/workflows`) still receive the raw script file via the
generic copy, but nothing currently translates it into that platform's native
automation — that's out of scope until a target needs it.

## Adding a new hook

1. Pick (or create) a category subfolder, e.g. `hooks/<category>/`.
2. Create `<name>.py` inside it.
3. Create the matching `<name>.hook.json` descriptor alongside it.
4. Keep the script single-purpose and side-effect-scoped to what its event
   needs — it ships to every installed project, so it must be safe to run
   unattended.

## Current hooks

- `context/context-size-check.py` — after a `Write`/`Edit` produces a
  `context.md` over 300 lines, upserts that file's path into
  `CONTEXT_SIZE_LOG.md` at the project root (removing the entry again if the
  file drops back under the threshold). Feeds the future context-doctor
  pipeline, which will use that log to find files needing review,
  compression, or splitting.
- `deny-remove/deny-remove.py` - denies Bash commands that delete files or
  directories: standalone commands (`rm`, `unlink`, `shred`, `find -delete`)
  and delete calls embedded in inline scripts (`os.remove`, `shutil.rmtree`,
  `fs.unlink`, `Path(...).unlink()`, ...). `git clean -f` is always blocked
  (not path-scoped). A target path is allowed if it falls under an entry in
  `deny-remove.allow.json` (see Allowlists below); nothing is allowed by
  default. A blocklist over command text, not a sandbox — see the script's
  module docstring for the gap and stronger alternatives.
- `deny-non-rel-path/deny-non-rel-path.py` - denies the agent from reading
  or writing any path that resolves outside the project root (including
  `../` traversal). Exact for `Read`/`Write`/`Edit`/`NotebookEdit`/`Glob`/
  `Grep`; best-effort text scan for `Bash`. Nothing outside root is allowed
  by default; opt a path in via `deny-non-rel-path.allow.json` (see
  Allowlists below).
- `ask-question/ask-question.py` - denies `AskUserQuestion` tool calls and
  tells the agent to use the `interview` skill instead, so user-facing
  questions go through that skill's format.
- `deny-allowlist-edit/deny-allowlist-edit.py` - denies the agent from
  writing to any `*.allow.json` file (the exception lists below), so those
  can only be edited by a human. Exact for `Write`/`Edit`/`NotebookEdit`;
  best-effort text scan for `Bash` (redirection, `tee`, `sed`/`perl -i`,
  inline-script file writes).

## Allowlists

`deny-remove` and `deny-non-rel-path` each read an optional
`<name>.allow.json` file from their own hook directory (next to the
script, not in the source tree unless a human puts it there — install.js
only copies files present in source, so one created at the installed
location survives reinstalls):

```json
{
  "allowed_paths": ["/absolute/path/to/allow"]
}
```

A checked path is permitted if it equals, or is a subdirectory of, one of
`allowed_paths`. Empty/missing file means nothing is allowed. Only a
human should ever edit these files — `deny-allowlist-edit` blocks the
agent from doing so itself.
