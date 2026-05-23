# Contributing / 贡献

## 中文

- `skills/goal-mode/` 只能保留 `SKILL.md`、`agents/openai.yaml`、`references/goal-workflow.md`、`LICENSE.txt`。
- 不要把 README、CHANGELOG、安装指南放进 skill 包。
- 改动 README、CI 或 release notes 时，保持中英双语。
- 复杂行为变更先发布为带后缀的 GitHub pre-release，例如 `v0.4.9-rc.1` 或 `v0.4.9-beta.1`；完整实机验证通过后，再创建无后缀正式版本，例如 `v0.4.9`，并标记为 Latest。

提交前运行完整校验：

```bash
python tests/validate_skill.py
python tests/install_smoke.py
python tests/goal_mode_scenarios.py
python -m pip install pyyaml
python tests/official_validate.py
```

## English

- Keep `skills/goal-mode/` limited to `SKILL.md`, `agents/openai.yaml`, `references/goal-workflow.md`, and `LICENSE.txt`.
- Do not add README, CHANGELOG, or installation guides to the installable skill package.
- Keep README, CI, and release notes bilingual.
- Publish complex behavior changes as suffixed GitHub pre-releases first, such as `v0.4.9-rc.1` or `v0.4.9-beta.1`; after full real-machine validation passes, create the unsuffixed stable version, such as `v0.4.9`, and mark it as Latest.

Run the full validation flow before submitting:

```bash
python tests/validate_skill.py
python tests/install_smoke.py
python tests/goal_mode_scenarios.py
python -m pip install pyyaml
python tests/official_validate.py
```
