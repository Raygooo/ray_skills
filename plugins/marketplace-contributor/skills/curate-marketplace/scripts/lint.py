#!/usr/bin/env python3
"""Lint the ray-skills marketplace for rot.

Borrowed from the lint pass in Karpathy's LLM Wiki pattern: instead of letting a
knowledge base accumulate contradictions, stale claims, and orphan pages, run a
maintenance pass that surfaces them. Here the "pages" are plugins/skills.

Deterministic, stdlib-only. Reports issues grouped by severity and exits non-zero
if any ERRORs are found (CI-friendly). Semantic checks (weak descriptions, stale
feature references) are left to the agent — see SKILL.md.

Usage:
    python3 lint.py [MARKETPLACE_ROOT]   # defaults to auto-detected repo root
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ERRORS: list[str] = []
WARNINGS: list[str] = []
INFO: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def info(msg: str) -> None:
    INFO.append(msg)


def find_root(start: Path) -> Path | None:
    """Walk up until we find .claude-plugin/marketplace.json."""
    cur = start.resolve()
    for cand in [cur, *cur.parents]:
        if (cand / ".claude-plugin" / "marketplace.json").is_file():
            return cand
    return None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"missing JSON file: {path}")
    except json.JSONDecodeError as e:
        err(f"invalid JSON in {path}: {e}")
    return None


def parse_frontmatter(md_text: str) -> dict | None:
    """Very small YAML-ish frontmatter parser: top-level key: value only.

    Good enough to check presence of `name` and `description`. Block scalars
    (description: |) are detected as present.
    """
    if not md_text.startswith("---"):
        return None
    end = md_text.find("\n---", 3)
    if end == -1:
        return None
    block = md_text[3:end]
    fm: dict[str, str] = {}
    cur_key = None
    for line in block.splitlines():
        if re.match(r"^[A-Za-z0-9_-]+\s*:", line):
            key, _, val = line.partition(":")
            cur_key = key.strip()
            fm[cur_key] = val.strip()
        elif cur_key and line.strip():
            # continuation of a block scalar / folded value
            fm[cur_key] = (fm.get(cur_key, "") + " " + line.strip()).strip()
    return fm


# Patterns that look like a concrete trigger ("...", 'turn this into') in a description.
TRIGGER_HINT = re.compile(r'"[^"]+"|trigger when|use (this|when)|when the user', re.I)
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def lint(root: Path) -> None:
    mkt_path = root / ".claude-plugin" / "marketplace.json"
    mkt = load_json(mkt_path)
    registered: dict[str, str] = {}
    if mkt:
        for entry in mkt.get("plugins", []):
            name = entry.get("name", "<unnamed>")
            src = entry.get("source", "")
            registered[name] = src
            # dangling: registered but the source dir / manifest is missing
            src_dir = (root / src).resolve() if src else None
            if src_dir and not (src_dir / ".claude-plugin" / "plugin.json").is_file():
                err(f"marketplace.json registers '{name}' -> {src} but {src}/.claude-plugin/plugin.json is missing (dangling entry)")

    plugins_dir = root / "plugins"
    on_disk: set[str] = set()
    if plugins_dir.is_dir():
        for pdir in sorted(p for p in plugins_dir.iterdir() if p.is_dir()):
            manifest = pdir / ".claude-plugin" / "plugin.json"
            if not manifest.is_file():
                warn(f"plugin folder '{pdir.name}' has no .claude-plugin/plugin.json (skipped — WIP?)")
                continue
            pj = load_json(manifest)
            if not pj:
                continue
            pname = pj.get("name", "")
            on_disk.add(pname or pdir.name)
            # name drift: dir vs plugin.json name
            if pname != pdir.name:
                err(f"name drift: folder 'plugins/{pdir.name}' != plugin.json name '{pname}'")
            # registration: present on disk but not in marketplace.json
            if pname and pname not in registered:
                err(f"plugin '{pname}' exists on disk but is NOT registered in marketplace.json")
            lint_plugin(root, pdir, pj)

    # registered but no folder at all
    for name, src in registered.items():
        if name not in on_disk and not (root / src / ".claude-plugin" / "plugin.json").is_file():
            # already reported as dangling above if source missing; this catches name mismatch
            pass


def lint_plugin(root: Path, pdir: Path, pj: dict) -> None:
    if not pj.get("description"):
        warn(f"plugin '{pdir.name}': plugin.json has no description")
    if not pj.get("version"):
        warn(f"plugin '{pdir.name}': plugin.json has no version")

    skills_dir = pdir / "skills"
    if not skills_dir.is_dir():
        info(f"plugin '{pdir.name}': no skills/ directory")
        return
    for sdir in sorted(s for s in skills_dir.iterdir() if s.is_dir()):
        skill_md = sdir / "SKILL.md"
        rel = f"plugins/{pdir.name}/skills/{sdir.name}"
        if not skill_md.is_file():
            err(f"{rel}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            err(f"{rel}/SKILL.md: missing or malformed YAML frontmatter")
            continue
        if not fm.get("name"):
            warn(f"{rel}/SKILL.md: frontmatter has no `name`")
        desc = fm.get("description", "")
        if not desc:
            err(f"{rel}/SKILL.md: frontmatter has no `description` (skill will never trigger)")
        elif len(desc) < 40 or not TRIGGER_HINT.search(desc):
            warn(f"{rel}/SKILL.md: description looks weak (too short or no concrete trigger phrasing)")
        if len(desc) > 1536:
            warn(f"{rel}/SKILL.md: description exceeds ~1536 char trigger budget ({len(desc)} chars)")

        # oversize SKILL.md
        n_lines = text.count("\n") + 1
        if n_lines > 500:
            warn(f"{rel}/SKILL.md: {n_lines} lines (>500 — split into references/)")
        elif n_lines > 300:
            info(f"{rel}/SKILL.md: {n_lines} lines (>300 — consider splitting into references/)")

        # broken links to BUNDLED content (references/ scripts/ assets/). Links to
        # repo-root files are illustrative pointers, not bundled content — skip them.
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("#")[0].strip()
            norm = target[2:] if target.startswith("./") else target
            if not norm.startswith(("references/", "scripts/", "assets/")):
                continue
            resolved = (sdir / norm).resolve()
            if not resolved.exists():
                err(f"{rel}/SKILL.md: broken link to bundled file '{target}' (not found)")

        # orphan reference files: present under references/ but never mentioned in
        # SKILL.md at all (by relative path OR basename — robust to link style).
        refs = sdir / "references"
        if refs.is_dir():
            for f in refs.rglob("*"):
                if not f.is_file():
                    continue
                relname = f.relative_to(sdir).as_posix()
                if relname not in text and f.name not in text:
                    warn(f"{rel}: orphan reference file '{f.relative_to(sdir)}' never mentioned in SKILL.md")


def report() -> int:
    def block(title: str, items: list[str], symbol: str) -> None:
        if items:
            print(f"\n{symbol} {title} ({len(items)})")
            for it in items:
                print(f"  - {it}")

    block("ERRORS", ERRORS, "✘")
    block("WARNINGS", WARNINGS, "▲")
    block("INFO", INFO, "ℹ")
    total = len(ERRORS) + len(WARNINGS)
    print(f"\n{'✔ clean' if total == 0 else f'{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)'}")
    return 1 if ERRORS else 0


def main() -> int:
    start = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    root = find_root(start)
    if root is None:
        print(f"✘ could not find .claude-plugin/marketplace.json above {start}", file=sys.stderr)
        return 2
    print(f"Linting marketplace at: {root}")
    lint(root)
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
