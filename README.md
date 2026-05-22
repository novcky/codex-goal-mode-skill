# Codex Goal Mode Skill

A clean, distributable Codex skill for unattended long-running goal workflows.

Use `goal-mode` when a user explicitly starts a goal with `/goal`. The skill initializes durable goal files, runs one verifiable task per session, records evidence and risk, and stops on red flags instead of drifting through unattended work.

## Install

In Codex, install from GitHub with:

```text
Use $skill-installer to install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

Restart Codex after installation so the new skill is loaded.

## Use

```text
/goal Build the feature, validate it, and keep advancing until complete.
```

The installed skill name is `goal-mode`, and the explicit skill invocation is `$goal-mode`.

## Validate

```bash
python tests/validate_skill.py
```
