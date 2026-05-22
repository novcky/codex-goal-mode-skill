#!/usr/bin/env python3
"""Smoke tests for the goal-mode Codex skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
OPENAI_YAML = ROOT / "agents" / "openai.yaml"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(f"Missing {label}: {needle}")


def main() -> None:
    if not SKILL_MD.exists():
        fail("SKILL.md is missing")
    if not OPENAI_YAML.exists():
        fail("agents/openai.yaml is missing")

    skill = SKILL_MD.read_text(encoding="utf-8")
    openai_yaml = OPENAI_YAML.read_text(encoding="utf-8")

    if not skill.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")

    for residue in ("TODO", "[TODO", "Resources (optional)", "Use -mode"):
        if residue in skill or residue in openai_yaml:
            fail(f"Template or shell-expansion residue found: {residue}")

    required_skill_phrases = {
        "explicit /goal trigger": "Use only when the user explicitly includes `/goal`",
        "runtime contract section": "## Runtime Contract",
        "runtime contract task instruction": "Start `tasks.md` with the Runtime Contract block above.",
        "task closure section": "## Task Closure Protocol",
        "red flags section": "## Red Flags - STOP",
        "init sentinel": "GOAL_INIT_DONE",
        "one task rule": "Execute only the first incomplete",
        "evidence rule": "Do not claim confidence without evidence.",
    }

    for label, phrase in required_skill_phrases.items():
        require(skill, phrase, label)

    require(openai_yaml, 'default_prompt: "Use $goal-mode with /goal', "default prompt skill name")

    match = re.search(r"^description:\s+(.+)$", skill, flags=re.MULTILINE)
    if not match:
        fail("Missing frontmatter description")

    description = match.group(1)
    for phrase in ("`/goal`", "explicitly says to enter goal mode", "red flags"):
        require(description, phrase, f"description phrase {phrase}")

    print("goal-mode smoke test passed")


if __name__ == "__main__":
    main()
