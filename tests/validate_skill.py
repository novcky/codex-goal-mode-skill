#!/usr/bin/env python3
"""Validate the distributable goal-mode skill package."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "goal-mode"
SKILL_MD = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
WORKFLOW_REF = SKILL_DIR / "references" / "goal-workflow.md"
README_ZH = ROOT / "README.md"
README_EN = ROOT / "README.en.md"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(f"Missing {label}: {needle}")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        fail("SKILL.md frontmatter is not closed")
    raw_frontmatter = parts[1]

    frontmatter: dict[str, str] = {}
    for line in raw_frontmatter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"Unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def main() -> None:
    if not SKILL_MD.exists():
        fail("skills/goal-mode/SKILL.md is missing")
    if not OPENAI_YAML.exists():
        fail("skills/goal-mode/agents/openai.yaml is missing")
    if not WORKFLOW_REF.exists():
        fail("skills/goal-mode/references/goal-workflow.md is missing")
    if not README_ZH.exists():
        fail("README.md is missing")
    if not README_EN.exists():
        fail("README.en.md is missing")
    expected_files = {
        Path("SKILL.md"),
        Path("agents/openai.yaml"),
        Path("references/goal-workflow.md"),
    }
    actual_files = {path.relative_to(SKILL_DIR) for path in SKILL_DIR.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        unexpected = ", ".join(str(path) for path in sorted(actual_files - expected_files))
        missing = ", ".join(str(path) for path in sorted(expected_files - actual_files))
        fail(f"skill package file set mismatch; unexpected: {unexpected or 'none'}; missing: {missing or 'none'}")

    skill = SKILL_MD.read_text(encoding="utf-8")
    openai_yaml = OPENAI_YAML.read_text(encoding="utf-8")
    workflow_ref = WORKFLOW_REF.read_text(encoding="utf-8")
    readme_zh = README_ZH.read_text(encoding="utf-8")
    readme_en = README_EN.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(skill)

    name = frontmatter.get("name")
    description = frontmatter.get("description", "")
    if name != "goal-mode":
        fail("frontmatter name must be goal-mode")
    if SKILL_DIR.name != name:
        fail("skill directory name must match frontmatter name")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        fail("skill name must be lowercase hyphen-case")
    if len(description) > 1024:
        fail("description must be 1024 characters or fewer")
    if "<" in description or ">" in description:
        fail("description must not contain angle brackets")
    if len(skill.splitlines()) > 120:
        fail("SKILL.md must stay thin and be at most 120 lines")
    if len(workflow_ref.splitlines()) > 240:
        fail("references/goal-workflow.md must stay under 240 lines")

    for residue in ("TODO", "[TODO", "Resources (optional)", "Use -mode"):
        if residue in skill or residue in openai_yaml:
            fail(f"Template or shell-expansion residue found: {residue}")

    required_skill_phrases = {
        "explicit /goal trigger": "Use only when the user explicitly includes `/goal`",
        "required load section": "## Required Load",
        "workflow reference path": "references/goal-workflow.md",
        "core contract section": "## Core Contract",
        "red flags section": "## Red Flags - STOP",
        "init sentinel": "GOAL_INIT_DONE",
        "safety section": "## Safety Rules",
    }
    for label, phrase in required_skill_phrases.items():
        require(skill, phrase, label)

    required_reference_phrases = {
        "runtime contract": "## Runtime Contract",
        "initialization turn": "## Initialization Turn",
        "session loop": "## Session Loop",
        "principles and checks": "## Principles and Checks",
        "check sentence": "Check:",
        "task closure protocol": "## Task Closure Protocol",
        "checkpoints": "## Checkpoints",
        "final review": "## Final Review",
        "rationalizations": "## Rationalizations to Reject",
        "aar questions": "## AAR Questions",
        "goal init sentinel": "GOAL_INIT_DONE",
        "one task rule": "Execute only one task per session.",
        "evidence rule": "Do not claim confidence without evidence.",
    }
    for label, phrase in required_reference_phrases.items():
        require(workflow_ref, phrase, label)

    require(openai_yaml, 'display_name: "Goal Mode"', "display name")
    require(openai_yaml, 'short_description: "Plan and run unattended goal tasks"', "short description")
    require(openai_yaml, 'default_prompt: "Use $goal-mode with /goal', "default prompt skill name")

    readme_requirements = {
        "install URL": "https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode",
        "stable install URL": "https://github.com/novcky/codex-goal-mode-skill/tree/v0.2.0/skills/goal-mode",
        "installer skill": "$skill-installer",
        "explicit trigger": "/goal",
        "explicit skill invocation": "$goal-mode",
        "validation command": "uv run python tests/validate_skill.py",
        "releases link": "https://github.com/novcky/codex-goal-mode-skill/releases",
    }
    for label, phrase in readme_requirements.items():
        require(readme_zh, phrase, f"Chinese README {label}")
        require(readme_en, phrase, f"English README {label}")
    require(readme_zh, "[English](README.en.md)", "Chinese README language link")
    require(readme_en, "[中文](README.md)", "English README language link")
    require(readme_zh, "references/goal-workflow.md", "Chinese README repository structure")
    require(readme_en, "references/goal-workflow.md", "English README repository structure")

    disallowed_skill_files = {"README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md", "CHANGELOG.md"}
    for path in SKILL_DIR.rglob("*"):
        if path.is_file() and path.name in disallowed_skill_files:
            fail(f"extraneous documentation inside skill package: {path.relative_to(SKILL_DIR)}")

    print("goal-mode skill validation passed")


if __name__ == "__main__":
    main()
