# Implementation plan: `context-doctor` skill + hooks

**Status:** not started. **Owner of this doc:** whoever picks it up next — read
this file plus the citations inside it; nothing else. No prior conversation
context is assumed.

## Mission

rig's `.context/` system-map (built by the vendored `icm-architect` skill,
System map form) has no mechanism that keeps itself current once a repo is
under active development. Two problems, currently both unhandled:

1. **Bloat** — `.context/*.md` files can grow past a healthy size with no
   flag. A hook already exists for this
   ([hooks/context/context-size-check.py](../hooks/context/context-size-check.py))
   but only matches files literally named `context.md` — it is blind to
   `objects/*.md` cards, `processes/*.md`, `effects/CONTEXT.md`, etc. This bug
   is already tracked in [docs/TODO.md](TODO.md) under "Hooks".
2. **Staleness** — nothing tells an agent that changing `agents/foo.md`
   should also prompt a refresh of `.context/objects/agents.md`. The only
   existing routing (`.context/effects/CONTEXT.md`) is read-direction only
   ("if you're changing X, open these cards first") — there is no
   write-back direction ("...then update these after").

This plan builds a new, rig-owned skill (`context-doctor`) plus two hooks
that close both gaps, and folds the manual two-command setup
(`/icm-architect` then a second bootstrap step) into a single
`/context-doctor init`.

## Hard constraints — do not violate

- **Never edit anything under `skills/icm-architect/`.** That folder is
  vendored, third-party, MIT-licensed (© Jake Van Clief — see
  `skills/icm-architect/LICENSE`), pulled in wholesale
  (`git log --oneline -- skills/icm-architect` shows exactly two commits:
  "Added ICM-architect skill", "ICM Architect skill update"). An upstream
  update would silently clobber any edit made there. All new behavior lives
  in new, rig-owned files instead.
- **No changes to `install.js` or `manifest.json`.** Both hooks and skills
  are auto-discovered by directory walk — confirmed by reading
  `install.js`'s `findHookDescriptors` (walks the whole `hooks/` tree for
  `*.hook.json` siblings, no registry) and the existing pattern in
  [.context/objects/hooks.md](../.context/objects/hooks.md). A new
  `skills/<name>/SKILL.md` folder and a new `hooks/<name>/*.hook.json` pair
  are true drop-ins.
- **Every rig-managed `.context/` map is rooted at `.context/`, never
  `map/`.** `icm-architect`'s own default (`references/system-map.md`,
  "Propose before writing... Prefer a `map/` shelf") is overridden by
  explicit instruction every time `context-doctor` invokes it. Precedent for
  this exact override already exists in this repo:
  [.context/decisions/2026-08-29-context-restructure-to-dot-context.md](../.context/decisions/2026-08-29-context-restructure-to-dot-context.md).
  Because of this standardization, hooks may hardcode `.context/` as the map
  root — no dual-name detection needed.
- **Do not remove `icm-architect`'s own content-review human gates.**
  `system-map.md`'s audit pipeline ("Stop after each slice. A person or a
  cold walk reads the output before the next slice starts.") stays intact.
  `context-doctor` only pre-decides two things that were previously an
  interactive proposal — which form (System map) and which folder name
  (`.context/`) — it does not skip the inventory/catalog/nouns/verbs/effects
  approval stops.
- **Skills cannot call each other directly.** There is no nested/recursive
  skill execution. One skill's instructions can only tell the *executing
  agent* to invoke the `Skill` tool a second time by name. `context-doctor`'s
  `SKILL.md` must contain an explicit instruction telling the agent to do
  this, with a literal `args` string — it cannot assume automatic dispatch.

## Deliverables

1. `skills/context-doctor/SKILL.md` (new)
2. `hooks/context/context-size-check.py` (bug fix — edit in place, it's
   rig-owned)
3. `hooks/context-doctor/staleness-check.py` +
   `hooks/context-doctor/staleness-check.hook.json` (new)
4. `docs/TODO.md` — remove the "Change the context hook..." line under
   Hooks once step 2 is done (it will be resolved)

No new skill folders under `skills/icm-architect/`. No touches to
`agents/`, `manifest.json`, `install.js`, `rules/`.

---

## Build sequence (human-gated)

Follow icm-architect's own house style: stop after each numbered step and
let a human read the output before continuing. Do not batch steps.

### Step 0 — Confirm the environment (no writes)

Read, don't write:
- [hooks/context/context-size-check.py](../hooks/context/context-size-check.py)
  and its `.hook.json` sibling, in full — this is the pattern every new hook
  in this plan must match (stdin JSON payload, upsert/remove log pattern,
  `PostToolUse` on `Write|Edit`, `targets: ["claude"]`).
- [.context/effects/CONTEXT.md](../.context/effects/CONTEXT.md) — the
  existing read-direction table this plan adds a write-direction sibling to.
