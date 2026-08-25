# ICM-compared — v1 vs v2 skill structure

Diff between the two flow-notes captures: [icm-architect-flow-notes.md](icm-architect-flow-notes.md) (v1) and [icm-architect-flow-notes-v2.md](icm-architect-flow-notes-v2.md) (v2), for the "working code project → ICM" scenario. Underlying source diff is [skills/icm-architect/SKILL.md](skills/icm-architect/SKILL.md), [skills/icm-architect/references/forms.md](skills/icm-architect/references/forms.md), and the new [skills/icm-architect/references/system-map.md](skills/icm-architect/references/system-map.md).

## Summary

| | v1 | v2 |
|---|---|---|
| Modes at "Choose a mode" | 2: Build, Restructure | **3**: Build, Restructure, **System map** (direct route) |
| Forms | 5: Pipeline, Umbrella, Record library, Knowledge bundle, Context map | **6**: + **System map** |
| Path for "working code project" | Restructure mode (generic 6-step: inventory → find form → classify 5 roles → propose → migrate → walk test) | **System map form** (dedicated 6-slice audit pipeline: inventory → catalog → nouns → verbs → impact index → re-verify) |
| Effect on the codebase | Files get **moved/renamed** into ICM shape (migrate step) | Code is **left untouched**; a parallel `map/` shelf is built that **cites** it (`path:line`) |
| New templates | `CLAUDE.md`, `CONTEXT.md`, `stage-CONTEXT.md`, `node.md`, `schema.md`, `questionnaire.md` | + **`object.md`** (noun card), **`process.md`** (verb card) |
| New reference doc | — | **`references/system-map.md`** (full audit pipeline, card spec, form-specific walk test, failure modes) |
| Walk test | 6 generic checks | 6 generic checks **+ 1 System-map-only check**, plus a whole separate form-specific walk test in `system-map.md` |
| New vocabulary | — | **Universe** tags (`live` / `leftover` / `ghost`), **Hits / Does not hit** waterfall, **object/process cards**, `effects/` change-impact index |
| Placement guidance | Not specified (workspace root vs. repo root left open) | **Explicit**: `map/` shelf beside `developer-docs/`/`docs/`/vault root; never inside `src/`, never scattered through the mapped tree |

## What's new, in detail

### 1. A third mode: direct route to System map

v1's "Choose a mode" was a 2-way fork between Build and Restructure. v2 adds a third bullet that routes "a body of work later agents must edit (code, markdown, or mixed)" straight to the System map form, bypassing the generic Build/Restructure decision entirely for that case.

