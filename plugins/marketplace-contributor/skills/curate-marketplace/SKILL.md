---
name: curate-marketplace
description: |
  Run a maintenance / lint pass over the ray-skills marketplace so knowledge compounds instead of rotting. Use this when the user wants to audit the marketplace, check that skills and plugins are healthy, find broken or stale skills, clean up after adding several plugins, or asks "is the marketplace consistent / anything broken". Catches weak skill descriptions, broken reference links, name drift, unregistered or dangling plugins, missing files, orphan reference docs, oversized SKILL.md files, and stale Claude Code feature references.
  Trigger when the user says things like: "lint the marketplace", "curate the marketplace", "audit my skills/plugins", "is anything broken / stale", "clean up the marketplace", or "run a maintenance pass".
---

# Curate the ray-skills Marketplace

The counterpart to `contribute-skill`. That skill *creates*; this one *maintains*. Inspired by the lint pass in Karpathy's LLM Wiki pattern — a knowledge base that is only ever appended to accumulates contradictions, stale claims, and orphan pages. This pass surfaces and fixes that rot for the marketplace, where the "pages" are plugins and skills.

## Workflow

### Step 1 — Run the deterministic lint script
Mechanical checks (file existence, JSON validity, name consistency, registration, broken links, orphans, size) are scripted so they're cheap and repeatable:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/curate-marketplace/scripts/lint.py" <marketplace-root>
```
(omit the path argument to auto-detect the repo root by walking up to `.claude-plugin/marketplace.json`). It prints findings grouped as **ERROR / WARNING / INFO** and exits non-zero if any ERRORs exist. Run it first and use its output as the spine of the report.

What the script checks:
- **Registration** — plugin folder on disk but not in `marketplace.json`; or registered but its `plugin.json` is missing (**dangling entry**).
- **Name drift** — folder name vs `plugin.json` `name`.
- **Skill integrity** — `SKILL.md` exists, has frontmatter with `name` + `description`; description not empty/too-short/over the ~1536-char budget.
- **Broken links** — relative links in `SKILL.md` to `references/`/`scripts/`/`assets/` that don't resolve.
- **Orphans** — files under `references/` not linked from `SKILL.md` (LLM Wiki "orphan page").
- **Oversize** — `SKILL.md` over 300 / 500 lines (split into `references/`).
- **JSON validity** — every manifest parses.

### Step 2 — Add the semantic checks (agent judgment)
The script can't judge meaning. Read each flagged `SKILL.md` (and skim the rest) and assess:
- **Weak descriptions** — does the description contain the user's own words, named tools/objects, and concrete trigger phrasings? A vague summary won't trigger reliably.
- **Stale feature references** — does any skill reference Claude Code features/paths/commands that have changed or no longer exist? (Cross-check against current docs if unsure.)
- **Contradictions / duplication** — do two skills claim to own the same trigger space, or give conflicting instructions? Note overlaps; recommend merging or disambiguating descriptions.
- **Missing cross-references** — a concept covered in one skill that another should link to but doesn't.

### Step 3 — Produce a fix checklist
Report findings as a single prioritized checklist, ERRORs first, each with the file path (as a markdown link) and a one-line fix. Separate **auto-fixable** (broken link typo, missing registration entry, name drift, JSON formatting) from **needs-judgment** (rewrite a weak description, merge duplicate skills).

### Step 4 — Fix, with consent for anything destructive
Apply safe auto-fixes directly (register a missing plugin, repair a broken link, fix a name mismatch, reformat JSON). For anything that changes meaning or removes content (rewriting descriptions, merging/deleting skills, removing a dangling entry that belongs to in-flight work) — confirm with the user first. Be especially careful with **dangling entries**: a plugin registered in `marketplace.json` whose files aren't committed yet is often another session's work-in-progress, not garbage — ask before removing.

### Step 5 — Log and re-run
After fixing, append a line to [log.md](log.md):
```
## [YYYY-MM-DD] curated | <scope> | <n> errors / <n> warnings fixed
```
Then re-run the lint script to confirm a clean pass, and report the before/after counts.

## Notes
- This skill is read-mostly; it should never push or commit unless the user asks. Publishing fixes follows the same rule as `contribute-skill` (push to `main`).
- Keep the script dependency-free (stdlib only) so it runs anywhere without setup.
