# Orchestration & Subagents Reference

How to think about multi-agent features when deciding what to ship in a plugin. Load this when the captured workflow involves delegation, parallelism, or a specialized reusable role.

> Sources: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/agent-teams

## The honest landscape (don't invent primitives)

There is **no declarative "workflow" file** you put in a plugin. If a workflow needs orchestration, you encode it one of these ways:

| Mechanism | Status | What it is | Ship it in a plugin as… |
|---|---|---|---|
| **Subagents** | **Stable** | A focused, isolated-context helper that does one job and returns a result. Spawned via the Task/Agent tool. | `agents/<name>.md` (see `plugin-components.md`) |
| **Skill-described orchestration** | **Stable** | A SKILL.md that *instructs* the agent to fan out work across subagents / iterate. The control flow lives in prose, executed at runtime. | the skill body itself |
| **Agent teams** | **Experimental** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | Multiple Claude Code instances coordinating via a shared task list + messaging. | not yet — flag as experimental, don't depend on it |
| **`/batch` skill** | **Stable, built-in** | Decomposes a large change into parallel units, each in its own worktree. | reference it; don't reimplement |
| **Workflow orchestration tool** | Harness-specific | Some harnesses expose a `Workflow` tool for deterministic JS-scripted fan-out. This is a *runtime tool*, **not** a plugin file you author. | n/a — mention only if the host harness has it |

When a user says "add the workflow feature," they almost always mean **"package a repeatable multi-step procedure"** — which is exactly what a skill is — optionally **plus one or more subagents** for the heavy isolated steps. Build that; don't promise a primitive that doesn't exist.

## When to bundle a subagent (`agents/*.md`)

Add an agent to the plugin when the workflow has a step that:

- needs a **clean/isolated context** (large search, reading many files) so it doesn't pollute the main conversation;
- is **reusable** across many skills/sessions as a named role (e.g. `security-reviewer`, `migration-runner`);
- benefits from a **different model or tool set** than the main session;
- should run with **`isolation: worktree`** because it mutates files in parallel with others.

If the step is a one-off within a single procedure, just describe it in the skill body — don't create an agent for it.

## Pattern: a skill that drives subagents

A skill can orchestrate without any special files — it just tells the agent how to fan out. Example phrasing inside a SKILL.md:

```markdown
### Step 3 — Review in parallel
For each changed file, spawn a subagent (Task tool, or the bundled
`security-reviewer` agent) to review it independently, then collect and
de-duplicate their findings before reporting.
```

The orchestration is the *instructions*; the parallelism happens at runtime when the agent honors them. For deterministic, scripted fan-out, defer to whatever orchestration tooling the host harness provides rather than encoding it in the plugin.

## Decision shortcut

- Repeatable procedure → **skill**.
- Repeatable procedure + a heavy/isolated/specialized step → **skill + bundled subagent**.
- "Run many isolated changes at once" → point at the built-in **`/batch`** skill.
- Cross-instance team coordination → **agent teams**, and label it experimental.