- [.context/objects/_index.md](../.context/objects/_index.md) — the noun
  list `context-doctor` will read at init time to build the new table.
- [AGENTS.md](../AGENTS.md) — the entry file that gets one new routing row.
- An existing installed skill's `SKILL.md` frontmatter (e.g.
  `skills/icm-architect/SKILL.md` lines 1-4) for the exact frontmatter shape
  to copy (`name`, `description` — no other keys).

**Human gate:** confirm you've read all five before writing anything.

### Step 1 — Fix the size-check hook (resolves the tracked TODO)

Edit [hooks/context/context-size-check.py](../hooks/context/context-size-check.py):

- Replace the filename check
  (`os.path.basename(file_path).lower() != "context.md"`) with a path check:
  the file counts if it lives anywhere under a `.context/` directory
  relative to `project_root` (i.e. `.context` is a path component between
  the project root and the file). Any filename under that tree counts, not
  just files named `context.md`.
- Keep everything else identical: `LINE_THRESHOLD = 300`, the
  `CONTEXT_SIZE_LOG.md` upsert/remove logic, the `PostToolUse`/`Write|Edit`
  matcher, `targets: ["claude"]`. This is a scope-of-match fix only, not a
  rewrite.
- Update the module docstring's second sentence (currently says "a file
  named CONTEXT.md") to describe the new, broader match.

**Human gate:** run the hook by hand against a synthetic payload before
moving on — e.g.:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":".context/objects/agents.md"},"cwd":"'"$(pwd)"'"}' \
  | python3 hooks/context/context-size-check.py
