---
name: proxy-app-launcher
description: |
  Create a macOS .app launcher that starts any Electron/desktop app with proxy environment variables injected, so the app works with Clash/V2Ray in rule mode without TUN.
  Use this skill whenever the user wants to: make a desktop app (Claude, Cursor, VS Code, Obsidian, etc.) go through a proxy; create a Dock shortcut that auto-sets http_proxy/https_proxy/all_proxy; fix 403 errors caused by Electron apps not respecting system proxy; avoid needing TUN mode for specific apps; or wrap any macOS app with custom environment variables.
  Also trigger when the user mentions: "Electron app doesn't use proxy", "app ignores system proxy", "Clash rule mode not working for app", "create proxy launcher", or "open --env".
---

# Proxy App Launcher for macOS

This skill creates a standalone `.app` bundle in `/Applications` that launches a target app with proxy environment variables. This solves the common problem where Electron apps (Claude, Cursor, VS Code, etc.) ignore macOS system proxy settings, causing connection failures or 403 errors when using Clash/V2Ray in rule mode.

## Why this exists

macOS Electron apps use Chromium's network stack, which doesn't always respect the system HTTP proxy configured by tools like Clash. The `open -a <App> --env KEY=VALUE` trick injects environment variables directly into the app process, but users can't use this from the Dock. This skill wraps that trick into a proper `.app` bundle with a custom icon so it's indistinguishable from a native app in the Dock/Launchpad.

## Workflow

### Step 1: Gather info from the user

Ask for (with sensible defaults):

| Parameter | Example | Default |
|---|---|---|
| Target app name | `Claude` | *(required)* |
| New app display name | `Claude Pro` | `<App> Pro` |
| Proxy address | `http://127.0.0.1:7890` | `http://127.0.0.1:7890` |
| SOCKS proxy | `socks5://127.0.0.1:7890` | `socks5://127.0.0.1:7890` |

Most users on Clash use port 7890 (mixed-port). If unsure, ask.

### Step 2: Create the .app bundle

Directory structure:
```
/Applications/<New Name>.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   └── launcher    # shell script
│   └── Resources/
│       └── app.icns    # custom icon
```

**Info.plist** — must include `LSArchitecturePriority` to prevent Rosetta prompts on Apple Silicon:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>app.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.proxy-launcher.TARGET_APP_LOWERCASE</string>
    <key>CFBundleName</key>
    <string>NEW_DISPLAY_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>NEW_DISPLAY_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSUIElement</key>
    <false/>
    <key>LSArchitecturePriority</key>
    <array>
        <string>arm64</string>
        <string>x86_64</string>
    </array>
</dict>
</plist>
```

**launcher script** (`Contents/MacOS/launcher`):

```bash
#!/usr/bin/env bash
open -a "TARGET_APP" \
  --env https_proxy=PROXY_HTTP \
  --env http_proxy=PROXY_HTTP \
  --env all_proxy=PROXY_SOCKS
```

Use `#!/usr/bin/env bash` (not `#!/bin/bash`) — this avoids architecture detection issues on Apple Silicon that cause Rosetta prompts.

After writing, `chmod +x` the launcher script.

### Step 3: Generate the custom icon

The icon helps users distinguish the proxy version from the original in the Dock.

Run `scripts/generate_icon.py` (bundled with this skill):

```bash
python3 -m venv /tmp/proxy-icon-venv
/tmp/proxy-icon-venv/bin/pip install Pillow
/tmp/proxy-icon-venv/bin/python3 <skill-path>/scripts/generate_icon.py \
  --source "/Applications/TARGET_APP.app/Contents/Resources/ICON_NAME.icns" \
  --output "/Applications/NEW_APP_NAME.app/Contents/Resources/app.icns"
```

To find the source icon name, read the target app's `Info.plist` and look for `CFBundleIconFile`.

The script extracts the largest PNG from the source `.icns`, adds a blue lightning badge in the bottom-right corner (representing proxy/acceleration), builds an `.iconset` with all required sizes, and converts to `.icns` via `iconutil`.

If Pillow installation fails for any reason, fall back to simply copying the original icon — the app will still work, just with the same icon.

### Step 4: Finalize

Run these commands in sequence:

```bash
# Clear quarantine attributes (prevents "app is damaged" dialogs)
xattr -cr "/Applications/NEW_APP_NAME.app"

# Re-register with LaunchServices (updates icon cache)
/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -f "/Applications/NEW_APP_NAME.app"

# Refresh the Dock to show updated icon
killall Dock
```

### Step 5: Tell the user to test

Ask the user to:
1. Find the new app in Launchpad or Spotlight
2. Open it and verify the target app launches
3. Confirm no Rosetta prompt appears
4. Check in Clash Dashboard's connection panel that traffic from the app process appears

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Rosetta prompt | Missing `LSArchitecturePriority` in plist, or shebang is `#!/bin/bash` | Add the key; use `#!/usr/bin/env bash` |
| Icon not updating | macOS icon cache | `killall Dock && killall Finder` |
| Name shows folder name, not CFBundleDisplayName | macOS prefers `.app` folder name | Rename the `.app` folder to match desired display name |
| App still gets 403 | Proxy port wrong, or Clash not running | Verify `curl --proxy http://127.0.0.1:7890 https://httpbin.org/ip` works first |
| "App is damaged" dialog | Quarantine xattr | `xattr -cr /Applications/AppName.app` |

## Cleanup

To remove a proxy launcher: `rm -rf "/Applications/NEW_APP_NAME.app"` and restart Dock.
