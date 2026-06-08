---
name: orchestrate-sub-agents
description: |
  Run this skill when the user wants to split a project into multiple tracks of
  work that parallel sub-agents can execute concurrently without stepping on
  each other. You design the split, write the per-track briefs + shared
  handbook + task tracker, set up git worktrees, and dispatch sub-agents via
  the Agent tool — you do NOT give the user copy-paste prompts to run in other
  sessions.

  Trigger when the user says things like: "spawn some sub-agents to do this in
  parallel", "split this into tasks agents can do concurrently", "dispatch
  parallel agents", "orchestrate this", "fire multiple agents", "divide this
  work between workers", "turn this into a multi-agent workflow", or describes
  a large refactor / build-out they want fanned out across agents. Also
  triggers when they ask you to *become* the primary/orchestrator session and
  delegate the implementation.

  Do NOT trigger for: single quick fixes, one-agent pair programming, or
  situations where the user just wants a plan (use the Plan agent instead).
---

# Orchestrate Sub-Agents

Coordinate parallel sub-agents on a shared codebase without collisions. You act as the primary session: you design the slicing, write the contracts, and dispatch workers via the Agent tool; each worker runs in an isolated git worktree and returns a structured summary when done. You then merge.

This skill exists because naive "spawn 5 agents and hope" produces merge hell: agents touch the same files, change the same contracts, and one's commit clobbers another's. The structure here — slice briefs, a shared handbook, a task tracker, and git worktrees — is the only thing that makes parallel agent work actually parallel.

## When this skill is the right tool

- Project has **≥ 3 logically separable layers** (UI / data / integration / tests / deployment / ...).
- The user wants multiple features shipped concurrently, not sequentially.
- There's a sane test bar (`pytest` or similar) the primary can trust to validate merged branches.
- A git repo exists (or the user is willing to `git init` before you start).

If any of these is missing, push back before starting. In particular, if there's no git repo, say so — worktrees need git.

## Workflow

### Step 1 — Ensure the repo is ready

- Confirm `git status` succeeds. If not, propose `git init` and a first commit, then stop and wait for confirmation.
- Confirm tests pass on `main` before you begin. If they don't, fixing that comes first.
- Confirm `.gitignore` excludes secrets, build artefacts, and anything large/private. Creating worktrees duplicates the working tree, so a fat checkout slows everything down.

### Step 2 — Decompose the project into slices

A **slice** is a layer of the system with clear file ownership. It's typically 1–6 files. Rules:

- Each slice **owns** a disjoint file set. Two slices cannot both own the same file.
- Each slice lists **contracts it must honour** — function signatures, SQL schemas, CLI flags, HTTP routes that other slices depend on. These are the merge-safety boundaries.
- Shared modules (e.g. `storage.py`, `config.py`) get a designated coordinator. Changes go through the primary session, not through worker agents.

Typical slice families (adapt to the project):

- UI / frontend
- Data ingestion / ETL
- Core domain logic (one per bounded context)
- External integrations (per 3rd-party service)
- Reporting / aggregation
- Feedback / human-in-the-loop
- Deployment / automation
- Evaluation / benchmarks

Write a short brief per slice under `docs/SLICES/NN-name.md`. Template: `assets/slice-brief.md.template`.

### Step 3 — Author the shared orchestration files

Create (or use `scripts/init_orchestration.sh` to scaffold):

- `docs/AGENT_HANDBOOK.md` — the rules every worker reads first. Template: `assets/AGENT_HANDBOOK.md.template`.
- `docs/SLICES/00-overview.md` — how the slices relate and which files each owns. Template: `assets/slices-overview.md.template`.
- `docs/TASK_TRACKER.md` — single source of truth for progress. Template: `assets/TASK_TRACKER.md.template`.
- `docs/SLICES/NN-<name>.md` per slice, following the brief template.

The handbook is **non-negotiable**. It spells out: worker stays inside its slice, commits to its worktree branch, doesn't modify shared files without a tracker note, returns a structured summary. If you skip this, worker agents drift and merges conflict. See `references/merge-protocol.md` for why.

### Step 4 — Pick the first wave of parallel work

Before firing anything, read `references/anti-collision.md`. The short version of anti-collision:

- No two agents in one wave own the same file.
- No two agents in one wave need the same schema/contract change.
- If a task has a dependency on another slice's output, do not schedule it in the same wave — sequence it.

Typical first wave: 3–5 agents. More is rarely worth it — your merge capacity bounds throughput.

### Step 5 — Create the worktrees

Claude Code's Agent tool has an `isolation: "worktree"` option. **Prefer that** when available. If worktree-isolation hooks aren't configured in the project's `.claude/settings.json`, fall back to creating worktrees manually:

