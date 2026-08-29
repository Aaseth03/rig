# GitHub Copilot `.github/` configuration spec

Reference for every customization surface GitHub Copilot reads out of a
repository's `.github/` folder — custom agents, custom instructions, prompt
files, skills, and hooks. Written to be enough on its own to build any of
these from scratch, without re-deriving conventions from trial and error.

Confidence note: most sections below are sourced from an official
`docs.github.com` reference page with a fully enumerated schema (linked per
section). Prompt files are the exception — GitHub's docs show one working
example but don't publish a single enumerated frontmatter field list, so that
section is marked accordingly. Verify against the linked page if a specific
field's behavior matters for what you're building.

## Directory map

```
.github/
├── copilot-instructions.md       # repo-wide instructions, always on
├── instructions/
│   └── <name>.instructions.md    # path-scoped instructions (applyTo)
├── prompts/
│   └── <name>.prompt.md          # slash-command prompt templates
├── agents/
│   └── <name>.agent.md           # custom agent profiles
├── skills/
│   └── <name>/
│       └── SKILL.md              # agent skills (+ supporting files)
└── hooks/
    └── <name>.json               # hook configuration (event -> actions)
```

Skills also work from `.claude/skills/` or `.agents/skills/` in the same
repo (Agent Skills is a cross-tool open standard) — see the Skills section.

