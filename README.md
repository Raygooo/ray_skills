# Ray Skills Marketplace

A Claude Code plugin marketplace with productivity tools for macOS power users.

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add Raygooo/ray_skills
```

Then install any plugin:

```
/plugin install proxy-app-launcher@ray-skills
```

## Plugins

### proxy-app-launcher

Creates a macOS `.app` launcher that starts any Electron/desktop app (Claude, Cursor, VS Code, Obsidian, etc.) with proxy environment variables injected. Solves the problem where Electron apps ignore system proxy settings when using Clash/V2Ray in rule mode.

**Skills included:**
- `proxy-app-launcher:proxy-app-launcher` — auto-triggered when you mention proxy issues with Electron apps

**Trigger phrases:**
- "Electron app doesn't use proxy"
- "app ignores system proxy"
- "Clash rule mode not working for app"
- "create proxy launcher"

### marketplace-contributor

Meta-plugin for growing this marketplace itself. Teaches agents how to capture a workflow as a reusable skill, scaffold a new plugin around it, apply progressive disclosure across `SKILL.md` / `references/` / `scripts/` / `assets/`, and register the plugin locally.

**Skills included:**
- `marketplace-contributor:contribute-skill` — auto-triggered when you want to save a workflow as a skill or add a new plugin to this marketplace

**Trigger phrases:**
- "save this as a skill"
- "turn this workflow into a skill"
- "add a skill to the marketplace"
- "create a new plugin for this"
- "contribute to my marketplace"
