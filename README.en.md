# Codex Goal Mode Skill

[中文](README.md)

A GitHub-installable Codex skill for unattended long-running goal workflows.

When a user explicitly starts a goal with `/goal`, `goal-mode` initializes durable goal files, runs one verifiable task per session, records evidence and risk, and pauses on stop conditions to keep unattended work on track.

## Install

In Codex, install the latest code from the `main` branch with `$skill-installer`:

```text
$skill-installer install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

Restart Codex after installation so the new skill is loaded.

To pin a specific version, choose the corresponding tag under [Releases](https://github.com/novcky/codex-goal-mode-skill/releases).

## Update

`$skill-installer` does not overwrite an existing skill directory. Before updating, remove the old installation:

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\goal-mode"
```

macOS / Linux:

```bash
rm -rf ~/.codex/skills/goal-mode
```

Then run the install command above again and restart Codex.

## Use

```text
/goal Build the feature, validate it, and keep advancing until complete.
```

The installed skill name is `goal-mode`, and the explicit skill invocation is `$goal-mode`.

## How It Works

- The first `/goal` turn creates `goal-N/input.md`, `goal-N/plan.md`, and `goal-N/tasks.md` under the current project root.
- It handles Codex sessions where `/goal` is transformed into an internal `goal_context` message.
- It also maintains a project-root `goal-current` pointer so later sessions can resume the active goal.
- Later turns read those three files, advance only one incomplete task from `tasks.md`, and record validation evidence, remaining risk, and the next step.
- It does not create git commits by default; commits happen only when the `/goal` request explicitly asks for them.
- When a stop condition appears, task execution pauses until the workflow state is repaired or the blocker is recorded.

## Core Layout

```text
skills/goal-mode/
  SKILL.md
  agents/openai.yaml
  references/goal-workflow.md
  LICENSE.txt
tests/
  validate_skill.py
  install_smoke.py
  official_validate.py
```

`skills/goal-mode/` is the installable skill package. README files, tests, and CI stay at the repository level to keep the distributed package minimal. The detailed workflow lives in `references/goal-workflow.md`.

## Contributing and Security

- [Issues](https://github.com/novcky/codex-goal-mode-skill/issues)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Quick Check

```bash
python tests/validate_skill.py
```

If you prefer `uv`, you can also run `uv run python tests/validate_skill.py`.

For the full pre-contribution validation flow, see [Contributing](CONTRIBUTING.md).

## License

MIT; see [LICENSE](LICENSE). The installable skill package also includes [LICENSE.txt](skills/goal-mode/LICENSE.txt).
