This file provides guidance to coding agents when working with code in this repository.

# rig

AI overhead system — a shared factory of agents, skills, hooks, and rules for AI
coding assistants, installed into other project repos via `install.js`.

## Where things live

| Path | What |
|---|---|
| `agents/` | Agent definitions (one `.agent.md` file per agent) — see [agents/CONTEXT.md](agents/CONTEXT.md) |
| `skills/` | Skill packages (one subfolder per skill, each with its own `SKILL.md`) — see [skills/CONTEXT.md](skills/CONTEXT.md) |
| `hooks/` | Hook scripts — category defined in `manifest.json`, no assets yet |
| `rules/` | Rule files — category defined in `manifest.json`, no assets yet |
| `manifest.json` | Catalog: maps each asset category to where it lands per target platform (`.claude/`, `.github/`, `.cursor/`) |
| `install.js` | The installer — copies `agents/`, `skills/`, `hooks/`, `rules/` into a target project per `manifest.json` |
| `CONTEXT.md` | How this repo works end-to-end: factory → install → target repo |

## Common tasks

- **Add a new agent** → drop a `.agent.md` file into `agents/`, see [agents/CONTEXT.md](agents/CONTEXT.md)
- **Add a new skill** → new subfolder in `skills/` with a `SKILL.md`, see [skills/CONTEXT.md](skills/CONTEXT.md)
- **Add a new install target platform** → add an entry to `manifest.json` under `targets` (see [README.md](README.md))
- **Install this repo into a project** → `node install.js --target-dir=<path>` (see [README.md](README.md) for flags)
