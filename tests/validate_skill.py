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
SKILL_LICENSE = SKILL_DIR / "LICENSE.txt"
README_ZH = ROOT / "README.md"
README_EN = ROOT / "README.en.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
SECURITY = ROOT / "SECURITY.md"
OFFICIAL_VALIDATE = ROOT / "tests" / "official_validate.py"
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


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
    if not SKILL_LICENSE.exists():
        fail("skills/goal-mode/LICENSE.txt is missing")
    if not README_ZH.exists():
        fail("README.md is missing")
    if not README_EN.exists():
        fail("README.en.md is missing")
    if not CONTRIBUTING.exists():
        fail("CONTRIBUTING.md is missing")
    if not SECURITY.exists():
        fail("SECURITY.md is missing")
    if not OFFICIAL_VALIDATE.exists():
        fail("tests/official_validate.py is missing")
    if not WORKFLOW.exists():
        fail(".github/workflows/validate.yml is missing")
    expected_files = {
        Path("SKILL.md"),
        Path("agents/openai.yaml"),
        Path("references/goal-workflow.md"),
        Path("LICENSE.txt"),
    }
    actual_files = {path.relative_to(SKILL_DIR) for path in SKILL_DIR.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        unexpected = ", ".join(str(path) for path in sorted(actual_files - expected_files))
        missing = ", ".join(str(path) for path in sorted(expected_files - actual_files))
        fail(f"skill package file set mismatch; unexpected: {unexpected or 'none'}; missing: {missing or 'none'}")

    skill = SKILL_MD.read_text(encoding="utf-8")
    openai_yaml = OPENAI_YAML.read_text(encoding="utf-8")
    workflow_ref = WORKFLOW_REF.read_text(encoding="utf-8")
    skill_license = SKILL_LICENSE.read_text(encoding="utf-8")
    readme_zh = README_ZH.read_text(encoding="utf-8")
    readme_en = README_EN.read_text(encoding="utf-8")
    contributing = CONTRIBUTING.read_text(encoding="utf-8")
    security = SECURITY.read_text(encoding="utf-8")
    official_validate = OFFICIAL_VALIDATE.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")
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
    if len(workflow_ref.splitlines()) > 260:
        fail("references/goal-workflow.md must stay under 260 lines")
    if "MIT License" not in skill_license:
        fail("skills/goal-mode/LICENSE.txt must contain the MIT License text")

    for residue in ("TODO", "[TODO", "Resources (optional)", "Use -mode"):
        if residue in skill or residue in openai_yaml:
            fail(f"Template or shell-expansion residue found: {residue}")

    required_skill_phrases = {
        "description starts with Codex goal handler": "description: Handler for Codex goal mode.",
        "explicit /goal trigger": "Use this skill only when the user explicitly includes `/goal`",
        "goal_context metadata trigger": "contains a `goal_context` block generated by Codex from a `/goal` command",
        "goal_context guard": "current user message is a Codex `goal_context` continuation generated from a `/goal` command",
        "required load section": "## Required Load",
        "workflow reference path": "references/goal-workflow.md",
        "core contract section": "## Core Contract",
        "red flags section": "## Red Flags - STOP",
        "init sentinel": "GOAL_INIT_DONE",
        "goal pointer": "goal-current",
        "commit control": "Do not create git commits unless the user's goal explicitly asks for commits.",
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
        "goal pointer": "goal-current",
        "goal active status": "Goal status: active",
        "goal complete status": "Goal status: complete",
        "goal_context objective extraction": "write the `objective` text as the goal prompt",
        "goal_context source note": "Source: Codex goal_context",
        "commit policy": "Commit policy",
        "commit control": "Do not create git commits unless the original goal explicitly requested commits.",
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
        "installer command": "$skill-installer install",
        "explicit trigger": "/goal",
        "explicit skill invocation": "$goal-mode",
        "validation command": "python tests/validate_skill.py",
        "releases link": "https://github.com/novcky/codex-goal-mode-skill/releases",
        "issues link": "https://github.com/novcky/codex-goal-mode-skill/issues",
        "repository license link": "[LICENSE](LICENSE)",
        "skill package license link": "[LICENSE.txt](skills/goal-mode/LICENSE.txt)",
    }
    for label, phrase in readme_requirements.items():
        require(readme_zh, phrase, f"Chinese README {label}")
        require(readme_en, phrase, f"English README {label}")
    require(readme_zh, "[English](README.en.md)", "Chinese README language link")
    require(readme_en, "[中文](README.md)", "English README language link")
    require(readme_zh, "references/goal-workflow.md", "Chinese README repository structure")
    require(readme_en, "references/goal-workflow.md", "English README repository structure")
    require(readme_zh, "official_validate.py", "Chinese README official validator script")
    require(readme_en, "official_validate.py", "English README official validator script")
    require(readme_zh, "CONTRIBUTING.md", "Chinese README contributing link")
    require(readme_en, "CONTRIBUTING.md", "English README contributing link")
    require(readme_zh, "SECURITY.md", "Chinese README security link")
    require(readme_en, "SECURITY.md", "English README security link")
    require(readme_zh, "## 快速自检", "Chinese README quick check heading")
    require(readme_en, "## Quick Check", "English README quick check heading")
    require(readme_zh, "## 更新", "Chinese README update heading")
    require(readme_en, "## Update", "English README update heading")
    require(readme_zh, "不会覆盖已存在的 Skill 目录", "Chinese README installer overwrite note")
    require(readme_en, "does not overwrite an existing skill directory", "English README installer overwrite note")
    require(readme_zh, "重新运行上面的安装命令", "Chinese README update reinstall wording")
    require(readme_en, "run the install command above again", "English README update reinstall wording")
    require(readme_zh, 'Remove-Item -Recurse -Force "$env:USERPROFILE\\.codex\\skills\\goal-mode"', "Chinese README Windows update remove command")
    require(readme_en, 'Remove-Item -Recurse -Force "$env:USERPROFILE\\.codex\\skills\\goal-mode"', "English README Windows update remove command")
    require(readme_zh, "rm -rf ~/.codex/skills/goal-mode", "Chinese README Unix update remove command")
    require(readme_en, "rm -rf ~/.codex/skills/goal-mode", "English README Unix update remove command")
    require(readme_zh, "重启 Codex", "Chinese README update restart note")
    require(readme_en, "restart Codex", "English README update restart note")
    require(readme_zh, "完整校验步骤见", "Chinese README full validation link")
    require(readme_en, "full pre-contribution validation flow", "English README full validation link")
    require(readme_zh, "goal-N/input.md", "Chinese README goal file side effect")
    require(readme_en, "goal-N/input.md", "English README goal file side effect")
    require(readme_zh, "goal-N/plan.md", "Chinese README plan file side effect")
    require(readme_en, "goal-N/plan.md", "English README plan file side effect")
    require(readme_zh, "goal-N/tasks.md", "Chinese README tasks file side effect")
    require(readme_en, "goal-N/tasks.md", "English README tasks file side effect")
    require(readme_zh, "goal-current", "Chinese README active goal pointer")
    require(readme_en, "goal-current", "English README active goal pointer")
    require(readme_zh, "goal_context", "Chinese README internal goal context note")
    require(readme_en, "goal_context", "English README internal goal context note")
    require(readme_zh, "git commit", "Chinese README commit policy")
    require(readme_en, "git commits", "English README commit policy")
    if "v0.2.0/skills/goal-mode" in readme_zh or "v0.2.0/skills/goal-mode" in readme_en:
        fail("README pinned install example must not point at v0.2.0")
    if re.search(r"tree/v[0-9]+\.[0-9]+\.[0-9]+/skills/goal-mode", readme_zh + readme_en):
        fail("README should not include a version-pinned install command; link to Releases instead")

    require(contributing, "## 中文", "contributing doc Chinese section")
    require(contributing, "## English", "contributing doc English section")
    require(contributing, "python tests/validate_skill.py", "contributing repository validator command")
    require(contributing, "python tests/install_smoke.py", "contributing install smoke command")
    require(contributing, "python -m pip install pyyaml", "contributing pyyaml command")
    require(contributing, "python tests/official_validate.py", "contributing official validator command")
    require(official_validate, "e8acbcb5f86cef1e04b96eed7557148b719c5f6b", "official validator pinned commit")
    require(
        official_validate,
        "6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51",
        "official validator sha256",
    )
    require(official_validate, "DOWNLOAD_TIMEOUT_SECONDS = 20", "official validator download timeout")
    require(official_validate, "RUN_TIMEOUT_SECONDS = 30", "official validator run timeout")
    require(workflow, "python tests/official_validate.py", "workflow official validator wrapper")
    require(workflow, "actions/checkout@v6", "workflow checkout action")
    require(workflow, "actions/setup-python@v6", "workflow setup-python action")
    if "curl -fsSL" in contributing or "/tmp/quick_validate.py" in contributing:
        fail("CONTRIBUTING.md should use the cross-platform official_validate.py wrapper")
    if "curl -fsSL" in workflow or "/tmp/quick_validate.py" in workflow:
        fail("CI should use the cross-platform official_validate.py wrapper")
    require(security, "## 中文", "security doc Chinese section")
    require(security, "## English", "security doc English section")
    require(
        security,
        "https://github.com/novcky/codex-goal-mode-skill/security/advisories/new",
        "security private vulnerability report link",
    )
    require(security, "https://github.com/novcky/codex-goal-mode-skill/issues", "security issue fallback link")

    disallowed_skill_files = {"README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md", "CHANGELOG.md"}
    for path in SKILL_DIR.rglob("*"):
        if path.is_file() and path.name in disallowed_skill_files:
            fail(f"extraneous documentation inside skill package: {path.relative_to(SKILL_DIR)}")

    print("goal-mode skill validation passed")


if __name__ == "__main__":
    main()
