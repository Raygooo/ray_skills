# Ray Skills Marketplace

A Claude Code plugin marketplace with productivity tools for macOS power users.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add Raygooo/ray_skills
```

Then install any plugin:

```
/plugin install proxy-app-launcher@ray-skills
```

## Plugins

### proxy-app-launcher

Creates a macOS `.app` launcher that starts any Electron/desktop app (Claude, Cursor, VS Code, Obsidian, etc.) with proxy environment variables injected. Solves the problem where Electron apps ignore system proxy settings when using Clash/V2Ray in rule mode.

**Skills included:**
- `proxy-app-launcher:proxy-app-launcher` — auto-triggered when you mention proxy issues with Electron apps

**Trigger phrases:**
- "Electron app doesn't use proxy"
- "app ignores system proxy"
- "Clash rule mode not working for app"
- "create proxy launcher"

### marketplace-contributor

Meta-plugin for growing this marketplace itself. Teaches agents how to capture a workflow as a reusable skill (and, when a step needs isolation, a bundled subagent), scaffold a new plugin, apply progressive disclosure across `SKILL.md` / `references/` / `scripts/` / `assets/`, delegate skill authoring to the built-in `skill-creator`, and publish by pushing straight to `main`.

**Skills included:**
- `marketplace-contributor:contribute-skill` — auto-triggered when you want to save a workflow as a skill/subagent or add a new plugin to this marketplace

**Trigger phrases:**
- "save this as a skill"
- "turn this workflow into a skill"
- "add a skill / subagent to the marketplace"
- "package this workflow"
- "create a new plugin for this"
- "contribute to my marketplace"

### parallel-orchestrator

Lets a primary agent split a project into file-disjoint slices, write per-slice briefs + a shared handbook + a task tracker, set up git worktrees, and dispatch parallel sub-agents via the Agent tool. Each worker stays inside its slice, commits to its worktree branch, and returns a structured summary — the primary merges cleanly after. No copy-pasting prompts to other sessions.

**Skills included:**
- `parallel-orchestrator:orchestrate-sub-agents` — auto-triggered when you ask to fan work out across parallel agents on a codebase

**Trigger phrases:**
- "spawn some sub-agents to do this in parallel"
- "split this into tasks agents can do concurrently"
- "orchestrate parallel work on this project"
- "fire multiple agents"
- "divide this between workers in worktrees"

### engineering-discipline

A six-document source-of-truth system that lets a software project preserve the *why* behind every decision while staying productive. Scaffolds a strategic roadmap, immutable ADRs, a feedback + improvements backlog, a numbered pre-implementation rubric, a knowledge-points learning log, and a cross-linked changelog — with workflow rules that connect them. Designed for projects where multiple contributors (human, or human + AI) need to pick up cold without re-litigating settled choices.

**Optional fourth layer: agent-driven evolution.** Once the substrate is in place, the project can opt into an autonomous evolution loop (cron / `/loop` / `/schedule`) plus a parent-driven sub-agent prompt (Agent tool) — both built on a shared implementation core. The agent picks an `IMP-NNN` from the backlog, walks the rubric, implements, runs the build, writes a CHANGELOG entry, commits to a worktree branch. The human merges or discards. **Bounded autonomy** — scope (one IMP), isolation (worktree), review (human merges) form the safety triad.

Has three modes: bootstrap a new repo (substrate alone, or substrate + agent layer), audit an existing one (catches missing pieces in either layer), or guide ongoing use (write today's entry, fire today's autorun, delegate today's IMP to a sub-agent).

**Skills included:**
- `engineering-discipline:engineering-discipline` — auto-triggered when you want to set up project documentation discipline, add an ADR system, scale how decisions and feedback are tracked, or layer agent-driven evolution on top

**Trigger phrases:**
- "set up engineering discipline"
- "add an ADR system"
- "bootstrap project documentation"
- "I want to track decisions and feedback like a senior engineer"
- "create a roadmap and decision log"
- "add a feature checklist before we ship"
- "help me document this project so future me can pick it up"
- "set up an autonomous evolution loop for this project"
- "have agents work on improvements while I'm away"
- "fire a cron job that picks IMPs and implements them"
- "spawn sub-agents to implement IMPs"
- "delegate one IMP to a sub-agent with the rubric"
- "give me an Agent-tool prompt for IMP-NNN"
- "set up the wrapper-core agent prompts"
- "add the initialization gate for autonomous runs"
