---
name: contribute-skill
description: |
  Capture a workflow as a reusable Claude Code skill (and, when needed, a bundled subagent) for the local ray-skills marketplace, then publish it by pushing straight to the GitHub main branch. Use this when the user wants to save a procedure so future agents can follow it, add a skill to an existing plugin in this repo, scaffold a brand-new plugin, or package a repeatable multi-step / multi-agent workflow. Covers progressive disclosure (SKILL.md vs references/ vs scripts/ vs assets/), bundling subagents (agents/), delegating to the built-in skill-creator, and registering the plugin in marketplace.json.
  Trigger when the user says things like: "save this as a skill", "turn this workflow into a skill", "add a skill / subagent to the marketplace", "create a new plugin for this", "package this workflow", "contribute to my marketplace", or "remember how to do X as a skill".
---

# Contribute a Skill to the ray-skills Marketplace

Teaches you (the agent) how to capture a workflow as a skill — optionally with a bundled subagent — and publish it into this local marketplace by pushing directly to `main`, so future sessions load and trigger it automatically.

## Mental model

- **Marketplace** = this repo, indexed by [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).
- **Plugin** = a folder under `plugins/<name>/` grouping related capabilities around one theme. Can ship skills, subagents (`agents/`), slash commands, hooks, and MCP servers.
- **Skill** = `plugins/<plugin>/skills/<skill>/SKILL.md`. The *how* — a repeatable procedure. Claude reads every installed skill's `description` and loads the body only when it matches — the description is the trigger contract.
- **Knowledge** = `plugins/<plugin>/knowledge/*.md` (optional). The *what / why* — durable domain facts and concept pages, decoupled from any single procedure, that skills link to. Borrowed from the entity-page idea in Karpathy's LLM Wiki; not auto-loaded, so a skill must reference it.
- **Subagent** = `plugins/<plugin>/agents/<name>.md`, a specialized isolated-context role for heavy/reusable steps.
- **Evolution log** = [log.md](log.md) at the repo root — append-only record of every distillation/curation, so the marketplace's growth compounds and stays auditable.

There is **no declarative "workflow" file** — a "workflow" is just a skill (the repeatable procedure) plus, when a step needs isolation/reuse, one or more subagents. See [references/orchestration.md](references/orchestration.md) before promising any multi-agent primitive.

