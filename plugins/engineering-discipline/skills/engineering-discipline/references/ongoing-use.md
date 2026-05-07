# Ongoing use — cadence, triggers, and quality bars

After bootstrap, the system needs to be used to be useful. This file is the day-to-day reference for *when* and *how* to write each kind of entry.

## Writing a CHANGELOG entry

**Trigger:** Every meaningful change. Trivial changes (typo fix, dependency bump, doc-only update) are exempt.

**Where it goes:** Top of `CHANGELOG.md`, under the current phase header. Newest entries on top.

**Required fields:**

- A short title (one line)
- **Triggered by:** what motivated the change — bug, user feedback (link FB-NNN), decision, observation
- **Changes:** bulleted list of what changed, file paths where useful, links to ADRs and backlog
- **Rubric items addressed:** explicit citation by ID (`Addresses R3.4, R5.1; defers R7.2 → IMP-NNN`)
- **ADRs added** (if any)
- **Backlog entries added** (if any)

**Quality bar:** A reader six months from now should be able to reconstruct *why* this change was made and which trade-offs it accepted, without reading the code.

## Writing an ADR

**Trigger:** A non-obvious tactical decision is being made — something with real alternatives that someone could later legitimately propose changing.

**Threshold for "non-obvious":** if you'd hesitate to lose the reasoning, or if you can imagine someone in 3 months proposing a different approach, write the ADR.

**Where it goes:** `docs/decisions/NNNN-<short-slug>.md`, where `NNNN` is one greater than the current highest in the index.

**Required sections:** see the per-ADR template (`docs/decisions/template.md`). All sections are required:

- Status (`accepted` / `superseded by ADR-NNNN`)
- Date
- Context (the problem, in enough detail that someone unfamiliar with the moment can understand)
- Decision (what we chose, specifically enough that the implementation could be reconstructed)
- Alternatives considered (with reasons rejected)
- Consequences (positive AND negative — what does this commit us to, what does it foreclose)
- Roadmap alignment (which phase / strategic decision this serves)

**The Alternatives section is non-negotiable.** Without it, the ADR is an assertion, not a record of reasoning. Always list at least one alternative — even if you rejected it quickly.

**Quality bar:** Read it six months later. If you can reconstruct *why we picked this and not the alternatives*, it's good enough. If you can't, rewrite the Context or Alternatives sections.

## Writing a feedback entry

**Trigger:** Anyone (user, contributor, AI collaborator, future-you) identifies a problem or suggests an improvement that isn't being addressed in the current commit.

**Where it goes:** `docs/backlog/feedback.md`, top of the file (newest on top), with the next `FB-NNN` ID.

**Required fields:**

