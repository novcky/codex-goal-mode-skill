# Contributing / 贡献

## 中文

- `skills/goal-mode/` 只能保留 `SKILL.md`、`agents/openai.yaml`、`references/goal-workflow.md`、`LICENSE.txt`。
- 不要把 README、CHANGELOG、安装指南放进 skill 包。
- 改动 README、CI 或 release notes 时，保持中英双语。
- 复杂行为变更先发布为 GitHub pre-release；完整实机验证通过后，再将同一个 release 提升为正式 Latest。

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
- Publish complex behavior changes as GitHub pre-releases first; after full real-machine validation passes, promote the same release to the stable Latest release.

Run the full validation flow before submitting:

```bash
python tests/validate_skill.py
python tests/install_smoke.py
python tests/goal_mode_scenarios.py
python -m pip install pyyaml
python tests/official_validate.py
```
