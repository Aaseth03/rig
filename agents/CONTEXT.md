# agents/ contract

One `.md` file per agent, at this folder's top level (no subfolders).

## Format

YAML frontmatter (`description`, `tools`, `user-invocable`) followed by the
agent's system prompt in the body. See [context-explorer.agent.md](context-explorer.agent.md)
for the pattern: narrow tool access, an explicit constraints section, an explicit
output format.

## Adding a new agent

1. Create `<name>.md` here.
2. Keep it single-purpose — one job per agent.
3. It ships to consumers via `install.js` and `manifest.json`'s `agents` mapping;
   no other wiring is needed.
