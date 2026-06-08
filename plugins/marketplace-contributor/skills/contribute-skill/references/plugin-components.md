# Plugin Components Reference

Everything a Claude Code plugin can ship, with exact paths and field names. Load this when you need the full schema — `SKILL.md` only summarizes.

> Source: https://code.claude.com/docs/en/plugins-reference and https://code.claude.com/docs/en/plugins

## Canonical directory layout

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # the ONLY file that lives inside .claude-plugin/
├── skills/                  # skills (preferred unit of capability)
│   └── <skill-name>/SKILL.md
├── commands/                # legacy flat slash commands — prefer skills/ for new work
│   └── <command>.md
├── agents/                  # subagents (specialized roles) — see orchestration.md
│   └── <agent-name>.md
├── hooks/
│   └── hooks.json           # event-driven automation
├── knowledge/               # durable domain facts / concept pages (not a Claude Code
│   └── <topic>.md           #   primitive — just markdown that skills link to on demand)
├── .mcp.json                # bundled MCP servers
├── .lsp.json                # bundled LSP servers
├── settings.json            # default settings applied when the plugin is enabled
├── LICENSE
└── CHANGELOG.md
```

**Hard rule:** only `plugin.json` goes inside `.claude-plugin/`. Every component directory (`skills/`, `commands/`, `agents/`, `hooks/`, …) sits at the **plugin root**, never inside `.claude-plugin/`.

## plugin.json schema

Required: `name` (kebab-case, must match the directory name). Everything else is optional but `description` and `version` are strongly recommended.

```json
{
  "name": "plugin-name",
  "displayName": "Human Readable Name",
  "version": "1.2.0",
  "description": "One-line description shown in /plugin listings",
  "author": { "name": "raygooo", "email": "lovzoe@hotmail.com" },
  "homepage": "https://github.com/Raygooo/ray_skills",
  "repository": "https://github.com/Raygooo/ray_skills",
  "license": "MIT",
  "keywords": ["..."],
  "defaultEnabled": true,

  "skills": "./skills/",            // optional: extra skill paths (ADDS to default)
  "commands": ["./commands/"],      // optional: command paths (REPLACES default)
  "agents": ["./agents/"],          // optional: agent paths (REPLACES default)
  "hooks": "./hooks/hooks.json",    // optional: path OR inline object
  "mcpServers": "./.mcp.json",      // optional: path OR inline object
  "lspServers": "./.lsp.json",      // optional: path OR inline object

  "dependencies": ["other-plugin", { "name": "lib", "version": "~2.1.0" }]
}
```

You usually don't need the path fields at all — Claude Code auto-discovers `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, and `.mcp.json` by convention. Only set them to override or add non-default locations.

## Subagents — `agents/<name>.md`

Markdown file with YAML frontmatter; the body is the agent's system prompt. See `orchestration.md` for when to ship one.

```markdown
---
name: security-reviewer          # optional, defaults to filename
description: Use to audit changed code for security issues.   # REQUIRED — drives auto-invocation
tools: Bash, Read, Grep          # optional: allowlist (omit = inherit all)
disallowedTools: Write, Edit     # optional
model: sonnet                    # optional model override
effort: medium                   # optional
maxTurns: 20                     # optional
isolation: worktree              # optional; only valid value is "worktree"
---

You are a security reviewer. Focus on … (system prompt body)
```

**Security restriction:** plugin-shipped agents may NOT declare `hooks`, `mcpServers`, or `permissionMode`. Invoked as `@agent-name` / via the Task tool / auto-selected by description, and listed under `/agents`.

## Slash commands — `commands/<name>.md`

Legacy flat format. Same frontmatter as a skill, but a single Markdown file with no supporting directory. Resolves to `/<plugin>:<command>`. **For new work, write a `skills/<name>/SKILL.md` instead** — skills support bundled `references/`, `scripts/`, `assets/` and also expose a `/<plugin>:<skill>` command.

## Hooks — `hooks/hooks.json`

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/guard.sh", "timeout": 30 }
        ]
      }
    ]
  }
}
```

Common events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`, `SessionEnd` (full list in the hooks docs). Hook `type` can be `command`, `http`, `mcp_tool`, `prompt`, or `agent`. Exit code `2` = blocking error. Hooks need `/reload-plugins` or a restart to take effect.

## MCP servers — `.mcp.json`

Standard MCP server config bundled with the plugin; merged in when the plugin is enabled. Use `${CLAUDE_PLUGIN_ROOT}` for any bundled server binaries/scripts.

## Path variables (usable in plugin.json, hooks, MCP/LSP config, skill & agent bodies)

| Variable | Resolves to | Notes |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | absolute install dir of this plugin | **changes on update**; use for bundled scripts/assets |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/` | persistent; **survives updates** (caches, generated files) |
| `${CLAUDE_PROJECT_DIR}` | project root where Claude Code launched | for project-local paths |

In shell-form commands wrap in double quotes: `"${CLAUDE_PLUGIN_ROOT}/x.sh"`. In exec-form (`args` array) pass unquoted as one element.