- v1: [SKILL.md L31-L32 (pre-update)](skills/icm-architect/SKILL.md#L31-L32) — 2 bullets only
- v2: [SKILL.md L31-L33](skills/icm-architect/SKILL.md#L31-L33) — 3rd bullet added, pointing at `references/system-map.md`

### 2. Sixth form: System map

`forms.md` was "The Five Forms" and is now "The Six Forms." The new section defines the form, its skeleton tree, defining moves, and watch-fors.

- v1 form table: 5 rows, [references/forms.md L11-L17 (pre-update numbering)](skills/icm-architect/references/forms.md#L11-L17)
- v2 form table: 6 rows (System map added), [references/forms.md L11-L18](skills/icm-architect/references/forms.md#L11-L18)
- v2 new section: [references/forms.md L145-L169](skills/icm-architect/references/forms.md#L145-L169)

### 3. A dedicated audit pipeline replaces generic restructuring for code

v1 sent a code project through Restructure mode's 6 steps (inventory, find hidden form, classify into Catalog/Contract/Factory/Product/Dead, propose, migrate, walk test) — the same steps used for reorganizing any messy folder or vault. That pipeline **moves files**.

v2's System map form has its own 6-slice pipeline (slice 0–5: inventory, catalog, nouns, verbs, impact index, re-verify), each one human-gated, defined entirely in the new [references/system-map.md L51-L90](skills/icm-architect/references/system-map.md#L51-L90). Critically, this pipeline **does not move the subject's files** — "the subject tree remains authoritative... the map cites it. The map never becomes a second spec" ([references/system-map.md L15-L17](skills/icm-architect/references/system-map.md#L15-L17)).

### 4. New artifact types: object cards and process cards

Two new templates formalize what a "node" is for a code/mixed tree — a noun (object) or a verb (process) — replacing the more generic `node.md` used by Record library / Context map:

- [assets/templates/object.md](skills/icm-architect/assets/templates/object.md) — 7 required sections per [references/system-map.md L92-L100](skills/icm-architect/references/system-map.md#L92-L100): one sentence, why this shape, shape (with citations), connected to, if you change this (Hits/Does not hit), surfaces, see
- [assets/templates/process.md](skills/icm-architect/assets/templates/process.md) — Input → Movement → Output, cited numbered steps, consumes/produces, Hits/Does not hit, surfaces, see

### 5. New vocabulary for code-specific ambiguity

Not present in v1 at all:

- **Universe tags** — `live` (in force), `leftover` (present but not the main path), `ghost` (named/filed but not wired) — [references/system-map.md L19-L23](skills/icm-architect/references/system-map.md#L19-L23). This addresses something v1 had no language for: code that exists but is dead, stubbed, or aspirational.
- **Hits / Does not hit** — a required "if you change this" waterfall on every card, first-order only, and explicitly naming the *wrong* obvious next guess — [references/system-map.md L165 (forms.md)](skills/icm-architect/references/forms.md#L165) and [references/system-map.md L98](skills/icm-architect/references/system-map.md#L98).
- **`effects/` change-impact index** — a catalog-only "if you're changing X, open these cards" file, explicitly forbidden from copying waterfalls itself — [references/system-map.md L84-L86](skills/icm-architect/references/system-map.md#L84-L86).

### 6. Placement question is now answered

A prior question in this session ("is it specified where the context files land in a repository?") was answered as *no* for v1 — intra-workspace placement was defined, but where the workspace sits inside a larger code repo was left as a judgment call.

v2 closes that gap for the code-project case specifically: "Prefer a `map/` shelf next to existing orientation (`developer-docs/`, `docs/`, vault root)... Do not drop a map inside `src/` or scatter cards through the tree you are mapping." — [references/system-map.md L27-L29](skills/icm-architect/references/system-map.md#L27-L29). It also specifies entry-file mechanics precisely: edit `CLAUDE.md`, generate `AGENTS.md` and `routing.md` as byte-identical twins, never hand-edit the twins — [references/system-map.md L31](skills/icm-architect/references/system-map.md#L31).

### 7. Walk test extended, not replaced

The generic walk test gained one bullet rather than being forked:

> "System map only: can a cold agent answer *what is X* and *what else moves if I change X* from `map/CLAUDE.md` plus one card? Extra checks are in `references/system-map.md`." — [SKILL.md L95](skills/icm-architect/SKILL.md#L95)

System map also carries its own standalone 6-point walk test at [references/system-map.md L102-L111](skills/icm-architect/references/system-map.md#L102-L111), which is stricter and code/citation-specific (e.g. "Follow one `See` link. Does it land on source, not another essay?").

## What stayed the same

- The ten invariants ([SKILL.md L14-L27](skills/icm-architect/SKILL.md#L14-L27)) — untouched, System map still obeys all ten.
- `references/core.md` — five design principles, five-layer hierarchy, stage contract format, naming conventions, library rules, token discipline: byte-for-byte unchanged.
- Build mode and Restructure mode's own step lists — unchanged for the cases they still own (non-code processes, and generic messy folders/vaults that aren't specifically "later agents will edit this").
- The core "propose before moving / human gate" discipline — v1's step 4 in Restructure mode and v2's slice 0 in System map both require explicit approval before any writing.

## Net effect for "new ICM setup from a working code project"

v1's answer was: *treat the repo like any messy folder — inventory it, find the hidden pipeline/library/map inside it, reclassify every file into one of five roles, propose a migration, move things.*

v2's answer is: *leave the repo alone; build a small, separate, cited map beside it that a later agent can walk to answer "what is this" and "what breaks if I touch it," using object/process cards, universe tags, and a change-impact index.* This is a materially different (and safer, less invasive) recommendation for real codebases, where migrating/renaming source files carries much higher risk than in a folder of markdown notes.