Deep references (load on demand — don't inline them here):
- [references/skill-authoring.md](references/skill-authoring.md) — full SKILL.md frontmatter, progressive disclosure, delegating to `skill-creator`.
- [references/plugin-components.md](references/plugin-components.md) — full `plugin.json` schema, all component dirs, agent frontmatter, path variables.
- [references/orchestration.md](references/orchestration.md) — subagents vs agent teams vs `/batch`; when to bundle an agent.

## Workflow

### Step 1 — Clarify what to capture
Confirm with the user: (1) the workflow in one sentence; (2) the trigger phrases that should wake it; (3) whether it needs scripts, reference docs, assets, or a **subagent** for a heavy/isolated step. If vague, propose a concrete shape and let them correct you.

### Step 2 — Prefer delegating skill authoring to `skill-creator`
If `anthropic-skills:skill-creator` is available, use it to scaffold and refine the actual `SKILL.md` (it handles structure, description tuning, and evals). Then come back here for the marketplace-specific wiring below. If it's not available, author by hand using [references/skill-authoring.md](references/skill-authoring.md). A skill invokes another skill simply by referencing its slash form (e.g. `/anthropic-skills:skill-creator`) — that's the only "sub-skill" mechanism.

### Step 3 — New plugin, or add to an existing one?
Judge by theme, not file count. Add to an existing plugin if it shares that plugin's core theme; otherwise create a new plugin. Prefer a new, focused plugin when in doubt — narrow descriptions trigger more reliably.

### Step 4 — Create the files
Layout (only the parts you need):
```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json        # only this file lives in .claude-plugin/
├── skills/<skill-name>/
│   ├── SKILL.md                      # always loaded on trigger — keep lean
│   ├── references/   (optional)      # loaded on demand
│   ├── scripts/      (optional)      # executed via Bash
│   └── assets/       (optional)      # templates/binaries
├── knowledge/        (optional)      # durable domain facts (what/why), shared across skills
└── agents/<agent-name>.md  (optional) # bundled subagent
```
Names are lowercase-hyphenated; the plugin's directory name must equal the `name` field in both `plugin.json` and `marketplace.json`. `SKILL.md` is uppercase exactly. Full schemas: [references/plugin-components.md](references/plugin-components.md).

### Step 5 — Write SKILL.md and apply progressive disclosure
Keep core workflow + decision logic in `SKILL.md`; push long reference material to `references/`, executables to `scripts/`, templates/binaries to `assets/`, and durable domain facts (the *what/why*, reusable across skills) to plugin-level `knowledge/*.md`. Reference each by relative path so the agent knows when to pull it in. Make the `description` specific (capability + concrete trigger phrasings). Details and the full field table: [references/skill-authoring.md](references/skill-authoring.md).

### Step 6 — (If the workflow needs it) Bundle a subagent
If a step needs an isolated context, a different model/toolset, or is a reusable named role, add `agents/<name>.md` (see [references/orchestration.md](references/orchestration.md) for the decision and [references/plugin-components.md](references/plugin-components.md) for the frontmatter). Plugin agents may not declare `hooks`, `mcpServers`, or `permissionMode`.

### Step 7 — (If new plugin) Write plugin.json
```json
{
  "name": "<plugin-name>",
  "description": "<one-line description>",
  "version": "0.1.0",
  "author": { "name": "raygooo", "email": "lovzoe@hotmail.com" },
  "repository": "https://github.com/Raygooo/ray_skills",
  "license": "MIT",
  "keywords": ["..."]
}
```

### Step 8 — (If new plugin) Register + document
Append to the `plugins` array in [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) (don't reorder existing entries):
```json
{ "name": "<plugin-name>", "source": "./plugins/<plugin-name>", "description": "<same one-liner>" }
```
Then add a `###` section under `## Plugins` in [README.md](README.md): name, problem it solves, `**Skills included:**` (`plugin:skill` ids), `**Trigger phrases:**`.

### Step 9 — Verify before publishing
- [ ] `plugin.json` exists; `name` matches the folder.
- [ ] `SKILL.md` has valid YAML frontmatter with `name` + a concrete `description`.
- [ ] `marketplace.json` still parses (no trailing commas) and README has the new section.
- [ ] Every referenced `references/`/`scripts/`/`assets/` file and any `agents/*.md` actually exists.
- [ ] (If JSON touched) `python3 -c "import json,sys; json.load(open(sys.argv[1]))" <file>` passes.

### Step 10 — Record in the evolution log
Append one line to [log.md](log.md) at the repo root so the marketplace's growth stays auditable:
```
## [YYYY-MM-DD] <kind> | <plugin>:<skill> vX.Y.Z | from: <source workflow / note>
```
`<kind>` ∈ `distilled` (new), `updated` (revised), `superseded` (replaced). Use today's date. Include this in the same commit as the change.

### Step 11 — Publish: push straight to `main`
This marketplace publishes by **committing and pushing directly to the `main` branch — no pull request**. The repo's default branch is `main` (verify with `git remote show origin | grep 'HEAD branch'`).

```bash
git add -A
git commit -m "<what changed and why>

Co-Authored-By: Claude <noreply@anthropic.com>"
# If currently on a feature/worktree branch, land it on main and push:
git push origin HEAD:main
# If already on main: git push origin main
```

If the local `main` is checked out elsewhere and you committed on another branch, fast-forward main first (`git fetch . <branch>:main` or merge) then `git push origin main`. After pushing, tell the user how to pick up the change:
```
/plugin marketplace update ray-skills
/plugin install <plugin-name>@ray-skills      # for a newly added plugin
```
Already-installed plugins may need `/plugin marketplace update` + a restart to reload. Report the pushed commit and all created/modified paths as markdown links.

## Common mistakes to avoid
- **Weak descriptions** — must contain the user's own words and named tools, not a vague summary.
- **Everything in SKILL.md** — split anything > ~300 lines into `references/`.
- **Name drift** — directory name, `plugin.json` name, and `marketplace.json` name must match exactly.
- **Misplacing files** — only `plugin.json` goes in `.claude-plugin/`; `skills/`, `agents/`, `hooks/` live at plugin root.
- **Inventing a "workflow" primitive** — there isn't one; ship a skill (+ subagent). See [references/orchestration.md](references/orchestration.md).
- **Forgetting to push** — publishing here means the change is on `main`; a local-only commit is not published.

## Worked examples
- [plugins/proxy-app-launcher](../../../proxy-app-launcher) — single-skill plugin with a bundled `scripts/` helper.
- [plugins/marketplace-contributor](../..) — this plugin; lean `SKILL.md` + a `references/` directory demonstrating progressive disclosure.
