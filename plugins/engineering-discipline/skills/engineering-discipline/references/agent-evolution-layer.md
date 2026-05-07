# The agent-evolution layer

This reference covers the **optional fourth layer** that can be added on top of the six-document source-of-truth system: an autonomous evolution loop plus a parent-driven sub-agent prompt, both built on the same shared core.

The six-doc substrate (ROADMAP, ADRs, backlog, rubric, learning, CHANGELOG) tells a project *what* to build and *why*. The agent-evolution layer adds *how to delegate the building safely* — to an autonomous Claude session running on a schedule, or to a sub-agent spawned by a parent session via the Agent tool.

## What the layer adds

```
┌──────────────────────────────────────────────────────────────┐
│  AGENT-EVOLUTION LAYER (this reference)                      │
│                                                               │
│  docs/autorun/                                               │
│  ├── core.md                  ← universal Steps A–F          │
│  ├── prompt.md                ← autonomous wrapper           │
│  ├── sub-agent-prompt.md      ← parent-driven wrapper        │
│  ├── README.md                ← file-layout explainer        │
│  └── reports/                 ← autonomous-only run reports  │
│  scripts/autorun.sh           ← cron entrypoint              │
│  docs/decisions/NNNN-initialization-gate.md     ← gate ADR   │
│  docs/decisions/NNNN-autonomous-evolution-loop.md            │
│  docs/decisions/NNNN-shared-core-for-agent-prompts.md        │
└──────────────────────────────────────────────────────────────┘
                           │
                           │ depends on
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  SIX-DOCUMENT SOURCE-OF-TRUTH SUBSTRATE                      │
│  (ROADMAP / ADRs / backlog / rubric / learning / CHANGELOG)  │
└──────────────────────────────────────────────────────────────┘
```

The agent-evolution layer **requires the six-doc substrate**. The agent prompts read the rubric to know what to walk; read the IMP backlog to know what to pick; flip IMP statuses; write CHANGELOG entries that cite rubric IDs; etc. None of that works without the substrate.

## The conceptual core: bounded autonomy (the safety triad)

The single load-bearing idea behind the agent-evolution layer is **bounded autonomy** — the recognition that letting an agent work without supervision is safe only when three constraints hold simultaneously:

1. **Scope.** The agent picks exactly one improvement per run, from a curated queue. It cannot drift into "while I'm here, let me also refactor X." The IMP backlog is the curation; the rubric is the discipline; the hard constraints in the prompt enforce both.
2. **Isolation.** All work happens in a git worktree on a non-`main` branch. The agent literally cannot commit to `main`, cannot push, cannot affect anything the human hasn't explicitly merged. Worktrees are the cheapest possible blast-radius firewall.
3. **Review.** Every run produces a one-screen report the human reads before merging. The agent's commit is a proposal, not a decision. Bad runs are deleted with `git worktree remove`; the cost of a bad run is one human's two-minute review, not a revert + apology.

Take any one of these away and the system breaks:
- Without scope, the agent ships drive-by refactors that touch unrelated files.
- Without isolation, a buggy run corrupts the canonical branch.
- Without review, errors compound until someone notices.

All three together are cheap to operate (cron + worktree + a daily glance at `reports/`). The triad is the design.

## When to add this layer

**Do add it when:**

- You're working with AI assistance and want to amortize the planning + verification overhead by having an agent run while you're away (overnight, weekend, between meetings).
- The project has a steady backlog of small-to-medium improvements (`IMP-NNN` entries) — typical "Phase 1 hardening" work, follow-up FBs, deferred rubric items.
- You're comfortable with a daily / weekly review rhythm. The layer creates a steady stream of branches to merge or discard; if the human won't actually look at them, the layer doesn't pay off.
- You want to be able to delegate one IMP to a sub-agent in a single Agent tool call, instead of hand-writing the discipline prompt every time.

**Skip it when:**

- The project is so early that there's no curated backlog yet — the agent will have nothing to work on. Build the six-doc substrate first; let a few `IMP-NNN`s accumulate; then add the layer.
- You're not going to actually review the runs. The layer's leverage is exactly the human-in-the-loop review; without that, it's worse than working manually because you accumulate technical debt invisibly.
- Solo, short-lived project (< 2 weeks). The setup overhead exceeds the savings.
- The project's gate condition isn't well-defined. The layer requires an `initialization-gate` ADR (see `assets/adr-initialization-gate.md.template`) that lists the preconditions for an autonomous run. Without a real gate, the agent will run on a broken project state and waste a worktree per failure.

## What "ready to add the layer" looks like

A project is ready when **all** of these are true:

- [ ] Six-doc substrate is bootstrapped (run the engineering-discipline skill if not).
- [ ] At least 3–5 `IMP-NNN` entries exist with status `accepted` or `scheduled-phase-N`. The agent needs a queue to work from.
- [ ] At least one phase has been completed and tagged (e.g. `phase-1-mvp`). The gate uses the existence of a tagged baseline to know "we have a known-good state to start from."
- [ ] The project has a working `tsc` / `lint` / `build` triplet (or the project's equivalent for non-TypeScript). The agent runs these as the verification step; if they're flaky or absent, every run will abort.
- [ ] The human reviewer agrees to a review cadence (daily, every-few-days, weekly) and will actually do it.

If any are missing, fix them before adding the layer. The skill's Audit mode can identify gaps.

## Two invocation modes share one core

The layer ships *three* prompt files but they form *two* invocation patterns over *one* shared core:

- **`core.md`** — the universal "implement an IMP cleanly" workflow. Six named steps: read context, walk rubric (planning), flip IMP status, implement, verify (rubric + build), document and commit. Both wrappers below delegate to this file for the actual implementation work.

- **`prompt.md`** — autonomous wrapper. Adds: pre-flight initialization gate, IMP picking from the queue (with priority rules and "no eligible IMP, propose one" fallback), two-mode worktree setup, in-flight status file in `reports/`, on-disk final report. Used by cron, `/loop`, and `/schedule`.

- **`sub-agent-prompt.md`** — parent-driven wrapper. Adds: parameter section the parent fills (the IMP id), pre-flight that *verifies* the parent's setup rather than creating it, structured prose report back to the parent in chat (no on-disk file). Used by the Agent tool from inside a Claude Code session.

Why split them this way? Because the implementation work is identical in both modes — only the environment story differs (gate / picking / worktree / status file / report sink). Splitting the universal logic into `core.md` and the environment-specific logic into the two wrappers means changes to "how an agent implements an IMP" land in one place. See `wrapper-core-split.md` for the design pattern.

## What the layer does NOT include

- A general-purpose multi-agent orchestrator. For fanning work out across parallel sub-agents working on file-disjoint slices, see the [`parallel-orchestrator`](https://github.com/Raygooo/ray_skills/tree/main/plugins/parallel-orchestrator) plugin. The two are complementary: parallel-orchestrator is for big multi-track builds; this layer is for one-IMP-at-a-time discipline that any wrapper can call into.
- Telemetry, run history, success-rate tracking. The on-disk reports are the only data; reading them is a manual review step. If a project needs aggregated metrics, that's a separate piece of infra (see [IMP-003-style status files](#) for what's there today).
- A failure-recovery mechanism beyond "abort cleanly and let the next run try." The agent does not retry within a run; if a run fails, the next scheduled run picks up — usually with the human's intervention in between.

## Worked example

The [`interactive_edu`](https://github.com/Raygooo/) project's `docs/autorun/` is the canonical worked example for this layer. The templates in `assets/` of this skill are generalized from that project's actual files; reading them side-by-side is the fastest way to see how a real implementation looks.
