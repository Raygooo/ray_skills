# Skill Authoring Reference

Deep reference for writing a single `SKILL.md`. Load when the workflow reaches "write the skill". For the surrounding plugin wiring see `plugin-components.md`.

> Source: https://code.claude.com/docs/en/skills

## Delegate to `skill-creator` first

Before hand-writing a skill, check whether the built-in **`anthropic-skills:skill-creator`** skill is available (it ships with Cowork/Claude Code). It is the canonical tool for *creating, editing, and evaluating* skills, and it handles structure, description optimization, and evals far better than improvising.

**Recommended division of labor:**

1. Invoke `/skill-creator` (or let it auto-trigger) to scaffold and refine the `SKILL.md` + supporting files for the new capability.
2. Then return here and apply the **marketplace-specific** steps that `skill-creator` does *not* know about: dropping the skill into `plugins/<plugin>/skills/`, writing `plugin.json`, registering in `marketplace.json`, updating the README, and pushing to `main`.

If `skill-creator` is not present, this reference is self-contained enough to author a good skill by hand. Either way, a skill may invoke another skill at runtime by referencing its slash form — e.g. *"run `/anthropic-skills:skill-creator`"* or *"hand off to `/marketplace-contributor:contribute-skill`"*. That is the closest thing to a "sub-skill": there is no nested-skill file format, only cross-invocation.

## SKILL.md frontmatter — full field reference

Only `description` really matters for triggering; everything else is optional.

| Field | Purpose |
|---|---|
| `name` | Display name; defaults to the directory name. |
| `description` | **The trigger contract.** What the skill does + when to use it + example phrasings. |
| `when_to_use` | Extra trigger context appended to `description`. Combined cap ≈ **1,536 chars**. |
| `allowed-tools` | Pre-approve tools while the skill is active (e.g. `"Read, Grep, Bash"`). Reduces permission prompts. |
| `disallowed-tools` | Deny tools while the skill is active. |
| `disable-model-invocation` | `true` ⇒ only runs when the user types `/skill`; Claude won't auto-trigger it. Use for destructive/controlled flows (deploys, commits). |
| `user-invocable` | `false` ⇒ hide from the `/` menu (still usable via the Skill tool). |
| `model` | Model override for this skill. |
| `effort` | Effort level override (`low`/`medium`/`high`/…). |
| `context` | Set to `fork` to run the skill body in a subagent instead of the main context. |
| `agent` | Subagent type to use when `context: fork` (e.g. `Explore`). |
| `paths` | Glob(s) that auto-surface the skill when matching files are in play (e.g. `"src/**/*.ts"`). |
| `argument-hint` / `arguments` | Autocomplete hint and named positional args for `$1`/`$name` substitution. |
| `hooks` | Skill-scoped hooks (advanced). |

Minimal good frontmatter:

```markdown
---
name: <skill-name>
description: |
  <What it does, in one sentence.> Use this when the user wants to <intents>.
  Trigger when the user says things like: "<phrase>", "<phrase>", or asks to <intent>.
---
```

## What makes a description trigger reliably

- Lead with the capability, then list concrete user phrasings and symptoms — use the user's own words.
- Name the domain objects and tools involved ("Electron app", "Clash", "marketplace.json"), not just the mechanism.
- Disambiguate from near-miss skills inside the description.
- Don't over-promise — a description that claims too much fires on false positives.

## Progressive disclosure — where each piece goes

`SKILL.md` is **always** loaded when the skill triggers, so keep it lean (aim < 300 lines, hard sense-check at ~500). Push everything else outward:

| Content kind | Location | Loaded |
|---|---|---|
| Core workflow, decision logic, short examples | `SKILL.md` | always, on trigger |
| Long reference docs, schemas, field tables | `references/<topic>.md` | on demand (agent `Read`s it) |
| Executable helpers (Python/shell/Node) | `scripts/<name>.{py,sh,js}` | executed via Bash, never read as prose |
| Templates, images, skeleton configs, binaries | `assets/<name>.<ext>` | used as input, not instructions |

Rule of thumb: if content only matters on one branch of the workflow, move it out of `SKILL.md` and link to it by relative path so the agent knows when to pull it in. (This very skill is built that way — a lean `SKILL.md` plus this `references/` directory.)

Dynamic context: ``!`command` `` in a skill body runs the command and injects its output before Claude reads the content — handy for surfacing live repo state.
