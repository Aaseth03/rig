# skills/ contract

One subfolder per skill. Each subfolder is a self-contained Claude Skill package:
a `SKILL.md` (frontmatter: `name`, `description`) plus whatever `references/`,
`assets/`, or `templates/` that skill needs.

## Adding a new skill

1. Create `skills/<name>/SKILL.md`.
2. Keep supporting files inside that same subfolder — skills should not share
   reference material with each other. If two skills need the same thing, that's
   a sign it belongs in `agents/` instead, or as its own skill.
3. It ships to consumers via `install.js` and `manifest.json`'s `skills` mapping.

## Current skills

- `icm-architect/` — designs/restructures ICM workspaces
- `interview/` — structured requirements interview that produces a decision record
