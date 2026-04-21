---
name: contribute-skill
description: |
  Author a new skill for the local ray-skills marketplace and publish it locally. Use this when the user wants to capture a workflow as a reusable skill, save a procedure so future agents can follow it, add a skill to an existing plugin in this repo, or scaffold a brand-new plugin around a new skill. Also covers progressive disclosure (when to put content in SKILL.md vs. references/ vs. scripts/ vs. assets/) and how to register the plugin in marketplace.json so Claude Code picks it up.
  Trigger when the user says things like: "save this as a skill", "turn this workflow into a skill", "add a skill to the marketplace", "create a new plugin for this", "contribute to my marketplace", "remember how to do X as a skill", or otherwise asks to formalize a procedure into a loadable skill in this repo.
---

# Contribute a Skill to the ray-skills Marketplace

This skill teaches you (the agent) how to capture a workflow as a skill and publish it into this local marketplace so future sessions can load and trigger it automatically.

## Mental model

A **marketplace** is this repo. It is indexed by [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

A **plugin** is a folder under `plugins/<plugin-name>/` that groups related skills (and optionally commands, hooks, agents) around a single theme.

A **skill** is a folder under a plugin's `skills/<skill-name>/` with a `SKILL.md` file. Claude Code reads the frontmatter of every installed skill and decides when to load the body based on the `description` field — so the description is the skill's trigger contract.

Content the user wants to save as a skill can include: **documents, knowledge, scripts, assets, and more**. Put each in the right place per the progressive-disclosure rules below.

## Workflow

### Step 1 — Clarify what the user wants to capture

Before writing anything, confirm with the user:

1. What is the workflow / procedure / knowledge being captured? Ask them to describe it in one sentence.
2. What trigger phrases should wake this skill up? ("When I say X, run this skill.")
3. Does it involve executable steps (scripts), reference docs (large content that shouldn't always be loaded), or bundled assets (templates, images)?

If the user is vague, propose a concrete shape and let them correct you.

### Step 2 — Decide: new plugin, or add to an existing one?

Look at `plugins/` and judge by theme, not by file count.

- **Add to an existing plugin** if the new skill shares the plugin's core theme (e.g. another macOS launcher trick → goes in `proxy-app-launcher`, or arguably a sibling plugin about launchers).
- **Create a new plugin** if the skill is a distinct concern with its own identity. Prefer this when in doubt — plugins are cheap, and a focused plugin description triggers more reliably than a grab-bag one.

### Step 3 — Directory layout

Create files to match this structure:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md          # always loaded when the skill triggers
        ├── references/       # optional — loaded on demand via Read
        │   └── *.md
        ├── scripts/          # optional — executable via Bash
        │   └── *.{sh,py,js,...}
        └── assets/           # optional — templates, images, binary inputs
            └── *
```

Naming conventions:

- Plugin name: lowercase, hyphen-separated, descriptive of the theme (e.g. `proxy-app-launcher`, `marketplace-contributor`).
- Skill name: lowercase, hyphen-separated, reads as a verb phrase or noun describing the capability (e.g. `contribute-skill`, `proxy-app-launcher`).
- `SKILL.md` must be uppercase exactly like that — the loader looks for this filename.

### Step 4 — Write SKILL.md

The frontmatter and body together form the skill. Template:

```markdown
---
name: <skill-name>
description: |
  <One paragraph explaining what the skill does and when to use it. This is the trigger contract — be specific about user intents, example phrasings, and scenarios. Claude only loads the body when this description matches.>
  Trigger when the user says things like: "...", "...", or otherwise asks to ...
---

# <Human-Readable Title>

<One or two sentences: what problem this skill solves and why it exists.>

## Workflow

### Step 1 — ...
### Step 2 — ...
...

## Troubleshooting (optional)

| Issue | Cause | Fix |
|---|---|---|
| ... | ... | ... |
```

Rules for a good `description`:

- Lead with what the skill does. Follow with concrete trigger phrases/intents.
- Include the problem domain, not just the mechanism. ("Fix Electron apps ignoring system proxy" > "Make .app bundles").
- If there are near-miss skills the agent might confuse this with, disambiguate inside the description.
- Keep it focused — a description that promises too much triggers on false positives.

### Step 5 — Apply progressive disclosure

Decide where each piece of content lives. `SKILL.md` is **always** loaded when the skill triggers — keep it lean.

| Content kind | Where it goes | Why |
|---|---|---|
| Core workflow, decision logic, short examples | `SKILL.md` | Always needed when the skill fires |
| Long-form reference docs, API schemas, deep explanations | `references/<topic>.md` | Read on demand only when the workflow hits that branch |
| Reusable executable helpers (Python, shell, Node) | `scripts/<name>.{py,sh,js}` | Invoked via Bash; don't inline large scripts into SKILL.md |
| Templates, images, `.icns` files, skeleton configs | `assets/<name>.<ext>` | Copied or used as input; not read as instructions |

Inside `SKILL.md`, reference these files by relative path so the agent knows to load them, e.g. *"see `references/plist-schema.md` for the full Info.plist reference"* or *"run `scripts/generate_icon.py`"*.

Rule of thumb: if content is only relevant to one branch of the workflow, move it out of SKILL.md.

### Step 6 — (If new plugin) Write plugin.json

Create `plugins/<plugin-name>/.claude-plugin/plugin.json`:

```json
{
  "name": "<plugin-name>",
  "description": "<one-line plugin description — shown in /plugin listings>",
  "version": "0.1.0",
  "author": {
    "name": "raygooo",
    "email": "lovzoe@hotmail.com"
  },
  "repository": "https://github.com/Raygooo/ray_skills",
  "license": "MIT",
  "keywords": ["...", "..."]
}
```

The `name` field must match the directory name.

### Step 7 — (If new plugin) Register in marketplace.json

Edit `.claude-plugin/marketplace.json` at the repo root and append to the `plugins` array:

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "<same one-line description as plugin.json>"
}
```

Do not re-order or modify other entries.

### Step 8 — (If new plugin) Update the top-level README.md

Add a new `###` subsection under `## Plugins` following the style of existing entries:

- Plugin name as heading
- One-paragraph description of the problem it solves
- `**Skills included:**` list with `plugin:skill` identifiers
- `**Trigger phrases:**` list — short quoted examples pulled from the skill description

This README is the human-facing index; keep it in sync.

### Step 9 — Publish locally

"Local publishing" in this marketplace is purely a file operation — no git push, no remote registry. After the files are in place:

1. If this marketplace is not yet registered in the user's Claude Code, tell the user to run:
   ```
   /plugin marketplace add <absolute-path-to-this-repo>
   ```
   (or the GitHub short form if they already use the remote version)
2. To install a newly added plugin:
   ```
   /plugin install <plugin-name>@ray-skills
   ```
3. To pick up changes to an already-installed plugin, the user may need to restart Claude Code or re-install the plugin. Tell them which.

Do **not** run `git push`, open PRs, or publish to any remote registry as part of this skill — the user will do that separately if/when they choose.

### Step 10 — Verify

Before declaring done, confirm:

- [ ] `plugins/<plugin-name>/.claude-plugin/plugin.json` exists and `name` matches the folder.
- [ ] `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` exists with valid YAML frontmatter (`name` and `description` present).
- [ ] If a new plugin: the entry in `.claude-plugin/marketplace.json` parses as valid JSON (no trailing commas).
- [ ] If a new plugin: README.md has a new `###` section.
- [ ] All referenced `references/`, `scripts/`, `assets/` files actually exist.
- [ ] The skill's `description` contains concrete trigger phrases — not just a summary.

Report the created/modified paths back to the user as markdown links.

## Common mistakes to avoid

- **Weak descriptions.** A description like "helps with proxies" will never trigger reliably. Include the user's own words, the symptoms they describe, and the named tools/objects involved.
- **Everything in SKILL.md.** If SKILL.md crosses ~300 lines, split long reference material into `references/`.
- **Forgetting marketplace.json.** A plugin folder that is not registered will not be discoverable by users browsing the marketplace.
- **Name drift.** The directory name, the `name` field in `plugin.json`, and the `name` field in `marketplace.json` must all match exactly.
- **Non-local publishing.** This skill's scope ends at local file changes. Do not commit, push, or publish externally unless the user explicitly asks.

## Example shape

See this repo's own plugins for worked examples:

- [plugins/proxy-app-launcher](plugins/proxy-app-launcher) — a single-skill plugin with a bundled Python script under `scripts/`.
- [plugins/marketplace-contributor](plugins/marketplace-contributor) — this plugin; a skill-only plugin with no bundled assets yet.
