# rig — factory contract

## What this repo is

A **factory**: it holds reusable AI-assistant assets (agents, skills, hooks, rules)
that get copied — as-is — into other project repos. Nothing in this repo runs
against a real project directly; it only produces files that land in one.

## Reads (inputs)

- `agents/*.agent.md`
- `skills/<name>/SKILL.md` (+ that skill's own reference/asset files)
- `hooks/*` (category defined in `manifest.json`, no assets yet)
- `rules/*` (category defined in `manifest.json`, no assets yet)
- `manifest.json` — per-platform destination mapping

## Process

`install.js`, run from inside a target project (or pointed at one via `--target-dir`):

1. Loads `manifest.json`.
2. For each selected target platform, creates its dot-folder (`.claude/`, `.github/`, `.cursor/`, …).
3. For each asset category present in this repo, copies it into the mapped subpath,
   skipping files that already exist at the destination unless `--force` is passed.

## Writes (outputs)

- `<target-dir>/.claude/{agents,skills,hooks,rules}/…`
- `<target-dir>/.github/{copilot-agents,workflows}/…`
- `<target-dir>/.cursor/rules/…`

## Human check

Before committing an install into a target repo, review the diff there.
`--dry-run` shows what would be copied without touching disk; existing files are
left alone by default, so local edits in the target repo survive a re-run.
