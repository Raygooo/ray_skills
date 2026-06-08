---
name: engineering-discipline
description: |
  Set up and maintain a six-document source-of-truth system for a software project — strategic roadmap, immutable ADRs, a feedback + improvements backlog, a pre-implementation rubric, a knowledge-points learning log, and a cross-linked changelog — so the *why* behind every decision survives across contributors and sessions. Optionally layers on agent-driven evolution: an autonomous loop (cron / `/loop` / `/schedule`) and a parent-driven sub-agent prompt (Agent tool) that picks an improvement, walks the rubric, implements it, and commits to a worktree branch for human review.

  Trigger when the user says things like: "set up engineering discipline", "add an ADR system", "bootstrap project documentation", "track decisions and feedback like a senior engineer", "create a roadmap and decision log", "document this project so future me can pick it up" — or, for the optional layer, "set up an autonomous evolution loop", "have agents work on improvements while I'm away", "delegate an IMP to a sub-agent with the rubric". Runs in three modes — bootstrap, audit, or ongoing-use. Skip for throwaway scripts and short-lived solo prototypes.
---

# Engineering Discipline

A six-document source-of-truth system that lets a software project preserve the *why* behind every decision while staying productive. Designed for projects where multiple contributors (human, or human+AI) need to pick up cold without re-relitigating settled choices.

This skill provides three modes (Bootstrap, Audit, Ongoing-use), templates for every document, and the workflow rules that connect them.

## Mental model

Six documents, each with a different scope and cadence:

```
strategic   →  ROADMAP.md           vision + numbered strategic decisions (D1, D2, ...)
decisions   →  docs/decisions/      ADRs — one per non-obvious tactical choice (immutable)
queued      →  docs/backlog/        feedback (FB-NNN) + improvements (IMP-NNN)
standards   →  docs/rubric.md       feature checklist (R1.1, R1.2, ..., R10.x)
learning    →  docs/learning/       knowledge points (KP-NNN) — transferable concepts
history     →  CHANGELOG.md         what shipped when, citing the others
```

Cross-linking is the discipline's load-bearing piece:

- A change in CHANGELOG cites the **rubric items** it addressed and links to any **ADRs** it produced.
- An ADR references the **roadmap phase** it serves.
- A backlog `IMP-NNN` links to the `FB-NNN` that triggered it; when implemented, links to the CHANGELOG entry.
- A knowledge point (`KP-NNN`) links to the ADR or feedback that demonstrated it.

This means **any decision can be traced backward to its origin and forward to its impact**. Cold-start onboarding works because the audit trail is real, not aspirational.

For the deeper rationale on each component (why ADRs are immutable, why the rubric is numbered, why feedback is separated from improvements), read `references/why-it-works.md`.

### Optional fourth layer: agent-driven evolution

Once the six-doc substrate is in place, the project can opt into an **agent-evolution layer** that lets Claude agents pick `IMP-NNN` entries from the backlog and implement them safely:

```
┌──────────────────────────────────────────────────────────────┐
│  AGENT-EVOLUTION LAYER (optional)                            │
│  docs/autorun/{core,prompt,sub-agent-prompt,README}.md       │
│  scripts/autorun.sh                                          │
│  + 3 ADRs (initialization gate, autonomous loop, core split) │
└──────────────────────────────────────────────────────────────┘
                           │ depends on
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  SIX-DOCUMENT SUBSTRATE (the diagram above)                  │
└──────────────────────────────────────────────────────────────┘
```

The layer ships **two invocation modes** sharing **one implementation core**:

- **Autonomous mode** (`prompt.md`) — fired on a schedule (cron, `/loop`, `/schedule`). The agent picks an IMP, walks the rubric, implements, commits to a worktree branch, writes a one-screen on-disk report. The human reviews the report and merges or discards.
- **Parent-driven mode** (`sub-agent-prompt.md`) — a parent Claude session spawns a sub-agent via the Agent tool. The parent provides the IMP id; the sub-agent does the implementation discipline and returns a structured prose report in chat for the parent to act on.