**Hook scripts have no mandated location.** Unlike Claude Code (which
requires a script to sit next to its `.hook.json` descriptor), a Copilot
hook's `bash`/`powershell`/`command` value is just a shell command string —
it can inline the logic directly, or point at a script file anywhere in the
repo. GitHub's own example puts them in a top-level `scripts/` folder next
to the `.github/hooks/<name>.json` that references them (see
[§5](#5-hooks--githubhooksjson)), but nothing stops you from colocating the
script inside `.github/hooks/` itself if you prefer that layout.

---

## 1. Custom agents — `.github/agents/*.agent.md`

Source: [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [About custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents)

One Markdown file per agent, YAML frontmatter + a Markdown body that is the
agent's system prompt (max 30,000 characters).

**File naming:** any unique name using only `. - _ a-z A-Z 0-9`, saved as
`<name>.agent.md`. The name (minus the extension) is also the dedup key
across enterprise/org/repo levels — repo-level always wins over org, org
always wins over enterprise.

### Frontmatter fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `description` | string | — | **Required.** Purpose and capabilities. |
| `name` | string | — | Display name. |
| `target` | string | both | `vscode` or `github-copilot`; omit to allow both. |
| `tools` | list or string | all | Tool names/aliases; YAML array or comma-separated string. |
| `model` | string | inherited | Model that executes the agent. |
| `disable-model-invocation` | boolean | `false` | Prevents the runtime from auto-selecting this agent. |
| `user-invocable` | boolean | `true` | Whether a human can select it manually. |
| `mcp-servers` | object | — | Extra MCP servers/tools (GitHub.com and CLI only). |
| `metadata` | object | — | Free-form key/value annotation. |

`infer` is retired — use `disable-model-invocation` instead. `argument-hint`
and `handoffs` are not supported for the GitHub.com cloud agent.

### `mcp-servers` schema

```yaml
mcp-servers:
  server-name:
    type: 'local'              # maps from 'stdio'
    command: 'executable-command'
    args: ['--arg1', '--arg2']
    tools: ["*"]                # or specific tool names
    env:
      ENV_VAR: ${{ secrets.VARIABLE_NAME }}
      # supported forms: $VAR, ${VAR}, ${VAR:-default}, ${{ secrets.VAR }}, ${{ vars.VAR }}
```

MCP server resolution order: built-in servers first, then custom-agent
config, then repository settings — each level can override the previous.

### Complete example

```markdown
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
tools: ["read", "search", "edit"]
model: claude-3-5-sonnet-20241022
disable-model-invocation: false
user-invocable: true
---

You are an expert code reviewer. Analyze pull requests for:

- Code quality and maintainability
- Security vulnerabilities
- Performance optimizations
- Test coverage gaps

Provide constructive feedback with specific suggestions.
```

---

## 2. Custom instructions

Source: [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)

Two forms, both plain Markdown, no `.agent.md`-style compound extension.

### 2a. Repo-wide — `.github/copilot-instructions.md`

Always-on, loads on every request across the whole repo. No frontmatter —
just natural-language Markdown.

```markdown
This is a Node.js CLI tool. Prefer async/await over callbacks. All new
commands must have a corresponding test in tests/.
```

### 2b. Path-scoped — `.github/instructions/<name>.instructions.md`

Frontmatter is **required**, keyed on `applyTo` (glob syntax, comma-separated
for multiple patterns):

```markdown
---
applyTo: "app/models/**/*.rb"
---

Use ActiveRecord validations instead of manual checks in `save`.
```

Multiple patterns:

```yaml
applyTo: "**/*.ts,**/*.tsx"
```

Optional `excludeAgent` scopes the file away from a specific consumer
(`code-review` or the cloud agent):

```yaml
---
applyTo: "**"
excludeAgent: "code-review"
---
```

### Precedence

1. Personal instructions (highest)
2. Repository instructions (path-scoped and repo-wide)
3. Organization instructions (lowest)

When a file matches both a path-scoped `*.instructions.md` and the repo-wide
`copilot-instructions.md`, **both** apply together — they don't override
each other.

---

## 3. Prompt files — `.github/prompts/*.prompt.md`

Source: [Your first prompt file](https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/your-first-prompt-file) — confirmed fields only; GitHub doesn't publish a single enumerated field list for this file type the way it does for agents/hooks/skills.

Markdown files with YAML frontmatter, invoked as a `/name` slash command in
Copilot Chat (name defaults to the filename if unset).

**Confirmed fields:**

| Field | Notes |
|---|---|
| `agent` | Which agent runs the prompt (`ask`, `edit`, `agent`, or a custom agent name). Defaults to the currently selected agent. |
| `description` | What the prompt does. |

Community usage (awesome-copilot, VS Code docs) also shows `model` and
`tools` fields controlling model choice and tool access respectively, and
notes that setting `tools` while the agent is `ask`/`edit` implicitly
switches it to `agent` — but confirm against current docs before relying on
exact behavior, since this wasn't in the one page GitHub publishes with a
worked example.

Prompt bodies support `${input:name:placeholder}` template variables, filled
in when the prompt is invoked.

### Example

```markdown
---
agent: 'agent'
description: 'Generate a clear code explanation with examples'
---

Explain the following code in a clear, beginner-friendly way:

Code to explain: ${input:code:Paste your code here}
Target audience: ${input:audience:Who is this explanation for?}

Please provide:

* A brief overview of what the code does
* A step-by-step breakdown of the main parts
* Explanation of any key concepts or terminology
* A simple example showing how it works
* Common use cases or when you might use this approach
```

Invoked in chat as `/generate-explanation` (filename minus `.prompt.md`).

---

## 4. Skills — `<name>/SKILL.md`

Source: [Adding agent skills for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)

Agent Skills is a cross-tool open standard (works the same in Copilot VS
Code, Copilot CLI, Copilot cloud agent, and Claude Code). A skill is a
directory containing a `SKILL.md` plus any supporting scripts/resources.

**Valid project-level locations** (any of these in a repo):
- `.github/skills`
- `.claude/skills`
- `.agents/skills`

**Personal (cross-project) locations:**
- `~/.copilot/skills`
- `~/.agents/skills`

### Naming rules

- Skill directory name: lowercase, hyphens for spaces (e.g. `webapp-testing`).
- The file inside it must be named exactly `SKILL.md`.
- The `name` frontmatter field follows the same lowercase-hyphen convention
  and typically matches the directory name.

### Frontmatter fields

| Field | Type | Required |
|---|---|---|
| `name` | string | Yes |
| `description` | string | Yes |
| `license` | string | No |
| `allowed-tools` | string | No — e.g. `allowed-tools: shell` pre-approves script execution. Only set this for a skill whose source you fully trust. |

### Complete example

```markdown
---
name: github-actions-failure-debugging
description: Guide for debugging failing GitHub Actions workflows.
  Use this when asked to debug failing GitHub Actions workflows.
---

To debug failing GitHub Actions workflows in a pull request, follow
this process, using tools provided from the GitHub MCP Server:

1. Use the `list_workflow_runs` tool to look up recent workflow runs
2. Use the `summarize_job_log_failures` tool to get an AI summary
3. If needed, use `get_job_logs` or `get_workflow_run_logs` for details
4. Try to reproduce the failure yourself
5. Fix the failing build
```

Copilot auto-discovers every file in the skill's directory once the skill is
invoked, so helper scripts referenced from the Markdown body (e.g.
`validate.sh`) are automatically available alongside it.

---

## 5. Hooks — `.github/hooks/*.json`

Source: [Hooks configuration](https://docs.github.com/en/copilot/reference/hooks-configuration), [About hooks for GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/hooks)

Each `.github/hooks/<name>.json` is **self-contained** — there is no central
settings file to merge into, unlike Claude Code. Copilot reads every JSON
file in the folder directly. Convention: one purpose-named file per hook
(`<name>.json`, where `<name>` describes what the hook does).

### Top-level shape

```json
{
  "version": 1,
  "disableAllHooks": false,
  "hooks": {
    "<eventName>": [ /* hook entries */ ]
  }
}
```

`disableAllHooks: true` skips every hook in the file without deleting it.

### Events

Both camelCase and PascalCase event names are accepted (they're aliases of
each other) — camelCase payload fields pair with camelCase event names,
PascalCase (`snake_case` fields, VS Code-compatible) pairs with PascalCase
event names.

| Event | Fires | Cloud agent |
|---|---|---|
| `sessionStart` / `SessionStart` | New or resumed session begins | Yes |
| `sessionEnd` / `SessionEnd` | Session terminates | Yes |
| `userPromptSubmitted` / `UserPromptSubmit` | User submits a prompt | Yes |
| `userPromptTransformed` | Runtime transforms the prompt before the model sees it | Yes |
| `preToolUse` / `PreToolUse` | Before each tool executes | Yes (non-interactive) |
| `postToolUse` / `PostToolUse` | After a tool completes successfully | Yes |
| `postToolUseFailure` / `PostToolUseFailure` | After a tool fails | Yes |
| `preCompact` / `PreCompact` | Context compaction begins | Yes (auto only) |
| `agentStop` / `Stop` | Agent finishes a turn | Yes |
| `subagentStart` | A subagent is spawned | Yes |
| `subagentStop` / `SubagentStop` | A subagent completes | Yes |
| `errorOccurred` / `ErrorOccurred` | An error occurs during execution | Yes |
| `permissionRequest` / `PermissionRequest` | Before the permission service runs | CLI only |
| `notification` / `Notification` | A system notification is emitted | CLI only |

### Entry type: `command`

```json
{
  "type": "command",
  "bash": "UNIX_COMMAND",
  "powershell": "WINDOWS_COMMAND",
  "command": "CROSS_PLATFORM_FALLBACK",
  "cwd": "RELATIVE_OR_ABSOLUTE_PATH",
  "env": { "VAR_NAME": "VALUE" },
  "timeoutSec": 30,
  "matcher": "OPTIONAL_REGEX"
}
```

- One of `bash` / `powershell` / `command` is required. Explicit `bash` or
  `powershell` overrides the generic `command` fallback on that platform.
- `cwd` — relative (to repo root) or absolute path. Script paths in `bash`/
  `powershell` are resolved relative to `cwd` when it's set, so a script
  that lives outside `.github/hooks/` just needs `cwd` pointing at its
  folder.
- `timeoutSec` — default 30.
- `matcher` — regex, compiled as `^(?:PATTERN)$` (must match the tool name
  in full, not just contain it).

**Referencing an external script file** — GitHub's own `userPromptSubmitted`
example keeps scripts in a top-level `scripts/` folder, separate from the
`.github/hooks/*.json` that wires them up:

```
scripts/
├── log-prompt.sh
└── log-prompt.ps1
.github/
└── hooks/
    └── log-prompt.json
```

```json
{
  "version": 1,
  "hooks": {
    "userPromptSubmitted": [
      {
        "type": "command",
        "cwd": "scripts",
        "bash": "./log-prompt.sh",
        "powershell": "./log-prompt.ps1"
      }
    ]
  }
}
```

### Entry type: `http`

```json
{
  "type": "http",
  "url": "https://hooks.example.com/endpoint",
  "headers": { "X-Custom-Header": "value" },
  "allowedEnvVars": ["GITHUB_TOKEN"],
  "timeoutSec": 30,
  "matcher": "OPTIONAL_REGEX"
}
```

`url` must be HTTPS for permission-related hooks. `allowedEnvVars` lists
which env vars may be interpolated into headers.

### Entry type: `prompt`

```json
{
  "type": "prompt",
  "prompt": "/analyze this codebase for security issues"
}
```

Injects a natural-language message or slash command into the session.

### Payload shapes (what a `command`/`http` hook receives)

`preToolUse` (camelCase / VS Code-compatible):

```typescript
// camelCase
{ sessionId, timestamp, cwd, toolName, toolArgs }
// VS Code-compatible
{ hook_event_name: "PreToolUse", session_id, timestamp, cwd, tool_name, tool_input }
```

`postToolUse` adds a result:

```typescript
{ sessionId, timestamp, cwd, toolName, toolArgs,
  toolResult: { resultType: "success", textResultForLlm: string } }
```

`postToolUseFailure` adds `error: string` instead of `toolResult`.

`sessionStart`:

```typescript
{ sessionId, timestamp, cwd, source: "startup" | "resume" | "new", initialPrompt? }
```

`agentStop` / `Stop`:

```typescript
{ sessionId, timestamp, cwd, transcriptPath, stopReason: "end_turn", stop_hook_active: boolean }
```

`subagentStart` / `subagentStop` add `agentName`, `agentDisplayName?`,
`agentDescription?` (start) or `agentId`, `agentType`, `response`,
`stopReason` (stop).

`errorOccurred`:

```typescript
{ sessionId, timestamp, cwd,
  error: { message, name, stack? },
  errorContext: "model_call" | "tool_execution" | "system" | "user_input",
  recoverable: boolean }
```

### Output a hook script should print to stdout

`preToolUse`:

```json
{ "permissionDecision": "allow|deny|ask", "permissionDecisionReason": "required when deny", "modifiedArgs": {} }
```

`postToolUse`:

```json
{ "modifiedResult": { "resultType": "success", "textResultForLlm": "..." }, "additionalContext": "..." }
```

`agentStop` / `subagentStop`:

```json
{ "decision": "block|allow", "reason": "required when block", "modifiedResponse": "subagentStop only" }
```

`permissionRequest` (CLI only): `{ "behavior": "allow|deny", "message": "...", "interrupt": false }`

Transient progress updates before the final decision:

```bash
echo '{"type": "progress", "message": "Checking...", "temporary": true}'
# ...work...
echo '{"permissionDecision": "allow"}'   # the final line must be one complete JSON object
```

### Exit codes (command hooks)

| Exit code | Behavior |
|---|---|
| `0` | Success; stdout parsed as the JSON output above. |
| `2` | Warning (except `preToolUse`/`permissionRequest`, where it **denies**); stderr shown to the user. |
| other non-zero | Fail-open, logged (except `preToolUse`, which fail-closed denies). |
| timeout | Fail-open; warning logged; execution continues. |

**`preToolUse` is fail-closed on errors** — a crash or non-zero exit
(including exit `2`) denies the tool call even if stdout claims
`permissionDecision: "allow"`. Timeouts are the one exception and stay
fail-open even for this event.

### Environment variables available to hook scripts

Cloud agent sandbox: `GITHUB_COPILOT_API_TOKEN`, `GITHUB_COPILOT_GIT_TOKEN`,
`COPILOT_AGENT_PROMPT` (the prompt the job was invoked with), `HOME=/root`.

CLI: `COPILOT_HOME` (default `~/.copilot/hooks/`),
`COPILOT_HOOK_ALLOW_LOCALHOST=1` (allow non-HTTPS localhost hooks).

### Security notes

- Cloud agent sandbox network is firewalled — only GitHub/Copilot hostnames
  are reachable by default; anything else needs an admin-configured allow
  rule.
- A hook `allow` never pre-approves a `requestSandboxBypass: true`
  permission request — the user is always asked for privilege escalation.
- Policy hooks (CLI only, admin-installed under
  `/etc/github-copilot/policy.d/` or
  `C:\ProgramData\GitHub\Copilot\policy.d\`) load before all other hooks and
  **cannot** be disabled by `disableAllHooks`.

### Worked examples

`preToolUse` gated on a matcher, cross-platform:

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "matcher": "bash|powershell",
        "bash": "./scripts/validate-command.sh",
        "powershell": ".\\scripts\\validate-command.ps1",
        "timeoutSec": 10,
        "env": { "POLICY_LEVEL": "strict" }
      }
    ]
  }
}
```

`postToolUse` logging to an external endpoint:

```json
{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "type": "http",
        "url": "https://audit.example.com/log",
        "headers": { "Authorization": "Bearer token", "Content-Type": "application/json" },
        "matcher": "bash|create|edit",
        "timeoutSec": 5
      }
    ]
  }
}
```

Multiple events in one file:

```json
{
  "version": 1,
  "disableAllHooks": false,
  "hooks": {
    "sessionStart": [
      { "type": "command", "bash": "echo 'Session started' >> ~/.copilot/audit.log" }
    ],
    "preToolUse": [
      { "type": "command", "bash": "./check-permissions.sh", "timeoutSec": 15 }
    ],
    "sessionEnd": [
      { "type": "command", "bash": "echo 'Session ended' >> ~/.copilot/audit.log" }
    ]
  }
}
```

---

## How this differs from Claude Code, at a glance

| | Claude Code | GitHub Copilot |
|---|---|---|
| Agents | `.claude/agents/<name>.md` | `.github/agents/<name>.agent.md` |
| Instructions | `CLAUDE.md` | `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` |
| Hooks location | merged into `.claude/settings.json` | standalone `.github/hooks/<name>.json` per hook |
| Hook script wiring | descriptor merged centrally, one command string | JSON entry inline in the same file, `bash`/`powershell`/`command` keys |
| Skills | `.claude/skills/<name>/SKILL.md` | same convention — also valid at `.github/skills/` or `.agents/skills/` |
