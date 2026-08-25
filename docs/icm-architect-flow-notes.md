# ICM Architect — Flow Notes: New ICM Setup from a Working Code Project

Notes on the decision and construction flow the `icm-architect` skill uses when turning an **existing working code project** into an ICM workspace. This is the **Restructure mode** path (an existing folder/repo/vault that needs ICM structure), as opposed to **Build mode** (designing a workspace from a described process with no existing artifact).

## Sources read

- [skills/icm-architect/SKILL.md](skills/icm-architect/SKILL.md) — main skill instructions (mode selection, invariants, restructure steps, walk test, guardrails)
- [skills/icm-architect/references/core.md](skills/icm-architect/references/core.md) — five design principles, five-layer hierarchy, stage contract format, naming conventions, library rules, token discipline
- [skills/icm-architect/references/forms.md](skills/icm-architect/references/forms.md) — the five forms (Pipeline, Umbrella, Record library, Knowledge bundle, Context map)
- [skills/icm-architect/assets/templates/CLAUDE.md](skills/icm-architect/assets/templates/CLAUDE.md) — entry-file template
- [skills/icm-architect/assets/templates/CONTEXT.md](skills/icm-architect/assets/templates/CONTEXT.md) — root pipeline contract template
- [skills/icm-architect/assets/templates/stage-CONTEXT.md](skills/icm-architect/assets/templates/stage-CONTEXT.md) — stage-level contract template

## 1. Decision flow (mode + form selection)

```mermaid
flowchart TD
    Start["Working code project<br/>needs an ICM workspace"] --> Ladder{"Is the work genuinely<br/>automated &amp; repeating?"}
    Ladder -->|"No — one-off or rarely repeats"| NoBuild["Don't build a workspace.<br/>Stay at chat / saved prompt / skill"]
    Ladder -->|"Yes"| ModeQ{"Does an existing folder/repo/vault<br/>already need restructuring,<br/>or are we designing fresh<br/>from a description?"}

    ModeQ -->|"Existing code project"| Restructure["Restructure mode"]
    ModeQ -->|"No artifact yet, only an idea"| Build["Build mode"]

    Build --> Dialogue["Extract structure from dialogue:<br/>repeating unit? stop-and-check points?<br/>stable vs new-per-run? what is 'done'?"]
    Dialogue --> FormPickB["Pick a form (forms.md)"]
    FormPickB --> Scaffold["Scaffold smallest structure,<br/>copy templates, write contracts"]

    Restructure --> Inventory["Inventory the tree<br/>(step 1)"]
    Inventory --> HiddenForm["Find the hidden form<br/>(step 2)"]
    HiddenForm --> FormPickR["Pick a form (forms.md)"]
    FormPickR --> Classify["Classify every file<br/>into 5 roles (step 3)"]

    FormPickB -.shared table.-> FormTable["Form choice table:<br/>Pipeline / Umbrella / Record library /<br/>Knowledge bundle / Context map"]
    FormPickR -.shared table.-> FormTable
```