Both modes share the same hard constraints: never commit to the default branch, never push, never proceed if `tsc`/`lint`/`build` fails, one IMP per invocation, all work in a worktree. The conceptual core is **bounded autonomy** — scope (one IMP), isolation (worktree), and review (human merges) form a safety triad; remove any one and the system breaks.

The layer is **off by default**. Bootstrap creates the six-doc substrate; opt into the agent-evolution layer separately when the project is ready (typical readiness: at least 3–5 `IMP-NNN`s queued, a tagged baseline like `phase-1-mvp`, working `tsc`/`lint`/`build`, and a human committed to a review cadence). See `references/agent-evolution-layer.md` for when to add this layer and `references/wrapper-core-split.md` for the design pattern.

## When to use this skill

**Use it when:**

- Project will have ≥2 contributors (human, or human collaborating with AI)
- Project will be worked on for more than ~2 weeks
- Decisions are accumulating that would otherwise live only in someone's head
- New contributors (or new AI sessions) need to pick up cold

**Skip it when:**

- Throwaway script or one-off prototype
- Solo project, <1 week of work, no plans to revisit
- The user already has a doc culture they don't want disturbed (audit and propose lightweight additions instead)

If unsure, ask the user one question: *"How long do you expect to be working on this, and will anyone else (or future-you) need to understand decisions you make today?"* — their answer makes the call.

## Workflow

### Step 1 — Determine mode

Ask the user (or infer from context):

| Symptom | Mode |
|---|---|
| "I'm starting a new project / fresh repo" | **Bootstrap** |
| "I have an existing project, want to add this discipline" | **Bootstrap** (additive) |
| "We have some docs already, want to know what's missing" | **Audit** |
| "Help me write today's CHANGELOG / ADR / KP entry" | **Ongoing-use** |

Bootstrap and Audit can run together: audit first to find what's missing, bootstrap-create only the missing pieces.

### Step 2 — Bootstrap mode (set up the system)

For each of the six documents that doesn't yet exist, copy the corresponding `.template` file from `assets/` into the user's repo and fill in placeholders together. **Do not run `cp` blindly** — open each template, walk it with the user, and write the customized version using your edit tools.

| Repo path | Source template | What to customize |
|---|---|---|
| `ROADMAP.md` | `assets/ROADMAP.md.template` | North Star, motivation, strategic decisions D1–DN, phased plan |
| `CHANGELOG.md` | `assets/CHANGELOG.md.template` | Initial phase header; leave the entry list empty |
| `docs/decisions/README.md` | `assets/decisions-README.md.template` | Index has zero rows initially |
| `docs/decisions/template.md` | `assets/adr-template.md.template` | Verbatim copy — this is the per-ADR template users will copy when writing ADRs |
| `docs/backlog/README.md` | `assets/backlog-README.md.template` | Verbatim copy |
| `docs/backlog/feedback.md` | `assets/feedback.md.template` | Empty log; show the format |
| `docs/backlog/improvements.md` | `assets/improvements.md.template` | Empty queue; show the format |
| `docs/rubric.md` | `assets/rubric.md.template` | Adjust items to project domain — the template is generic; some R3 / R5 items may need rewording for non-LLM, non-streaming, non-realtime work |
| `docs/learning/README.md` | `assets/learning-README.md.template` | Verbatim copy |
| `docs/learning/knowledge-points.md` | `assets/knowledge-points.md.template` | Empty log; show the format |
| `CLAUDE.md` (or `AGENTS.md`) | `assets/CLAUDE-additions.md.template` | If the file exists, splice in the relevant sections; if not, scaffold from the template |

**Tailoring the rubric.** The rubric template is written for software projects that touch external services and have real users. For lower-stakes projects, suggest dropping or simplifying R3 (resource economics) and R6 (security & trust) items. For higher-stakes projects, suggest adding domain-specific items. Either way, **keep the numbering scheme** so cross-references stay stable.

### Step 2b — (optional) Agent-evolution layer

After the six-doc substrate is in place, **ask the user** whether they want to add the agent-evolution layer now. Only add it if all of these hold:

