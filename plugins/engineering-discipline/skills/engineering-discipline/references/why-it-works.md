# Why each component exists

This is the rationale for the six-document system. Read this when the user asks "why bother" or when you need to defend a specific design choice.

## ROADMAP.md — strategic source of truth

**What it preserves.** Vision, scope, the small set of strategic decisions that shape the whole project (D1, D2, …), and the phased plan.

**What goes wrong without it.** New contributors guess at scope. Old debates resurface as if for the first time. Strategic decisions get re-litigated because no one wrote them down.

**Cadence.** Updated rarely — only when the strategy genuinely changes. ROADMAP is *not* a sprint board. If you find yourself updating it weekly, you've conflated strategy with tactics.

**Common mistakes:**

- Putting tactical decisions here ("we use Postgres" — that's an ADR).
- Making it a marketing doc. The audience is contributors, not stakeholders.
- Letting it go stale. If the project's direction has actually shifted and ROADMAP says otherwise, update it in the same commit as the strategic change.

## docs/decisions/ — Architecture Decision Records

**What it preserves.** The reasoning for non-obvious tactical choices: alternatives considered, why this one won, what we accepted and what we foreclosed.

**What goes wrong without it.** Three months later, someone proposes the same alternative we rejected. Nobody remembers why we rejected it. Either we waste a week relitigating, or we silently flip the decision and forget the reasoning we had.

**Why ADRs are immutable.** The point is to record *what we believed when we decided*. Editing a past ADR rewrites history and destroys the audit trail. To change a decision, write a new ADR with status `accepted`, mark the old one `superseded by ADR-NNNN`, and link forward and backward. Both stay in the folder. Anyone reading later can see the evolution.

**Why cross-references to ROADMAP phases matter.** An ADR is a tactical choice that serves a strategic goal. If you can't articulate which phase / strategic decision the ADR serves, you may not have a clear enough strategy — or the choice may not actually be load-bearing enough to need an ADR.

**Common mistakes:**

- Writing ADRs for trivial things (variable naming, internal helper structure). ADRs are for choices that have alternatives.
- Editing accepted ADRs. Always supersede instead.
- Renumbering. ADR-0007 stays ADR-0007 forever, even if it's later superseded.
- Forgetting the *Alternatives considered* section — without it, the ADR is just an assertion, not a record of reasoning.

## docs/backlog/ — feedback log + improvements queue

**What it preserves.** Two distinct things, deliberately separated:

- `feedback.md` — chronological **observations** (`FB-NNN`). Raw signal: what someone said, what we noticed, what failed. Some becomes work; some doesn't.
- `improvements.md` — prioritized **commitments to act** (`IMP-NNN`). Each has a status (proposed → accepted → scheduled → in-progress → done / wontfix), an explanation of why it matters, and possible approaches.

**Why split them.** Without separation, all feedback gets either filtered out (lost) or promoted to work (overwhelming). The split lets you record *everything* in feedback while keeping improvements small and prioritized.

**What goes wrong without it.** "I'll remember that idea" — you won't. Or feedback gets dumped into a generic issue tracker and disappears among bug reports. Or improvements get implemented without anyone remembering why they were prioritized over alternatives.

**Cross-references with ADRs.** Some feedback triggers a *decision* (an ADR), not just *work* (an improvement). When the feedback is interesting enough to warrant capturing the reasoning, link the resulting ADR back to the feedback. Both records belong: the feedback shows *what surfaced the problem*, the ADR shows *how we decided*.

**Common mistakes:**

- Filtering feedback before recording it ("this isn't worth writing down"). Record raw observations even if no immediate action is planned. Future-you will thank present-you.
- Conflating feedback and improvements. They have different shapes and lifecycles.
- Letting `wontfix` be invisible. If you decide not to act on something, mark the improvement `wontfix` with the reason. Silently abandoning it loses the *why we said no*.

## docs/rubric.md — pre-implementation feature checklist

**What it preserves.** The questions that integration tests, lint, and build can't catch: failure modes, liveness, security, escape hatches, cost, lifecycle. Numbered (R1.1, R1.2, …, R10.x) so they can be cited unambiguously.

**Why "before AND after."** Before implementing, the rubric forces design questions into existence — for each item, the developer decides *handle now / defer with backlog entry / wontfix with reason*. Anything not addressed is now a *known gap*, not a surprise. After implementing, the rubric is verification — *is this true now?* The first walk catches missing-case bugs at the cheapest possible point. The second walk catches "I thought I handled it but I actually didn't."

**Why numbered.** A change can cite "Addresses R3.4, R5.1; defers R7.2 → IMP-007" in its CHANGELOG entry. This makes the audit trail concrete and reviewable. Without numbers, "we walked the rubric" is unfalsifiable.

**Why a single rubric, not per-feature checklists.** Per-feature checklists rot. A single, evolving rubric with stable IDs is the artifact that gets better over time. Add new items as the project's domain reveals new categories of bugs. Drop or reword items that are consistently irrelevant.

**Common mistakes:**

- Treating the rubric as paperwork. The point is to *catch problems before they ship*; if you walk it but don't act on misses, it's theatre.
- Letting the rubric grow without pruning. Items that haven't been useful in 6 months should be considered for removal — or rewriting if they're conceptually right but worded poorly.
- Skipping the rubric on "small" features. The features that look small are often the ones that surprise you.

## docs/learning/ — knowledge points

**What it preserves.** Transferable concepts that emerged from real project work. Each `KP-NNN` is: a one-sentence concept definition, a concrete reference to project work, a *why it matters* divorced from this specific project, and links.

**Why the AI collaborator proposes them.** When working with capable AI assistance, it's possible to ship a lot of code without internalizing the concepts. KPs are a deliberate counter-balance: at meaningful moments, the AI proposes naming a transferable concept the human just practiced. The human can accept, edit, or decline.

**Why "transferable" matters.** A KP is *not* "we used React 19." It's something that would be useful on a different project, in a different language, in a different domain. Examples: "liveness signals must be tied to real data flowing," "the agent loop is a primitive, not a feature," "partial outputs are the rule, not the exception." If a candidate KP doesn't generalize, it's not a KP.

**Trigger volume.** A handful per project phase, not per commit. Quality over quantity. The point is to leave a trail of named concepts the human can revisit, not to generate a glossary of every minor pattern.

**Common mistakes:**

- Writing too many. Five excellent KPs are worth more than fifty mediocre ones.
- Making KPs project-specific. Always include a *why it matters beyond this project* paragraph.
- Skipping the *what we did* link. Without a concrete project artifact, the KP is an abstract platitude.

## CHANGELOG.md — chronological history

**What it preserves.** What shipped, when, in which phase, with cross-references to all the other documents.

**Why cross-references in every entry.** A CHANGELOG entry without rubric IDs, ADR links, or backlog references is *not* part of the system. It's just a commit message in markdown. The cross-references are how the system surfaces "why" to anyone reading later.

**Why phase-organized, newest-on-top.** Phase organization makes it easy to summarize "what shipped in Phase 1." Newest-on-top means recent context is reachable without scrolling.

**What goes wrong without it.** Each contributor remembers the last 3 months. The first 6 months of the project are a blur. New contributors have to spelunk git logs to reconstruct *what shipped* (vs. *what was attempted*). The audit trail is incomplete.

**Common mistakes:**

- Reusing commit messages verbatim. CHANGELOG entries are *narrative* — what changed, what triggered it, what's worth noting. Commit messages are *what was different in this revision*.
- Forgetting cross-references. The entry is supposed to be the entry point to the audit trail.
- Letting it lapse. Each meaningful change → entry. Skipping a few makes it unreliable.

## How the system fails

The system works when the cross-linking is real. It fails when:

- People treat it as paperwork (checkbox theatre).
- Cross-references are aspirational rather than enforced (an entry that *should* link to an ADR but doesn't, because the ADR doesn't exist).
- Templates are used verbatim without customization.
- The rubric exists but is never cited.
- The KP folder collects entries that are project-specific facts ("we use port 3000"), not transferable concepts.

Failure shows up as: contributors not finding answers in the docs, decisions getting silently flipped without an ADR, the same arguments recurring, new sessions (especially AI sessions) re-litigating settled choices because the audit trail isn't actually reachable.

If you see these symptoms, the fix is rarely "more docs." It's "fix the cross-linking on the docs you have, and treat the system as load-bearing instead of optional."
