# Dispatch prompt anatomy

The Agent-tool `prompt` for each worker is the contract. It's self-contained: the sub-agent starts with zero context, sees only this prompt, and must produce useful work. Get this prompt right or the worker wastes cycles.

## The template

```
You are a worker agent on <project-name>. Agent id: **<agent-id>**.

**YOUR WORKTREE:** <absolute path to the worktree>
**YOUR BRANCH:** <branch-name> (already checked out for you)

Your very first Bash command MUST be `cd <worktree-absolute-path>`. All
subsequent work happens inside this worktree. Git commits you make there go
to your branch. Never modify the main repo directly.

**STEP 1 — Read these three files first, in this order (inside your worktree):**

1. `docs/AGENT_HANDBOOK.md` — operating rules
2. `docs/SLICES/<slice-file>` — your slice brief
3. `docs/TASK_TRACKER.md` — current progress

**STEP 2 — Claim your specific task.**

Your task from Slice <nn>'s must-do list: **"<exact task wording>"**.

Edit `docs/TASK_TRACKER.md` in your worktree: change that line from `[ ]` to
`[~] YYYY-MM-DDTHH:MM <agent-id> — claimed`. Commit the claim as a one-line
commit.

**STEP 3 — Implement.**

<concrete what-to-do list: 3–10 bullet points. Include file names, function
names, expected behaviour. Be specific.>

**STEP 4 — Test.**

- `python -m pytest tests/ -q` must stay green.
- Add focused tests at `tests/<path>` covering ...
- Optional: slice-specific smoke test from the brief.

**STEP 5 — Close out.**

Mark `[x]` in `docs/TASK_TRACKER.md` with a short shipped-note. Commit.
Return the structured summary per the handbook (Slice, Status, Tasks
completed, Changes shipped, Tests added, Contracts touched, Spotted but not
fixed, Follow-ups).

Non-negotiables:
- Stay inside Slice <nn>'s file scope: <list the owned file paths>.
- Don't change <contracts-listed-here>.
- Tests must pass at handoff.
- Don't merge into main — primary session does that.
```

## Why each part exists

- **Agent id.** Makes the audit trail in `TASK_TRACKER.md` readable (see who did what, when).
- **Worktree path + first `cd`.** The single most common failure mode: the agent works in the main repo by accident. Hardcode the path and force the `cd`.
- **Read-order list.** Without it, agents read every doc in the repo. With it, they stay scoped.
- **Specific task (not "pick one").** Parallel agents MUST get non-overlapping tasks. If you say "pick", two agents pick the same one.
- **Concrete what-to-do list.** The agent doesn't know your intent; spell it out. File names, function names, expected inputs/outputs.
- **Tests green requirement.** If you don't say it, some agents decide tests are optional.
- **Structured summary ask.** Returns you a ready-to-merge report instead of a free-form essay.

## Things to include when relevant

- **Backward compatibility clauses** — "Calling this function without the new kwarg must behave exactly as before."
- **DB schema etiquette** — "Do not modify `src/storage.py`. If you need a schema change, add a 'schema changes requested' note to `TASK_TRACKER.md` and stop."
- **External-system warnings** — "This slice calls Home Assistant. Don't write back; read-only."
- **Small examples** — 2–3 lines of example input/output if the task is fuzzy.

## Things to leave out

- Design rationale. Put that in the handbook or slice brief, not the dispatch prompt. The prompt is the contract, not the justification.
- "Read the whole codebase first." Rarely needed; wastes tokens.
- Open-ended "clean this up as you go". Encourages scope creep.

## Spawning multiple agents in one response

If you call the Agent tool N times in a single assistant response, they run in parallel. Use `run_in_background: true` so completion notifications arrive asynchronously. If you call them in separate responses, they're serial.

## Handling failure and blockers

The handbook tells workers to mark `[!]` with a reason if they can't proceed. When you see that:

1. Read the reason in `TASK_TRACKER.md`.
2. Is it structural (your slicing is wrong) or local (one gotcha)?
3. Structural → re-scope the slice, notify other agents if needed, rebrief and re-dispatch.
4. Local → unblock the specific worker (answer their question via `SendMessage` to the agent id if still running, or a follow-up task if they've exited).

## Example: good vs. bad prompts

**Bad:**
> Work on Slice 01 for parallel cat-monitor. Read the handbook.

Too vague. Agent doesn't know which task, which worktree, what the stakes are, or what "done" looks like.

**Good:**
> You are agent-ui-b1. Worktree: /path/.claude/worktrees/ui-grouping. Branch: slice-01-session-grouping. First Bash: `cd /path/.claude/worktrees/ui-grouping`. Read docs/AGENT_HANDBOOK.md, docs/SLICES/01-web-ui.md, docs/TASK_TRACKER.md. Task: "Group review-gallery frames by session." Mark [~], commit claim. Modify src/webapp.py _render_review_gallery to group by session_start_local, add `.session-group` and `.session-header` CSS, add a "Sessions" stat card. Add tests/test_webapp_grouping.py with ≥2 tests. Keep keyboard shortcuts working. `python -m pytest tests/ -q` must pass. Mark [x], commit, return structured summary.

Specific, actionable, bounded.
