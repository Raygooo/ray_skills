# The wrapper-core split

A design pattern for agent prompts that need to support multiple invocation contexts (cron-driven autonomous runs, parent-session-driven sub-agents, future contexts) without duplicating the implementation discipline.

This file exists because every project that adds the agent-evolution layer eventually faces the same fork: do we maintain one big monolithic prompt, or split it? The wrapper-core split is the answer this skill recommends.

## The problem the split solves

The first version of an autonomous-evolution prompt is usually a single ~400-line file. It works. Then someone wants to delegate one IMP to a sub-agent via the Agent tool, with the parent picking the IMP — and they end up writing a 150-line ad-hoc prompt inline that re-implements the autonomous prompt's "read context → walk rubric → implement → verify → commit" shape. Both prompts work, but they drift: a refinement to the autonomous version (e.g. an in-flight status file) doesn't propagate to the parent-driven version, because the parent-driven version is reinvented every time.

Drift compounds. After 5–10 invocations, the two prompts disagree about something that matters.

## The pattern

Split the prompt surface into:

- **One core** that owns the implementation discipline. Read context. Walk the rubric (planning). Flip the IMP status. Implement. Verify (rubric + tsc/lint/build). Document. Commit. These steps are universal across every invocation context.
- **One wrapper per invocation context** that owns the environment story. Where does the IMP id come from (autonomous picks; parent provides)? Where does the agent run (created worktree vs. existing one)? Where does the report go (on-disk file vs. chat reply)? These differ per context.

Wrappers delegate to the core for the work. The core has no awareness of who's calling it.

```
┌──────────────────────────┐    ┌─────────────────────────────┐
│ prompt.md                │    │ sub-agent-prompt.md          │
│ (autonomous wrapper)     │    │ (parent-driven wrapper)      │
│                          │    │                              │
│ Step 0: gate             │    │ Pre-flight: verify env       │
│ Step 1: pick IMP         │    │ Receive IMP id as param      │
│ Step 2: setup worktree   │    │ (already in worktree)        │
│ Step 3: open status file │    │ —                            │
│ Step 4: ─┐               │    │ —                            │
│ Step 5: finalize report  │    │ Return prose to parent       │
└──────────┼───────────────┘    └──────────┬──────────────────┘
           │                                │
           └──────────►  core.md  ◄─────────┘
                        (Steps A–F:
                         universal
                         implementation
                         discipline)
```

## Named hook points

The core defines named **hook points** at step boundaries. Wrappers can install side-effects (status-file appends, telemetry, notifications) at these named boundaries without modifying the core's logic.

Today the autonomous wrapper installs status-file appends at:

| Boundary | Hook side-effect |
|---|---|
| After Step B (rubric plan written) | `step: rubric-plan` |
| After Step C (IMP status flipped) | `step: imp-status-in-progress (IMP-NNN)` |
| Start of Step D (implementation) | `step: implementation-start` |
| Start of Step E (verification) | `step: verification-start` |
| After Step E build pass | `step: build-pass` |
| Before Step F staging | `step: ready-to-commit` |

The parent-driven wrapper installs no hooks today. Future wrappers might post to Slack, write to a telemetry sink, or update a project-status badge. The contract is: hooks must not change which files the core edits or which commands it runs. If a wrapper needs to do something that changes the core's output, that's a sign the core needs a new step — propose it, don't hack the wrapper.

Hook points use **named** steps (Step B, Step C, …), not numbered references. Naming makes the contract resilient to future renumbering.

## When to add a new wrapper

When a new invocation context appears — for example:

- A CI-pipeline wrapper that runs the discipline as part of a PR check.
- A chat-bot wrapper that lets a teammate trigger an IMP implementation via Slack.
- A REPL wrapper for in-session experimentation.

The right move is a new file under `docs/autorun/` (e.g. `ci-prompt.md`) that adds whatever the new context needs (pre-flight different, parameter source different, output sink different) and delegates to `core.md` for the implementation work.

The wrapper file can be small. The autonomous wrapper is ~330 lines because of the gate, picking, two-mode worktree setup, status file, and on-disk report. The parent-driven wrapper is ~160 because the parent has already done most of that work. A CI wrapper would probably be 80–120 lines.

## When to extend the core

When a new step truly belongs to *every* invocation context — for example:

- A "run failure-mode test suite" step before the build verification.
- A "check provider rate limits" step before starting implementation.
- A "produce a security-impact analysis" step alongside the rubric walk.

The right move is to add a new lettered step to `core.md` (e.g. Step G), rename the existing step ordering if needed, and update each wrapper's hook table to include any new boundaries.

If the new step is only needed by some wrappers, it does NOT belong in the core — push it into the relevant wrapper instead.

## Anti-patterns to avoid

- **Branching the core on a mode flag.** Don't write `if (mode === "autonomous")` blocks inside the core. The whole point of the split is that the core doesn't know who's calling it. If a step would need to branch by mode, factor it out into the wrappers.
- **Wrappers reaching into core internals.** Wrappers should only interact with the core through (a) the hand-off `"Read core.md and follow Steps A–F"` and (b) the named hook points. Don't have a wrapper say "skip Step C" or "after the third sub-paragraph of Step E." If the wrapper needs to skip a step, it's a sign the step shouldn't be in the core.
- **Copy-pasting between wrappers.** The whole reason for the split is to avoid duplication. If you find yourself copying paragraphs from `prompt.md` into `sub-agent-prompt.md`, lift them into `core.md` instead.
- **Silently letting the wrappers and core drift.** When you change `core.md`, re-read both wrappers' hook tables to make sure they still align with the named boundaries. The cost is one minute; the cost of drift is debugging a broken run weeks later.

## Renaming, splitting, merging

The core's structure isn't sacred. If after a few iterations Steps D and E feel awkwardly fused, split them. If Steps B and C feel like one logical unit, merge them. When you renumber, update every wrapper's hook table in the same commit. The wrappers should be small enough that this is a five-minute change.

## Worked example

See [`docs/autorun/`](https://github.com/Raygooo/) in the `interactive_edu` project for a real implementation. Compare:

- `core.md` (~225 lines) — the implementation discipline
- `prompt.md` (~330 lines) — autonomous wrapper
- `sub-agent-prompt.md` (~160 lines) — parent-driven wrapper

Read them side-by-side once and the pattern clicks.

## Related

- `agent-evolution-layer.md` — the "why" behind the whole layer; bounded autonomy as the safety triad
- `invocation-modes.md` — the four ways to fire an agent and how each chooses its wrapper
- The wrapper-core split itself is captured as an ADR in the worked-example project — see `assets/adr-shared-core-for-agent-prompts.md.template` for the pre-filled rationale.