```
Confirm it now inspects `objects/agents.md` (it won't be over 300 lines
today, so expect no log entry — the point is that it *no longer skips the
file solely because of its name*). Then repeat with `.context/CONTEXT.md`
to confirm the old case still works.

Once confirmed, remove the resolved line from
[docs/TODO.md](TODO.md)'s "Hooks" section.

### Step 2 — Write `skills/context-doctor/SKILL.md`

Frontmatter (match the shape read in Step 0):

```yaml
---
name: context-doctor
description: Bootstrap and maintain a rig-managed .context/ system-map so it stays current as code changes — sets up the map via icm-architect on first run, then tracks and remediates staleness and bloat. Use when the user says "/context-doctor", "/context-doctor init", "set up context tracking", "keep the context map current", or asks to initialize or refresh this repo's .context/ map.
---
```

Body must specify two branches, selected by the literal `args` text the
skill was invoked with:

**Branch A — `init`** (first-time setup; also runs if `.context/` doesn't
exist yet regardless of args):

1. Call the `Skill` tool a second time:
   `skill: "icm-architect"`, `args: "Restructure mode, System map form. Root the map at .context/ at the project root — do not propose or use map/. Run the normal audit pipeline (inventory, catalog, nouns, verbs, effects) with its usual human-gated stops."`
   State plainly in the SKILL.md that this is pre-deciding *only* form and
   location, and that the agent must still honor every stop-and-check
   `icm-architect` itself asks for during the audit.
2. Once `.context/objects/_index.md` and `.context/effects/CONTEXT.md`
   exist, read both.
3. Generate `.context/effects/UPKEEP.md` — a new file, deliberately
   *separate* from `effects/CONTEXT.md` (which `icm-architect` may
   regenerate on a future re-audit and would otherwise silently wipe this
   table). Table shape:

   ```markdown
   # effects/UPKEEP.md — write-back index

   Companion to effects/CONTEXT.md, but reversed: if you changed the file
   in the left column, the card in the right column needs re-verifying
   (status/date/citations) against the new source. Generated by
   context-doctor init from objects/_index.md — do not hand-edit; re-run
   context-doctor to regenerate.

   | Source changed | Refresh after |
   |---|---|
   | `agents/*.md` | [../objects/agents.md](../objects/agents.md) |
   | `skills/<name>/` | [../objects/skills.md](../objects/skills.md) |
   | `hooks/<name>/*.py` or `*.hook.json` | [../objects/hooks.md](../objects/hooks.md) |
   | `manifest.json` | [../objects/manifest.md](../objects/manifest.md) |
   | `install.js` | [../processes/install.md](../processes/install.md) |
   ```

   (The actual rows must be derived from whatever `objects/_index.md`
   contains in the target repo at init time — the table above is this
   repo's expected shape, not a hardcoded template to copy verbatim into
   every install.)
4. Add exactly one new row to the target repo's root entry file (`AGENTS.md`
   or `CLAUDE.md`, whichever exists — see the existing "Common tasks" /
   routing table in [AGENTS.md](../AGENTS.md) for the pattern), e.g.:
   `**What context needs refreshing after I change X?** → .context/effects/UPKEEP.md`

**Human gate:** stop after Branch A completes and show the generated
`UPKEEP.md` plus the diff to the entry file before considering init done.

**Branch B — no args / bare `/context-doctor`** (maintenance pass, only
valid once `.context/` already exists):

1. Read `CONTEXT_SIZE_LOG.md` and `CONTEXT_STALE_LOG.md` (from Step 3
   below) at the project root, if present.
2. For each bloat entry: open the file, split or compress it back under 300
   lines (this reuses `icm-architect`'s own re-verify judgment — restate the
   relevant checklist from `references/system-map.md` step 5 in this
   SKILL.md's own words rather than instructing the agent to open that file
   at runtime, so this skill doesn't silently break if the vendored file's
   internal structure changes upstream).
3. For each staleness entry: open the named card and the source path that
   triggered it, re-verify the card's claims, update
   `status:`/date/citations.
4. Remove resolved entries from both logs as they're fixed (mirror the
   upsert/remove pattern already used by `context-size-check.py`).

**Human gate:** present the list of remediated files before writing; do not
auto-fix silently in bulk.

### Step 3 — Write the staleness hook

New files:

`hooks/context-doctor/staleness-check.hook.json`:
```json
{
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "runtime": "python3",
  "script": "staleness-check.py",
  "targets": ["claude"]
}
```

`hooks/context-doctor/staleness-check.py` — model this closely on
`hooks/context/context-size-check.py`'s structure (same stdin-JSON-payload
pattern, same `resolve_file_path`-style helper, same log-upsert style, but a
new log file `CONTEXT_STALE_LOG.md`):

1. Parse `.context/effects/UPKEEP.md`'s table (skip if the file doesn't
   exist yet — a repo that hasn't run `context-doctor init` has nothing to
   check).
2. If the edited path matches a `Source changed` pattern (glob-style prefix
   match, e.g. `agents/*.md` matches `agents/foo.md`): upsert a line into
   `CONTEXT_STALE_LOG.md` naming the mapped "Refresh after" card, unless an
   entry for that card is already pending.
3. If the edited path *is* one of the "Refresh after" targets itself:
   remove any pending entry naming it (it just got refreshed).
4. No cross-call session state beyond the log file — same as the size hook.

**Human gate:** test by hand with synthetic payloads before considering this
step done:

```bash
# simulate editing a mapped source file — should add a pending entry
echo '{"tool_name":"Write","tool_input":{"file_path":"agents/new-agent.md"},"cwd":"'"$(pwd)"'"}' \
  | python3 hooks/context-doctor/staleness-check.py
cat CONTEXT_STALE_LOG.md

# simulate refreshing the mapped card — should remove that entry
echo '{"tool_name":"Edit","tool_input":{"file_path":".context/objects/agents.md"},"cwd":"'"$(pwd)"'"}' \
  | python3 hooks/context-doctor/staleness-check.py
cat CONTEXT_STALE_LOG.md   # entry should be gone
```

### Step 4 — End-to-end dry run

In a scratch copy of a small unrelated repo (not this one — use
`/private/tmp/claude-.../scratchpad` or similar):

1. `node install.js --target-dir=<scratch repo>` and confirm
   `context-doctor`'s skill folder and both hooks land in `.claude/`.
2. Run `/context-doctor init` inside that scratch repo and confirm:
   - it invokes `icm-architect` with the scripted `args` (form + location
     pinned), and `icm-architect`'s own audit stops still fire for approval
   - `.context/` ends up at the project root, never `map/`
   - `effects/UPKEEP.md` is generated and the entry file gets its one new
     routing row
3. Make a trivial edit to a mapped source file in that scratch repo through
   Claude Code and confirm `CONTEXT_STALE_LOG.md` picks it up.
4. Run `/context-doctor` (no args) and confirm it reads and clears the log.

**Human gate:** do not consider this plan complete until the dry run in
Step 4 has been observed end-to-end by a person, not just asserted.

### Step 5 — Land it

Only after Step 4 is confirmed:
- Stage the three new/changed source paths plus the `docs/TODO.md` edit.
- Do not touch `.claude/`/`.github/` in *this* repo (rig) — those are
  install output here, not source (see
  [.context/CONTEXT.md](../.context/CONTEXT.md)).
- Normal commit flow from here; nothing in this plan authorizes a push.

---

## Explicit non-goals (do not do these unless separately asked)

- Do not add `github-copilot` as a `targets` value for either hook — no
  existing hook in this repo has adapted its payload parsing for Copilot's
  tool taxonomy yet (see
  [.context/decisions/2026-08-28-github-copilot-install-target.md](../.context/decisions/2026-08-28-github-copilot-install-target.md)),
  and neither should this one without that separate work.
- Do not build detection for a `map/`-rooted install. Standardizing on
  `.context/` is the whole point of routing setup through `context-doctor`;
  a repo that bypasses it by calling bare `icm-architect` is out of scope.
- Do not have `context-doctor` silently auto-fix bloat/staleness with no
  human check — Branch B's human gate above is load-bearing, not optional.
