# Invocation modes

There are four ways to fire an agent that uses the agent-evolution layer. Three are autonomous (no live human in the session); one is parent-driven (a parent Claude session delegates one IMP).

This file is a quick reference for choosing which mode to use when. For the design rationale of the wrapper-core split that lets one core support all four modes, see `wrapper-core-split.md`.

## At a glance

| Mode | How fired | Typical cadence | Output sink | Wrapper |
|---|---|---|---|---|
| **A. cron** | `scripts/autorun.sh` from system cron / launchd | Daily (or whatever schedule fits the backlog) | On-disk report at `docs/autorun/reports/<TS>.md` | `prompt.md` |
| **B. Claude Code `/loop`** | Inside an open Claude Code session, `/loop 24h docs/autorun/prompt.md` | Daily, while the session is alive | Same on-disk report | `prompt.md` |
| **C. Claude Code `/schedule`** | Inside Claude Code, `/schedule` then provide the prompt content; Anthropic-hosted | User-defined | Same on-disk report (synced back to the repo) | `prompt.md` |
| **D. Parent-driven Agent tool** | Parent session calls `Agent({ isolation: "worktree", prompt: "Read sub-agent-prompt.md. Your parameters: IMP to implement: IMP-NNN. Begin." })` | On-demand from the parent | Structured prose returned to parent in chat | `sub-agent-prompt.md` |