- ID, date, source
- Verbatim quote (when applicable) or paraphrase
- Observation context — what was happening, what was tried, what the consequence is
- Triggered improvement: link to `IMP-NNN` if the feedback became one (set this later if the link doesn't exist yet)

**Don't filter.** Record raw observations even if no immediate action is planned. Future-you decides what's actionable; present-you doesn't have enough information to decide.

## Writing an improvement entry

**Trigger:** Feedback (or independent reflection) identifies a concrete change to make later.

**Where it goes:** `docs/backlog/improvements.md`, top of the file (newest on top), with the next `IMP-NNN` ID.

**Required fields:**

- ID, status (`proposed` / `accepted` / `scheduled-phase-N` / `in-progress` / `done` / `wontfix`)
- Source — `Source: FB-NNN` if it came from feedback, or `Internal observation` otherwise
- Target phase
- **Why it matters** — user-facing impact, in plain language
- **Possible approaches** — sketch the options and the trade-offs; this is *not* the final decision (that's an ADR), it's the menu
- Cross-references — feedback entries, related ADRs, related KPs

**Status discipline.** Update the status as work progresses. Don't delete entries when they're done — keep them with status `done` and a link to the CHANGELOG entry that implemented them. The historical record matters.

## Walking the rubric

**Before implementing a feature:**

1. Open `docs/rubric.md`.
2. For every item (R1.1, R1.2, … through R10.x), make a decision:
   - **Handle now** — implement an answer in this change
   - **Defer** — file an `IMP-NNN` for later
   - **Wontfix** — explicitly decide not to address it, with reason
3. Note which items will be cited in the CHANGELOG entry.

**After implementing the feature:**

1. Re-walk the rubric against the actual code and behavior.
2. For each item: is the answer *true now*?
3. If not, fix it before declaring done — or update the deferral / wontfix.

**Citation format in CHANGELOG:** `Addresses R3.4, R5.1, R6.1; defers R7.2 → IMP-NNN; wontfix R10.3 (project is single-tenant).`

## Proposing a knowledge point (AI collaborator's responsibility)

**Trigger moments:**

- A major feature shipped and a name can be put on the pattern it embodied
- Feedback revealed a transferable principle (the FB → KP pattern is common — the feedback is project-specific, the KP is general)
- A significant ADR was accepted whose reasoning generalizes beyond this project
- A phase transition

**Trigger volume target:** A handful per phase, not per commit. Quality over quantity.

**Required fields:**

- ID (next `KP-NNN`), title, date
- **Concept** — one-sentence definition
- **What we did** — concrete reference to project work (file paths, ADR numbers, commit timing)
- **Why it matters** — the general principle, divorced from this specific project; where this comes up in other work
- **See also** — links to ADRs, feedback, code

**Quality bar for "transferable."** A KP is not "we used X library." It's a concept that would be useful on a different project, in a different language, in a different domain. Examples that pass: "liveness signals must be tied to real data flowing," "the agent loop is a primitive, not a feature." Examples that fail: "we use port 3000," "DeepSeek silently ignores cache_control."

**Workflow when AI proposes:**

1. AI surfaces the proposal in chat: "I'd like to add KP-NNN: <title>. Concept: <one sentence>. Want me to draft it?"
2. Human accepts, edits, or declines.
3. If accepted, AI writes the entry. Human reviews on next cycle and refines.

The AI should default to *under-proposing* rather than over-proposing. A KP that the human declines is fine; a KP that the human edits heavily is also fine. A KP that's mediocre and gets accepted is the failure mode.

## Updating the ROADMAP

**Trigger:** A strategic decision changes (something at the level of D1–DN), or a phase wraps and the next phase needs to be specified.

**This should happen rarely.** If you find yourself updating ROADMAP weekly, you're conflating tactical and strategic decisions. Tactical changes go in ADRs.

**When updating:**

- Add a new strategic decision: `Dn`. Don't renumber existing ones.
- Update phase deliverables when an entire phase pivots.
- Update the document map if the doc structure changes (rare).

**Don't update for:**

- New ADRs (they reference ROADMAP, not the other way around)
- New backlog entries
- New CHANGELOG entries
- New KPs

## Anti-patterns to watch for

- **Templates leaking.** Placeholder content like *"<your project name>"* appearing in real docs. Always customize before considering bootstrap done.
- **Aspirational cross-links.** A CHANGELOG entry that says *"see ADR-0007"* when ADR-0007 doesn't exist. Either write the ADR or remove the link.
- **Renumbering.** Once an ID is assigned (ADR-NNNN, FB-NNN, IMP-NNN, KP-NNN, R-N.N), it's stable forever. Gaps in the sequence are fine.
- **Editing accepted ADRs.** Always supersede instead.
- **Filtering feedback.** Record raw, decide later.
- **Letting CHANGELOG become commit messages.** A CHANGELOG entry is narrative, not a `git log --oneline` excerpt.
- **KP overproduction.** Five excellent KPs > fifty mediocre ones.

## Health checks

Periodically (e.g. once per phase wrap-up), audit the system:

- Does each ADR have a `Roadmap alignment` section that references a real phase?
- Does each `done` improvement have a CHANGELOG link?
- Does each CHANGELOG entry from the last quarter have rubric citations? If many don't, the rubric isn't being walked.
- Are KPs accumulating at all? Zero KPs over a 3-month phase suggests the AI collaborator isn't proposing them.
- Has any ADR been silently superseded (decision changed in code, no new ADR)? Search recent commits for architectural changes; cross-check against the ADR index.

If any of these checks fail, fix them. The system is load-bearing only when it's actually maintained.
