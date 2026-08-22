---
name: interview
description: Interview the user about a plan, decision, or idea until a shared understanding is reached. Use when you want to ask the user any question, the user wants to stress-test their thinking, wants to plan something, asks for an ambiguous task execution, or uses any 'interview' or 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Number questions once, continuing across the whole session (Q1, Q2, Q3, ...); never restart the count in a later round and never reuse a number.

Each question must be **atomic**: it asks exactly one thing, has no "and"/"or" joining two separate decisions, and does not smuggle in an assumption the user hasn't confirmed. If a question needs a compound answer, split it into separate questions instead.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Prune branches that don't change the deliverable: if a decision wouldn't alter what gets built or written, drop it instead of asking it.

Handle contradictions explicitly. If the user provides contradicting answers that imply conflicting rules in the same or across rounds the questions were not explicit enough. Do not silently pick one answer, ask for clarification through new clearly defined atomic questions and use the new answers.

Finding _facts_ is your job, never the user's; don't ask the user for anything you could look up yourself. Never call filesystem or search tools yourself to find a fact — their raw output pollutes your context. Instead, dispatch the `context-explorer` sub-agent with the exact question you need answered, and use only its returned summary. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## Recording the outcome

Once the user confirms the shared understanding, write it to a markdown file before doing anything else:

1. Fill the template at [templates/decision-record.md](templates/decision-record.md) as a **distilled record, not a transcript**: summarize the session into `Why` and `Summary`, and list only the decisions that shaped the outcome under `Decisions` — do not restate every question and recommended answer verbatim. Mark the session `Type` as `Feature` if it produced enough to start building, or `Decision` otherwise, and fill whichever of `Spec` / `Trade-offs` doesn't apply with `N/A`.
2. Derive `<slug>` as the kebab-case form of the topic title (e.g. "Auth token refresh" → `auth-token-refresh`).
3. Save it to `.context/decisions/<YYYY-MM-DD>-<slug>.md` at the root of the project being worked on, creating `.context/decisions/` if it doesn't exist yet.
4. Report the file path to the user. This file, not the chat transcript, is the record of what was decided.
