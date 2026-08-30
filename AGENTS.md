This file provides guidance to coding agents when working with code in this repository.

# rig

AI overhead system — a shared factory of agents, skills, hooks, and rules for AI
coding assistants, installed into other project repos via `install.js`.

## Where things live

| Path | What |
|---|---|
| `agents/` | Agent definitions (one `.md` file per agent) — see [.context/objects/agents.md](.context/objects/agents.md) |
| `skills/` | Skill packages (one subfolder per skill, each with its own `SKILL.md`) — see [.context/objects/skills.md](.context/objects/skills.md) |
| `hooks/` | Hook scripts, each paired with a `<name>.hook.json` descriptor — see [.context/objects/hooks.md](.context/objects/hooks.md) |
| `rules/` | Rule files — category defined in `manifest.json`, no assets yet (ghost — see [.context/objects/_index.md](.context/objects/_index.md)) |
| `manifest.json` | Catalog: maps each asset category to where it lands per target platform (`.claude/`, `.github/`) — see [.context/objects/manifest.md](.context/objects/manifest.md) |
| `install.js` | The installer — copies `agents/`, `skills/`, `hooks/`, `rules/` into a target project per `manifest.json` — see [.context/processes/install.md](.context/processes/install.md) |
| `.context/` | The repo's own context map (this repo is code other agents edit) — start at [.context/CONTEXT.md](.context/CONTEXT.md) |

## Common tasks

- **Add a new agent** → drop a `.md` file into `agents/`, see [.context/objects/agents.md](.context/objects/agents.md)
- **Add a new skill** → new subfolder in `skills/` with a `SKILL.md`, see [.context/objects/skills.md](.context/objects/skills.md)
- **Add a new hook** → drop a `<name>.py`/`.sh` plus `<name>.hook.json` into `hooks/`, see [.context/objects/hooks.md](.context/objects/hooks.md)
- **Add a new install target platform** → add an entry to `manifest.json` under `targets`, see [.context/objects/manifest.md](.context/objects/manifest.md) (or [README.md](README.md))
- **Install this repo into a project** → `node install.js --target-dir=<path>`, see [.context/processes/install.md](.context/processes/install.md) (or [README.md](README.md) for flags)
- **"What breaks if I change X?"** → [.context/effects/CONTEXT.md](.context/effects/CONTEXT.md)
- **What context needs refreshing after I change X?** → [.context/effects/UPKEEP.md](.context/effects/UPKEEP.md)
- **Why was a past decision made?** → [.context/decisions/](.context/decisions/)
