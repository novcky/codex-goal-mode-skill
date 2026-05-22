# Codex Goal Mode Skill

[中文](README.md)

A clean, distributable Codex skill for unattended long-running goal workflows.

When a user explicitly starts a goal with `/goal`, `goal-mode` initializes durable goal files, runs one verifiable task per session, records evidence and risk, and stops on red flags to keep unattended work from drifting.

## Install

In Codex, install the latest version from GitHub with `$skill-installer`:

```text
Use $skill-installer to install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

Install the current stable release, `v0.2.0`:

```text
Use $skill-installer to install https://github.com/novcky/codex-goal-mode-skill/tree/v0.2.0/skills/goal-mode
```

Restart Codex after installation so the new skill is loaded.

Stable versions are available under [Releases](https://github.com/novcky/codex-goal-mode-skill/releases).

## Use

```text
/goal Build the feature, validate it, and keep advancing until complete.
```

The installed skill name is `goal-mode`, and the explicit skill invocation is `$goal-mode`.

## Repository Layout

```text
skills/goal-mode/
  SKILL.md
  agents/openai.yaml
  references/goal-workflow.md
tests/
  validate_skill.py
```

`skills/goal-mode/` is the installable skill package. README files, tests, and CI stay at the repository level so the distributed skill package remains clean. The detailed workflow lives in `references/goal-workflow.md`.

## Validate

```bash
uv run python tests/validate_skill.py
```

## License

MIT
