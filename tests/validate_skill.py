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
SCENARIO_VALIDATE = ROOT / "tests" / "goal_mode_scenarios.py"
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
    if not SCENARIO_VALIDATE.exists():
        fail("tests/goal_mode_scenarios.py is missing")
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
    scenario_validate = SCENARIO_VALIDATE.read_text(encoding="utf-8")
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
    if len(workflow_ref.splitlines()) > 280:
        fail("references/goal-workflow.md must stay under 280 lines")
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
        "strict initialization boundary": "The initialization turn must not edit target project files, validate task work, execute Task 1, close tasks, or run final review.",
        "same-session task red flag": "you are about to execute Task 1 in the same session that created `goal-current` or `goal-N/`",
        "goal pointer": "goal-current",
        "language policy core contract": "Persist and follow a `zh-CN` or `en-US` language policy",
        "dirty worktree core contract": "Guard against pre-existing worktree changes before task, checkpoint, or final-review work.",
        "deliverable splitting core contract": "Split explicitly named deliverables into separate independently verifiable tasks during initialization.",
        "dirty worktree red flag": "`git status --short` shows user or unrelated changes",
        "automatic task-boundary commit": "Commit code changes at the task boundary when working inside a git repository",
        "tracking commit policy": "use checkpoint/final-review tracking commits for tracking-only `tasks.md` updates",
        "commit hook compatibility": "keep the goal-mode boundary marker in the commit body and `tasks.md`",
        "task boundary stop core contract": "After any task-boundary commit, task commit skip, or task commit failure, stop immediately",
        "task final review red flag": "run a checkpoint or final review in the same session that completed a task boundary",
        "deliverable merge red flag": "merge multiple explicitly named deliverables into one task",
        "task final red flag": "you are about to use `goal-N task final: Final Review`",
        "language policy red flag": "you are about to ignore the persisted `Language policy`",
        "commit hook red flag": "without a `Goal-mode boundary:` marker in the body",
        "checkpoint tracking red flag": "checkpoint tracking commit or recorded commit failure",
        "checkpoint final review red flag": "run final review in the same session that created a checkpoint tracking commit",
        "checkpoint plan edit red flag": "modify `plan.md` or implementation files during a checkpoint-only session",
        "checkpoint missing commit red flag": "`tasks.md` claims a checkpoint commit exists but `git log -1` does not show that commit",
        "final missing commit red flag": "`tasks.md` claims a final-review commit exists but `git log -1` does not show that commit",
        "durable commit status": "make its commit-status wording durable so it remains true after the commit",
        "pending commit status red flag": "commit status still saying pending, ready to commit, or to be created",
        "commit failure red flag": "task-boundary commit or a recorded commit failure",
        "safety section": "## Safety Rules",
    }
    for label, phrase in required_skill_phrases.items():
        require(skill, phrase, label)

    required_reference_phrases = {
        "runtime contract": "## Runtime Contract",
        "initialization turn": "## Initialization Turn",
        "language policy section": "## Language Policy",
        "session loop": "## Session Loop",
        "commit hook compatibility section": "## Commit Hook Compatibility",
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
        "language policy zh": "Language policy: zh-CN",
        "language policy en": "Language policy: en-US",
        "language policy persisted": "Choose one language policy per goal during initialization and keep it for the entire goal",
        "language default Chinese": "If the prompt contains Chinese characters, choose `zh-CN`.",
        "mixed language default Chinese": "If the prompt is mixed or uncertain, choose `zh-CN`.",
        "plain English default": "If the prompt is plain English, choose `en-US`.",
        "fixed machine tokens": "Keep fixed machine tokens, paths, commands, error output, git subjects, and goal-mode markers unchanged",
        "strict init runtime contract": "If this session created goal-current or goal-N files, stop with exactly GOAL_INIT_DONE.",
        "strict init no combining": "Do not combine initialization with task execution, even for tiny goals.",
        "strict init task ban": "do not edit target project files, run task validation, close tasks, perform final review, create commits, or mark the goal complete",
        "deliverable splitting": "Split explicitly named deliverables into separate tasks",
        "three deliverable checkpoint coverage": "For a goal that names three or more deliverables, create at least three implementation tasks so the Task 3 checkpoint can run.",
        "goal_context objective extraction": "write the `objective` text as the goal prompt",
        "goal_context source note": "Source: Codex goal_context",
        "commit policy": "commit code changes at the task boundary when the project is a git repository",
        "checkpoint commit policy": "Commit checkpoint-only tracking updates as `goal-N checkpoint after task M: complete` when the project is a git repository.",
        "final review commit policy": "Commit final-review-only tracking updates as `goal-N final review: complete` when the project is a git repository.",
        "task-boundary commit format": "goal-N task M: <task title>",
        "commit hook rejected literal": "If a repository hook, commitlint, or Conventional Commit rule rejects the literal subject",
        "goal mode boundary marker": "Goal-mode boundary: goal-N task M: <task title>",
        "checkpoint boundary marker": "Goal-mode boundary: goal-N checkpoint after task M: complete",
        "final boundary marker": "Goal-mode boundary: goal-N final review: complete",
        "commit body verification": "git log -1 --format=%s%n%b",
        "actual subject tasks record": "Record both the actual commit subject and the goal-mode boundary marker in `tasks.md`.",
        "task boundary stop": "After the task-boundary commit succeeds, the non-git task skip is recorded, or the commit failure is recorded, stop immediately.",
        "no checkpoint final after task": "Do not run a checkpoint or final review in the same session that completed a task boundary",
        "first task includes init files": "include the untracked initialization files from the initialization turn",
        "checkpoint commit format": "goal-N checkpoint after task M: complete",
        "durable checkpoint commit status": "write durable checkpoint commit-status text that records the actual subject and the goal-mode boundary marker",
        "checkpoint repair rule": "If a previous checkpoint is already marked complete in `tasks.md` but its tracking update is uncommitted",
        "checkpoint stop rule": "After the checkpoint tracking commit succeeds or is skipped, stop immediately; final review must wait for the next goal-mode session.",
        "checkpoint scope rule": "During a checkpoint-only session, do not edit `plan.md`, `input.md`, or implementation files.",
        "checkpoint stage only tasks": "Stage only `goal-N/tasks.md` for the checkpoint tracking commit.",
        "checkpoint commit verification": "verify `git log -1 --format=%s%n%b` shows `goal-N checkpoint after task M: complete` or the matching `Goal-mode boundary:` marker",
        "final review commit format": "goal-N final review: complete",
        "task final banned": "do not use `goal-N task final: Final Review`",
        "durable commit status runtime": "Commit-status text in tasks.md must remain true after the commit",
        "durable task commit status": "write durable commit-status text that records the actual subject and the goal-mode boundary marker",
        "durable final commit status": "write durable final-review commit-status text that records the actual subject and the goal-mode boundary marker",
        "pending commit status banned": "do not commit pending, ready-to-commit, or to-be-created wording",
        "commit skipped non-git": "Commit skipped: not a git repository",
        "commit failure handling": "If the commit fails, record the failure in `tasks.md` and stop instead of asking the user.",
        "one task rule": "Execute only one task per session.",
        "stop after task principle": "Principle: Stop after task boundary.",
        "deliverable splitting principle": "Principle: Deliverable splitting.",
        "evidence rule": "Do not claim confidence without evidence.",
        "dirty worktree runtime": "block on unrelated dirty worktree changes",
        "dirty worktree allowed leftovers": "Allowed dirty state is limited to active goal-mode tracking leftovers",
        "dirty worktree blocker": "Record a blocker in `tasks.md`, do not edit implementation files, do not stage or commit the unrelated files, and stop.",
        "powershell no profile": "Use `pwsh -NoProfile` or `powershell -NoProfile`",
        "profile startup noise": "shell profile startup noise",
        "no-profile non-login retry": "retry with a no-profile or non-login shell",
        "checkpoint repair task": "Insert the next repair task in `tasks.md`",
        "checkpoint no implementation fix": "do not fix implementation files in the checkpoint session",
        "compaction evidence digest": "Compaction evidence digest",
        "short evidence digest": "short evidence digest",
        "avoid long command output": "avoid pasting long command output",
        "compact audit digest": "compact audit digest",
        "final review post commit": "verify `git log -1 --format=%s%n%b` shows `goal-N final review: complete` or the matching `Goal-mode boundary:` marker",
        "future layout migration note": "Future directory-layout migration note",
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
        "scenario validation command": "python tests/goal_mode_scenarios.py",
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
    require(readme_zh, "goal_mode_scenarios.py", "Chinese README scenario validator script")
    require(readme_en, "goal_mode_scenarios.py", "English README scenario validator script")
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
    require(readme_zh, "预发布版本", "Chinese README prerelease wording")
    require(readme_en, "pre-release", "English README prerelease wording")
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
    require(readme_zh, "GOAL_INIT_DONE", "Chinese README strict init output")
    require(readme_en, "GOAL_INIT_DONE", "English README strict init output")
    require(readme_zh, "Language policy: zh-CN", "Chinese README zh language policy")
    require(readme_en, "Language policy: zh-CN", "English README zh language policy")
    require(readme_zh, "Language policy: en-US", "Chinese README en language policy")
    require(readme_en, "Language policy: en-US", "English README en language policy")
    require(readme_zh, "中文或中英混合目标默认中文", "Chinese README Chinese default language")
    require(readme_en, "Chinese or mixed Chinese/English goals default to Chinese", "English README Chinese default language")
    require(readme_zh, "Goal-mode boundary:", "Chinese README commit hook boundary marker")
    require(readme_en, "Goal-mode boundary:", "English README commit hook boundary marker")
    require(readme_zh, "后续会话才开始执行 Task 1", "Chinese README delayed task execution")
    require(readme_en, "later sessions start Task 1", "English README delayed task execution")
    require(readme_zh, "task 边界提交", "Chinese README task-boundary commit policy")
    require(readme_en, "task-boundary commit", "English README task-boundary commit policy")
    require(readme_zh, "checkpoint 和最终审核会在后续会话中单独执行", "Chinese README stop after task boundary")
    require(readme_en, "checkpoints and final review run in later sessions", "English README stop after task boundary")
    require(readme_zh, "首轮初始化文件不会单独提交", "Chinese README initialization commit policy")
    require(readme_en, "Initialization files are not committed on the first turn", "English README initialization commit policy")
    require(readme_zh, "goal-N final review: complete", "Chinese README final-review commit message")
    require(readme_en, "goal-N final review: complete", "English README final-review commit message")
    require(readme_zh, "goal-N checkpoint after task M: complete", "Chinese README checkpoint commit message")
    require(readme_en, "goal-N checkpoint after task M: complete", "English README checkpoint commit message")
    require(readme_zh, "短证据摘要", "Chinese README evidence digest")
    require(readme_en, "short evidence digest", "English README evidence digest")
    require(readme_zh, "no-profile 或 non-login shell", "Chinese README no-profile retry")
    require(readme_en, "no-profile or non-login shell", "English README no-profile retry")
    if "goal-N task final: Final Review" in readme_zh + readme_en:
        fail("README must not document the old task-final commit format")
    if "v0.2.0/skills/goal-mode" in readme_zh or "v0.2.0/skills/goal-mode" in readme_en:
        fail("README pinned install example must not point at v0.2.0")
    if re.search(r"tree/v[0-9]+\.[0-9]+\.[0-9]+/skills/goal-mode", readme_zh + readme_en):
        fail("README should not include a version-pinned install command; link to Releases instead")

    require(contributing, "## 中文", "contributing doc Chinese section")
    require(contributing, "## English", "contributing doc English section")
    require(contributing, "python tests/validate_skill.py", "contributing repository validator command")
    require(contributing, "python tests/install_smoke.py", "contributing install smoke command")
    require(contributing, "python tests/goal_mode_scenarios.py", "contributing scenario validator command")
    require(contributing, "python -m pip install pyyaml", "contributing pyyaml command")
    require(contributing, "python tests/official_validate.py", "contributing official validator command")
    require(contributing, "v0.4.9-rc.1", "contributing prerelease suffix example")
    require(contributing, "v0.4.9-beta.1", "contributing beta suffix example")
    require(contributing, "无后缀正式版本", "contributing stable version policy")
    require(contributing, "unsuffixed stable version", "contributing English stable version policy")
    require(official_validate, "e8acbcb5f86cef1e04b96eed7557148b719c5f6b", "official validator pinned commit")
    require(
        official_validate,
        "6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51",
        "official validator sha256",
    )
    require(official_validate, "DOWNLOAD_TIMEOUT_SECONDS = 20", "official validator download timeout")
    require(official_validate, "RUN_TIMEOUT_SECONDS = 30", "official validator run timeout")
    require(workflow, "python tests/official_validate.py", "workflow official validator wrapper")
    require(workflow, "python tests/goal_mode_scenarios.py", "workflow scenario validator")
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

    require(scenario_validate, "class GoalModePolicy", "scenario validator policy model")
    require(scenario_validate, "expected_action", "scenario validator expected action assertion")
    require(scenario_validate, "expected_must_stop", "scenario validator expected stop assertion")
    require(scenario_validate, "expected_forbidden_next", "scenario validator forbidden next assertion")
    require(scenario_validate, "mark_goal_complete_and_stop", "scenario validator terminal final review action")
    require(scenario_validate, "goal_context initialization stops before Task 1", "scenario validator initialization case")
    require(scenario_validate, "compaction requires full goal-file reread", "scenario validator compaction case")
    require(scenario_validate, "task boundary commit stops before checkpoint", "scenario validator task boundary case")
    require(scenario_validate, "checkpoint tracking commit stops before final review", "scenario validator checkpoint case")
    require(scenario_validate, "final review requires verified tracking commit before completion", "scenario validator final review case")
    require(scenario_validate, "final review blocks completion when tracking commit is missing", "scenario validator missing tracking commit case")
    require(scenario_validate, "final review blocks completion when verification is missing", "scenario validator blocked final review case")
    require(scenario_validate, "final review blocks completion when high-risk issue remains", "scenario validator high-risk final review case")

    disallowed_skill_files = {"README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md", "CHANGELOG.md"}
    for path in SKILL_DIR.rglob("*"):
        if path.is_file() and path.name in disallowed_skill_files:
            fail(f"extraneous documentation inside skill package: {path.relative_to(SKILL_DIR)}")

    print("goal-mode skill validation passed")


if __name__ == "__main__":
    main()