```bash
for slice_branch in "ui:slice-01-feature-x" "data:slice-04-feature-y" ...; do
    wt_name="${slice_branch%%:*}"
    branch="${slice_branch##*:}"
    git worktree add -b "$branch" ".claude/worktrees/$wt_name" main
done
```

(`scripts/setup_worktrees.sh` automates this; pass it a newline-delimited list of `worktree_name:branch_name`.)

### Step 6 — Dispatch the sub-agents

Call the Agent tool **once per worker**, in the same primary-session response so they run in parallel. Each call gets:

- **subagent_type**: `general-purpose` (unless a more specialised agent matches)
- **run_in_background**: `true` — you want them async
- **prompt**: a self-contained brief. See `references/dispatch-anatomy.md` for the exact shape.

The prompt MUST:

1. Declare the agent's worktree path as its first `cd` target.
2. Reference the three files the agent reads first: `AGENT_HANDBOOK.md`, the slice brief, `TASK_TRACKER.md`.
3. Name the one specific task (not "pick any task") — this prevents two agents from claiming the same task.
4. Specify the non-negotiables: stay in scope, don't change contracts, tests must pass, don't merge to main.
5. Ask for the structured summary format on completion.

**Do not tell the user to copy-paste prompts into other sessions.** That defeats the point of this skill. Use the Agent tool.

### Step 7 — Monitor and merge

Workers complete asynchronously. For each completion notification:

1. Read the agent's structured summary.
2. Decide: merge / request changes / reject.
3. Merge cleanly (`git merge --no-ff <branch>`). With good slicing, conflicts are rare; when they happen they're almost always in `TASK_TRACKER.md` and trivially resolvable.
4. Run the full test suite on merged `main`.
5. Remove the worktree + branch after merge.

See `references/merge-protocol.md` for conflict resolution, rebase strategies, and when to request changes vs. merge-and-fix-forward.

### Step 8 — Report and plan the next wave

Report to the user:

- What merged (branch names, summary bullets per slice)
- Test status on `main`
- What's now unclaimed in `TASK_TRACKER.md` — preview the next wave

If there are remaining slices/tasks, ask whether to fire another wave.

## Hard rules

1. **Always use git worktrees.** Two agents writing to the same working tree will clobber each other. No exceptions.
2. **Dispatch via the Agent tool.** Never hand the user a prompt with "paste this into a new session." That breaks the orchestration model and loses the structured summary.
3. **One task per agent per wave.** Assign a specific task in the dispatch prompt. Don't let agents pick.
4. **Primary owns shared modules.** Workers read `storage.py` / `config.py` / `cli.py` — they don't write to them without a coordinator note in `TASK_TRACKER.md`.
5. **Tests pass before merge.** If a worker's branch fails tests on merge, request a fix on the branch; don't merge-and-hope.

## Decision points

- **Should this be one slice or two?** — If the tasks share most owned files, it's one slice. Different files but tightly coupled contracts → still probably one slice (one agent).
- **Can this task run in the current wave?** — Check: does any other wave-candidate touch these files? Does this task need the output of another in-flight task? If either is yes, schedule it later.
- **Sub-agent vs. do it yourself?** — If the task is small (< 30 min) or requires cross-slice context you already have, do it yourself. Orchestration has overhead.
- **When the agent returns a blocker** — If `[!]` is the status, triage before spawning anything else: is the block structural (your slicing is wrong) or local (they hit one gotcha)? Fix structure first.

## Progressive-disclosure map

| If you need … | Read … |
|---|---|
| The exact dispatch prompt shape | `references/dispatch-anatomy.md` |
| Why anti-collision rules exist and edge cases | `references/anti-collision.md` |
| Merge strategies and conflict playbook | `references/merge-protocol.md` |
| Starter templates for handbook / tracker / slice brief / overview | `assets/*.template` |
| Shell helpers to scaffold orchestration docs and worktrees | `scripts/init_orchestration.sh`, `scripts/setup_worktrees.sh` |

## Common mistakes

- **"Let each agent pick its own task."** Two agents pick the same task; one overwrites the other's progress. Always assign one task per agent in the dispatch prompt.
- **Not pre-creating worktrees when the tool's `isolation: "worktree"` fails.** If you see `WorktreeCreate hooks are configured` errors, fall back to manual worktrees — don't silently run agents in the main tree.
- **Skipping the handbook.** Without it, workers silently edit shared files. The handbook is the contract; don't ship an orchestration without one.
- **Parallel workers on a stale branch.** All worktrees must branch from the same `main` commit; otherwise merges sprout useless merge commits. Fetch + rebase before dispatching.
- **Copy-paste prompts to the user.** If you're writing "paste this into a new Claude Code session", you're using the wrong tool — use the Agent tool.