**Citations:**
- Ladder / "don't over-structure" guardrail: [SKILL.md L98](skills/icm-architect/SKILL.md#L98)
- Mode choice ("Building from a described process" vs "An existing folder, repo, or vault that needs ICM structure"): [SKILL.md L29-L32](skills/icm-architect/SKILL.md#L29-L32)
- Build mode dialogue questions: [SKILL.md L36-L42](skills/icm-architect/SKILL.md#L36-L42)
- Form choice table (Pipeline/Umbrella/Record library/Knowledge bundle/Context map): [SKILL.md L46-L54](skills/icm-architect/SKILL.md#L46-L54), detailed in [references/forms.md L7-L17](skills/icm-architect/references/forms.md#L7-L17)
- Restructure mode step 1 (Inventory) and step 2 (Find the hidden form): [SKILL.md L64-L68](skills/icm-architect/SKILL.md#L64-L68)
- Step 3 (Classify every file): [SKILL.md L70](skills/icm-architect/SKILL.md#L70)

## 2. Construction flow — Restructure mode

This is the concrete build sequence once "working code project → ICM" has been chosen.

```mermaid
flowchart TD
    S1["1. Inventory before touching<br/>List the tree. Note: what it is,<br/>when last touched, what refers to it.<br/>Never delete or move yet."] --> S2

    S2["2. Find the hidden form<br/>Ask/infer: what's the repeating unit?<br/>Where does work enter/leave?<br/>Extract the pipeline/library/map<br/>already implicit in the code —<br/>don't replace it."] --> S3

    S3["3. Classify every file<br/>into one of 5 roles"] --> R1 & R2 & R3 & R4 & R5

    R1["Catalog<br/>identity/routing →<br/>CLAUDE.md / index files"]
    R2["Contract<br/>describes a step →<br/>CONTEXT.md"]
    R3["Factory<br/>stable reference →<br/>_shared/, _system/, references/"]
    R4["Product<br/>run-specific artifacts →<br/>stage output/ or record folders"]
    R5["Dead<br/>stale/duplicated/superseded →<br/>propose _archive/, never silently delete"]

    R1 & R2 & R3 & R4 & R5 --> S4

    S4{"4. Propose before moving<br/>Present target tree +<br/>migration map (old path → new path → role).<br/>HUMAN GATE: get approval."}
    S4 -->|"rejected / revise"| S2
    S4 -->|"approved"| S5

    S5["5. Migrate<br/>Move files. Write entry file + contracts<br/>from templates (CLAUDE.md, CONTEXT.md,<br/>stage-CONTEXT.md). De-duplicate toward<br/>one-home-per-fact (link, don't copy).<br/>Separate reusable method from this instance."] --> S6

    S6["6. Validate with the walk test"] --> WT{"Walk test passes?"}
    WT -->|"No — a check fails"| Fix["Fix the structure:<br/>move or split files.<br/>(Not: add more explanation.)"] --> S6
    WT -->|"Yes"| Done["ICM workspace ready:<br/>entry file + per-folder CONTEXT.md<br/>+ factory/product split in place"]
```

**Citations:**
- Step 1 Inventory: [SKILL.md L66](skills/icm-architect/SKILL.md#L66)
- Step 2 Find the hidden form: [SKILL.md L68](skills/icm-architect/SKILL.md#L68)
- Step 3 Classify every file + the 5 roles (Catalog/Contract/Factory/Product/Dead): [SKILL.md L70-L75](skills/icm-architect/SKILL.md#L70-L75)
- Step 4 Propose before moving (human gate on the migration map): [SKILL.md L77](skills/icm-architect/SKILL.md#L77)
- Step 5 Migrate (move, write entry file/contracts, de-duplicate, separate method from instance): [SKILL.md L79](skills/icm-architect/SKILL.md#L79)
- Step 6 Validate with the walk test: [SKILL.md L81](skills/icm-architect/SKILL.md#L81)
- The walk test itself (6 checks): [SKILL.md L83-L92](skills/icm-architect/SKILL.md#L83-L92)
- "If a step fails, fix the structure... by moving or splitting files": [SKILL.md L94](skills/icm-architect/SKILL.md#L94)
- Templates used at step 5:
  - Entry file shape (routing table, "where things live", "route by what just happened", one rule): [assets/templates/CLAUDE.md L1-L26](skills/icm-architect/assets/templates/CLAUDE.md#L1-L26)
  - Root pipeline contract shape (stage table, factory/product line, status-by-scanning rule): [assets/templates/CONTEXT.md L1-L12](skills/icm-architect/assets/templates/CONTEXT.md#L1-L12)
  - Stage contract shape (Inputs split working/reference, "Do NOT load", Process, Outputs, Human check): [assets/templates/stage-CONTEXT.md L1-L18](skills/icm-architect/assets/templates/stage-CONTEXT.md#L1-L18), full annotated example at [references/core.md L36-L59](skills/icm-architect/references/core.md#L36-L59)

## 3. Supporting concepts drawn on during construction

These aren't separate steps but are the rules the agent applies *while* doing steps 3 and 5 above.

| Concept | Where it's defined | Applied at |
|---|---|---|
| The ten invariants (one-folder-one-job, small entry file, numbering, explicit contracts, factory vs. product, edit surfaces, load-only-what's-needed, plain text, filesystem-as-state, instantiate-by-copying) | [SKILL.md L14-L27](skills/icm-architect/SKILL.md#L14-L27) | Checked throughout, esp. steps 3–6 |
| Five-layer context hierarchy (L0 entry → L1 root contract → L2 stage contract → L3 factory refs → L4 product/output) | [references/core.md L19-L32](skills/icm-architect/references/core.md#L19-L32) | Step 3 classification, step 5 writing contracts |
| Naming conventions (`NN_kebab-name` stages, underscore-prefixed system folders, one entry file per agent type) | [references/core.md L62-L69](skills/icm-architect/references/core.md#L62-L69) | Step 5 migrate |
| Library rules (catalog holds no books, one home per fact, generated indexes never hand-edited) | [references/core.md L71-L78](skills/icm-architect/references/core.md#L71-L78) | Step 5 de-duplication |
| Token discipline (2k–8k tokens per stage load) | [references/core.md L80-L82](skills/icm-architect/references/core.md#L80-L82) | Step 6 walk test |
| The five forms (Pipeline/Umbrella/Record library/Knowledge bundle/Context map) in depth | [references/forms.md L19-L143](skills/icm-architect/references/forms.md#L19-L143) | Step 2, form selection |
| Guardrails (don't over-structure, where ICM loses, anti-patterns) | [SKILL.md L98-L100](skills/icm-architect/SKILL.md#L98-L100) | Before step 1 and throughout |