- [ ] The substrate is bootstrapped (Step 2 done).
- [ ] The project has at least 3–5 `IMP-NNN` entries with status `accepted` or `scheduled-phase-N`. The agent needs a queue to work from. If empty, defer the layer until the queue fills.
- [ ] A baseline tag exists (e.g. `phase-1-mvp`, `baseline-v1`, `v0.1.0`) marking a known-good state. If not, suggest creating one before proceeding.
- [ ] The project has a working type-check / lint / build triplet (or equivalent). If broken or absent, fix or define those first.
- [ ] The user is committed to a review cadence (daily, every-few-days, weekly) and will actually review autonomous run reports. If they won't review, the layer's leverage disappears and it's worse than manual work.

If any of these is missing, **defer the layer** and tell the user what's needed first. Do not scaffold a half-functional layer.

If all are met, walk the user through these placeholder values, then write the eight files below:

| Placeholder | Typical value | Notes |
|---|---|---|
| `{{PROJECT_NAME}}` | repo directory name | Used in agent prompts and the cron script's log path |
| `{{PROJECT_ROOT}}` | absolute path to the repo | Used in shell scripts |
| `{{DEFAULT_BRANCH}}` | `main` (sometimes `master`) | The autorun's hard-constraint "never commit here" branch |
| `{{TYPE_CHECK_CMD}}` | `npx tsc --noEmit` (TypeScript), `mypy .` (Python), `cargo check` (Rust), etc. | Step E verification |
| `{{LINT_CMD}}` | `npm run lint`, `ruff check`, `cargo clippy`, etc. | Step E verification |
| `{{BUILD_CMD}}` | `npm run build`, `cargo build --release`, `pytest`, etc. | Step E verification (use the project's "is everything OK" command) |
| `{{BASELINE_TAG_PREFIX_PATTERN}}` | `(phase-\|baseline\|v)` | Regex matching baseline tag names — for the Step 0 gate check |
| `{{ADR_NUMBER_GATE}}`, `{{ADR_NUMBER_LOOP}}`, `{{ADR_NUMBER_CORE}}` | next 3 ADR numbers from `docs/decisions/README.md` index | Cross-references between the three new ADRs |
| `{{COMMIT_TRAILER}}` | `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (or whatever the user prefers) | Last line of every commit message |
| `{{DATE}}` | today's date in YYYY-MM-DD | ADR `Date:` field |

| Repo path | Source template |
|---|---|
| `docs/autorun/core.md` | `assets/autorun-core.md.template` |
| `docs/autorun/prompt.md` | `assets/autorun-prompt.md.template` |
| `docs/autorun/sub-agent-prompt.md` | `assets/autorun-sub-agent-prompt.md.template` |
| `docs/autorun/README.md` | `assets/autorun-readme.md.template` |
| `docs/autorun/reports/` (empty directory; create with a `.gitkeep` so git tracks it) | — |
| `scripts/autorun.sh` | `assets/autorun-script.sh.template` (also `chmod +x`) |
| `docs/decisions/<NNNN>-initialization-gate.md` | `assets/adr-initialization-gate.md.template` |
| `docs/decisions/<NNNN>-autonomous-evolution-loop.md` | `assets/adr-autonomous-evolution-loop.md.template` |
| `docs/decisions/<NNNN>-shared-core-for-agent-prompts.md` | `assets/adr-shared-core-for-agent-prompts.md.template` |
| `docs/decisions/README.md` | append three new rows to the index — do not renumber existing entries |

**Process:** open each template, substitute placeholders inline, write to the destination using your edit tools. Do not `cp` blindly — placeholder strings will leak through.

**After writing:** walk the user through the four invocation options (cron / `/loop` / `/schedule` / parent-driven Agent tool) using `references/invocation-modes.md`. Recommend they pick one to start with — typically cron for set-and-forget, or parent-driven for on-demand delegation. Then ask whether they want to add a starter cron entry now or wait.

**Don't fire any agents during bootstrap.** The layer is *configured*, not *exercised*. The first autonomous run happens when the user (or cron) invokes it themselves.

### Step 3 — Audit mode (find what's missing)

For each of the six documents, check whether it exists and whether it's healthy:

| Component | Check | Red flag |
|---|---|---|
| ROADMAP | Exists? Has strategic decisions D1..? Is current state visible? | Stale "What we're building" sections, no decision log, no phase markers |
| ADRs | Folder exists? README index up to date? Any decisions made in code without an ADR? | Folder absent; `git log` reveals architecture changes with no ADR |
| Backlog | Folder exists? Feedback flowing in? Improvements have status? | Backlog is empty AND issue tracker is overflowing → feedback is going elsewhere |
| Rubric | Exists? Is it being cited in CHANGELOG entries? Walk recent commits | Rubric exists but never referenced — culture isn't using it |
| Learning | Folder exists? KPs accumulating at all? | Solo project that lasted >1 month with zero KPs → either over-discipline or learning isn't being captured |
| CHANGELOG | Exists? Entries link to ADRs/rubric/backlog? | Bare commit messages with no narrative; no entry has cross-references |

If the project also uses the **agent-evolution layer**, audit it too:

| Layer component | Check | Red flag |
|---|---|---|
| `docs/autorun/core.md` | Exists? Has Steps A–F? | Missing entirely OR existing but with implementation steps inlined into the wrappers (drift) |
| `docs/autorun/prompt.md` | Exists? Has gate (Step 0), IMP picking (Step 1), worktree setup (Step 2), status file (Step 3), core delegation (Step 4), final report (Step 5)? | Missing dual-mode worktree setup → fails on harness-managed runs; missing status file → no mid-run observability |
| `docs/autorun/sub-agent-prompt.md` | Exists? Has parameter section, verify-not-create preflight, prose report? | Often missing in older projects that only set up the autonomous loop; the parent then writes ad-hoc inline prompts that drift |
| `docs/autorun/reports/` | Has reports? Are recent ones reviewed (merged or worktree-removed)? | Many `<TS>.in-progress.md` files older than 10 minutes → wedged runs nobody investigated; many unmerged worktree branches → human isn't reviewing |
| `scripts/autorun.sh` | Exists? Executable? Points at the prompt? | Missing `chmod +x`; hardcoded path that doesn't match the repo's actual root |
| `docs/decisions/NNNN-initialization-gate.md` | Exists? G1–G7 listed? | Gate ADR missing → autonomous runs fire on dirty trees |
| `docs/decisions/NNNN-autonomous-evolution-loop.md` | Exists? Hard constraints listed? | Loop ADR missing → next contributor doesn't know why these constraints exist |
| `docs/decisions/NNNN-shared-core-for-agent-prompts.md` | Exists? Wrapper-core split documented? | Often missing in older layers; the parent-driven wrapper might also be missing |

A common pattern: the autonomous loop is set up but the parent-driven sub-agent prompt isn't (because it was added later in the design). If the user spawns sub-agents via the Agent tool with ad-hoc inline prompts, propose adding `sub-agent-prompt.md` from the template.

Report findings as a punch list: *"Missing: docs/rubric.md, docs/autorun/sub-agent-prompt.md. Stale: docs/decisions/README.md index. Healthy: ROADMAP.md, CHANGELOG.md, docs/autorun/core.md."* For each missing/stale item, propose the smallest viable fix.

### Step 4 — Ongoing use (writing entries)

When the user is mid-feature and asks for help with documentation, route by intent:

| User says... | Action |
|---|---|
| "We need to decide between X and Y" | Plan to write an ADR. Use `assets/adr-template.md.template`. Increment ID from the index in `docs/decisions/README.md`. |
| "I just received feedback from a user" | Append to `docs/backlog/feedback.md`. Assign next `FB-NNN`. Note any improvement it triggers. |
| "Here's an idea we want to do later" | Append to `docs/backlog/improvements.md`. Assign next `IMP-NNN`. Set status `proposed` until accepted. |
| "I'm about to build feature X" | Walk `docs/rubric.md` with them in **planning mode** — every item, decide *handle now / defer with backlog entry / wontfix*. |
| "I just shipped feature X" | Walk the rubric in **verification mode** (is each item actually true now?). Then write the CHANGELOG entry, citing rubric items. |
| "What did we ship lately?" | Read `CHANGELOG.md`. |
| "Why did we choose X?" | Search `docs/decisions/` for relevant ADRs. |
| "What's queued for later?" | Read `docs/backlog/improvements.md`. |
| "Spawn a sub-agent for IMP-NNN" / "Delegate this IMP" | If `docs/autorun/sub-agent-prompt.md` exists, the parent's invocation is `Agent({ isolation: "worktree", prompt: "Read sub-agent-prompt.md. Your parameters: IMP to implement: IMP-NNN. Begin." })`. See `references/invocation-modes.md`. If the prompt doesn't exist, scaffold it from `assets/autorun-sub-agent-prompt.md.template` first. |
| "Set up cron for autonomous runs" / "Add /loop / /schedule" | Walk through `references/invocation-modes.md` Mode A / B / C. The autorun script is `scripts/autorun.sh`; cron entry shape is in the `autorun-readme.md.template`. |
| "Why isn't the autorun firing?" / "An autorun aborted" | Check `docs/autorun/reports/` for the latest report or `.in-progress.md` file. Also check `docs/backlog/feedback.md` for an `FB-NNN` describing a gate failure. The initialization-gate ADR explains what conditions must hold. |
| "Add a new step to the agent's workflow" | Determine: does it apply to *every* invocation context, or only some? If every: extend `core.md` with a new lettered step (and update each wrapper's hook table if relevant). If only some: add to the relevant wrapper. See `references/wrapper-core-split.md`. |
| "Set up the autorun layer for this project" | Run **Step 2b — agent-evolution layer** of Bootstrap. Verify the readiness preconditions before scaffolding. |

For when to propose a new knowledge point, see `references/ongoing-use.md` §"Proposing knowledge points."

### Step 5 — Cross-link discipline

When writing any entry, **always** include the relevant cross-links. Examples:

- A new ADR's *Roadmap alignment* section should reference the roadmap phase by name.
- A CHANGELOG entry should cite rubric IDs (`Addresses R3.4, R5.1`) and link to any ADRs / FB / IMP it touches.
- An IMP-NNN should have `Source: FB-NNN` if it was triggered by feedback.
- A KP-NNN should link to the project artifact (ADR, code path, feedback entry) that demonstrated the concept.

Cross-links are not optional. They are the audit trail. An entry without them is a half-entry.

### Step 6 — Report what was created

When finishing a bootstrap or audit, return a structured summary listing every file created or modified, with markdown links. Example:

> Created:
> - [`ROADMAP.md`](./ROADMAP.md)
> - [`docs/decisions/README.md`](./docs/decisions/README.md)
> - [`docs/decisions/template.md`](./docs/decisions/template.md)
> - ... (etc.)
>
> Modified:
> - [`CLAUDE.md`](./CLAUDE.md) — added Quickstart, Document map, Recording-changes, Recording-feedback, Using-the-rubric, and Proposing-knowledge-points sections.

## Common mistakes to avoid

- **Treating templates as final.** Templates have placeholder content. Always customize before considering bootstrap done.
- **Skipping cross-links.** A CHANGELOG entry that doesn't cite rubric IDs or link to ADRs is *not* using the system. The discipline is exactly the cross-linking.
- **Editing accepted ADRs.** ADRs are immutable. To change a decision, write a new ADR with status `accepted`, mark the old one `superseded by ADR-NNNN`, and link.
- **Renumbering anything.** ADR numbers, rubric item IDs, FB / IMP / KP IDs are stable forever. Even if entry 3 is later marked `wontfix`, it stays numbered 3 — gaps in the sequence are fine.
- **Over-applying to small projects.** This system is overhead for a 50-line script. Recognize when not to use it (see "When to use this skill" above).
- **Producing the system without onboarding the user.** After bootstrap, walk the user through what each doc is for in 2 minutes. The system fails when the user doesn't know what they have.
- **Forgetting to update CLAUDE.md.** If the user collaborates with AI in this project, the cold-start onboarding (CLAUDE.md / AGENTS.md) is the highest-leverage doc. Always include it in bootstrap.

## Reference material

### Six-doc substrate

- `references/why-it-works.md` — the rationale for each substrate component, including alternatives we rejected and the failure modes the system is designed to prevent
- `references/ongoing-use.md` — detailed guidance on writing entries, propose-knowledge-point triggers, and how to keep the system from rotting

### Agent-evolution layer

- `references/agent-evolution-layer.md` — the conceptual "why" behind the optional fourth layer; bounded autonomy as the safety triad (scope + isolation + review); when to add this layer; what "ready" looks like
- `references/wrapper-core-split.md` — the design pattern that lets one core support multiple invocation contexts; named hook points; when to add a new wrapper vs. extend the core; anti-patterns to avoid
- `references/invocation-modes.md` — the four ways to fire an agent (cron / `/loop` / `/schedule` / parent-driven Agent tool); choose-your-mode table; how to fire each; how to review what each produced

## Templates

All in `assets/`. Each is a `.template` file, named so its target path is obvious.

### Six-doc substrate

- `ROADMAP.md.template`
- `CHANGELOG.md.template`
- `CLAUDE-additions.md.template`
- `decisions-README.md.template`
- `adr-template.md.template`
- `backlog-README.md.template`
- `feedback.md.template`
- `improvements.md.template`
- `rubric.md.template`
- `learning-README.md.template`
- `knowledge-points.md.template`

### Agent-evolution layer (optional, applied via Step 2b)

- `autorun-core.md.template` — universal Steps A–F (read context → walk rubric (planning) → flip IMP status → implement → verify → document and commit)
- `autorun-prompt.md.template` — autonomous wrapper (gate, IMP picking, dual-mode worktree setup, status file, on-disk report)
- `autorun-sub-agent-prompt.md.template` — parent-driven wrapper (parameters, verify-not-create preflight, prose report)
- `autorun-readme.md.template` — file-layout explainer for `docs/autorun/`
- `autorun-script.sh.template` — cron-friendly wrapper that invokes `claude -p` non-interactively
- `adr-initialization-gate.md.template` — pre-filled ADR for the gate (G1–G7)
- `adr-autonomous-evolution-loop.md.template` — pre-filled ADR for the autonomous loop's design rationale and constraints
- `adr-shared-core-for-agent-prompts.md.template` — pre-filled ADR for the wrapper-core split

When using these, **read each template, customize placeholders for the user's project, and write to the destination**. Never `cp` a template into a real doc; placeholder strings (e.g. `{{PROJECT_NAME}}`, `{{DEFAULT_BRANCH}}`, `{{TYPE_CHECK_CMD}}`) will leak through.

### Placeholders used in agent-evolution-layer templates

| Placeholder | Meaning |
|---|---|
| `{{PROJECT_NAME}}` | The repo / project's name (typically the directory name) |
| `{{PROJECT_ROOT}}` | Absolute path to the repo (used in shell scripts and Agent tool prompts) |
| `{{DEFAULT_BRANCH}}` | Usually `main`; sometimes `master` or another |
| `{{TYPE_CHECK_CMD}}` | Project's type-check command — e.g. `npx tsc --noEmit`, `mypy .`, `cargo check` |
| `{{LINT_CMD}}` | Project's lint command — e.g. `npm run lint`, `ruff check`, `cargo clippy` |
| `{{BUILD_CMD}}` | Project's "is everything OK" command — e.g. `npm run build`, `pytest`, `cargo build --release` |
| `{{BASELINE_TAG_PREFIX_PATTERN}}` | Regex for baseline tag names — e.g. `(phase-\|baseline\|v)` |
| `{{ADR_NUMBER_GATE}}`, `{{ADR_NUMBER_LOOP}}`, `{{ADR_NUMBER_CORE}}` | Next three ADR numbers from `docs/decisions/README.md`, padded to 4 digits |
| `{{COMMIT_TRAILER}}` | Co-author trailer line — e.g. `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` |
| `{{DATE}}` | Today's date in YYYY-MM-DD (for ADR `Date:` fields) |
