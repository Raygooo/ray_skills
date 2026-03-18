# Ray Skills

A collection of Claude Code skills for productivity and macOS power users.

## Skills

### [proxy-app-launcher](./proxy-app-launcher/)

Creates a macOS `.app` launcher that starts any Electron/desktop app (Claude, Cursor, VS Code, Obsidian, etc.) with proxy environment variables injected. Solves the problem where Electron apps ignore system proxy settings when using Clash/V2Ray in rule mode.

**Trigger phrases:**
- "Electron app doesn't use proxy"
- "app ignores system proxy"
- "Clash rule mode not working for app"
- "create proxy launcher"

## Installation

### Install all skills

```bash
git clone https://github.com/raygooo/ray_skills ~/.claude/skills/ray_skills
# Then symlink individual skills
ln -s ~/.claude/skills/ray_skills/proxy-app-launcher ~/.claude/skills/proxy-app-launcher
```

### Install a single skill

```bash
git clone https://github.com/raygooo/ray_skills /tmp/ray_skills
cp -r /tmp/ray_skills/proxy-app-launcher ~/.claude/skills/
```

## Structure

```
ray_skills/
└── proxy-app-launcher/
    ├── SKILL.md          # Skill instructions and metadata
    └── scripts/
        └── generate_icon.py  # Icon generation utility
```