A, B, and C are functionally interchangeable — same prompt, same on-disk reports, same review flow. The choice is purely about infrastructure preference (do you want to run a cron service, keep a local Claude session alive, or use Anthropic's hosted scheduler?).

D is genuinely different. A parent session has already picked the IMP and provided context the autonomous loop would have to derive. The sub-agent's job is purely execution; the report goes back in chat for the parent to act on (typically a `--no-ff` merge).

## When to use which

### Use a cron / loop / schedule mode (A, B, C) when:

- You want continuous evolution without supervising every run. Set the cadence, walk away, review the reports when convenient.
- The backlog has enough `accepted` IMPs to keep the agent fed. If the agent runs out of work, it generates one new `proposed` IMP per run and stops — that's fine, just less throughput.
- You're comfortable with the daily-review rhythm. If reports pile up unread, the layer's leverage is gone.
- Pick **A (cron)** if you have a Mac/Linux box that's always on; lowest infrastructure friction.
- Pick **B (`/loop`)** if you typically have Claude Code open during the day anyway; no separate process to manage.
- Pick **C (`/schedule`)** if you want it to run even when your laptop is closed; Anthropic handles the host.

### Use parent-driven mode (D) when:

- You're working interactively and want to delegate one IMP without context-switching. You pick which IMP, the sub-agent does the discipline.
- You want to parallelize: spawn 2–3 sub-agents on independent IMPs in separate worktrees, review their reports, merge or discard each.
- You've identified an IMP whose scope is clear but whose implementation is grungy enough that you'd rather hand it off than do it yourself. The sub-agent walks the rubric, runs the build, writes the CHANGELOG entry — all the discipline you'd skip if you were tired.
- The work would benefit from worktree isolation (e.g. you're already deep in another change and don't want to context-switch your main checkout).

### Don't use any mode when:

- The IMP is unclear in scope. Discuss it with the human first; refine the IMP entry; *then* delegate.
- The IMP touches strategic decisions (D1–DN in ROADMAP). Those are human-only.
- The IMP requires external services or accounts that aren't already configured. Agents can't sign up for things.
- The project's `tsc` / `lint` / `build` is currently broken. The agent will run them as the verification step and abort. Fix the build first.

## How to fire each mode

### Mode A — cron

In your crontab (`crontab -e`):

```cron
# Daily at 09:00 local time
0 9 * * * /path/to/project/scripts/autorun.sh >> ~/<project>_autorun.log 2>&1
```

`autorun.sh` is the cron wrapper this skill scaffolds (see `assets/autorun-script.sh.template`). It:
- Changes to the project root
- Reads `docs/autorun/prompt.md`
- Invokes `claude -p` in non-interactive mode with `--dangerously-skip-permissions`

`--dangerously-skip-permissions` is required for non-interactive runs since the agent needs to edit files and run shell commands without a user prompt. The autorun prompt enforces its own safety boundaries (initialization gate, no main commits, no pushes, sandboxed worktree) — those are the actual safety net, not the permission prompts.

### Mode B — `/loop`

Inside an open Claude Code session:

```
/loop 24h docs/autorun/prompt.md
```

The session itself does the work. Stop it with `/loop stop`.

### Mode C — `/schedule`

Inside Claude Code:

```
/schedule
```

Then provide the prompt content (paste from `docs/autorun/prompt.md`). Anthropic runs the agent on the schedule from their infrastructure.

### Mode D — parent-driven Agent tool

Inside a parent Claude Code session, the parent calls the Agent tool. The exact shape:

```
Agent({
  description: "Implement IMP-NNN",
  isolation: "worktree",
  prompt: `You are implementing one IMP for the <project> project.
Read /absolute/path/to/project/docs/autorun/sub-agent-prompt.md in full
and follow it.

Your parameters:
- IMP to implement: IMP-NNN

Begin.`
})
```

The `isolation: "worktree"` option is critical — it puts the sub-agent in a fresh git worktree on a non-`main` branch with a clean tree. Without it, the sub-agent's pre-flight verification will fail and it'll abort.

For parallel work, the parent fires multiple `Agent` calls in a single message; they run concurrently in separate worktrees. After completion, the parent serially merges with `--no-ff`, resolving any conflicts (typically in `CHANGELOG.md` and `docs/backlog/improvements.md` where multiple IMPs add entries).

## Reviewing what each mode produced

### Modes A, B, C (autonomous)

After each run:

1. Open the latest report: `ls -t docs/autorun/reports/ | head -1`. Read it.
2. The report includes the worktree's absolute path. `cd` into it.
3. Diff against the project's baseline: `git diff main..HEAD`.
4. Decide: merge into `main` (`git merge <branch> --no-ff` from the project root, NOT the worktree), or delete the worktree (`git worktree remove ../<worktree-path> --force`).

If a `<TS>.in-progress.md` file exists from a timestamp older than the longest a healthy run takes (typically ~10 minutes), it's a wedged run — investigate the worktree directly.

### Mode D (parent-driven)

The sub-agent's structured prose report contains everything the parent needs:
- Branch name (the parent merges this)
- Commit SHA(s)
- Files modified
- Rubric walk results
- Verification results (`tsc` / `lint` / `build`)
- A merge-commit summary paragraph (drop into `git merge --no-ff -m`)
- Blockers if any

The parent merges with `--no-ff` from the project root (not the sub-agent's worktree). After successful merge, clean up: `git worktree remove ../<worktree> --force; git branch -D <branch>`.

## Choosing well

If you're starting fresh: **add the cron entry first** (Mode A). It's the lowest-supervision mode, the autonomous prompt is what you'll iterate on, and you'll discover the layer's actual ergonomics through review-cycle feedback. Move to other modes (or add Mode D for parallel parent-driven work) once you've used the layer for a couple of weeks.

If your project already has Mode A working and you're comfortable, **add Mode D** when you find yourself writing ad-hoc inline sub-agent prompts in a parent session. That's the moment the parent-driven wrapper pays off.

Mode B and Mode C are conveniences over Mode A; pick them based on whether you'd rather manage cron or trust an open Claude Code session / Anthropic-hosted scheduling.

## Related

- `agent-evolution-layer.md` — the "why" behind the whole layer
- `wrapper-core-split.md` — the design pattern that lets one core support all four modes
- The `parallel-orchestrator` plugin (separate from this skill) — for fanning multi-track builds across many parallel sub-agents on file-disjoint slices, which is a different concern from one-IMP-at-a-time discipline
