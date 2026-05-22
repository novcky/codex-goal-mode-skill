# Contributing / 贡献

## 中文

- `skills/goal-mode/` 只能保留 `SKILL.md`、`agents/openai.yaml`、`references/goal-workflow.md`、`LICENSE.txt`。
- 不要把 README、CHANGELOG、安装指南放进 skill 包。
- 改动 README、CI 或 release notes 时，保持中英双语。

提交前运行完整校验：

```bash
python tests/validate_skill.py
python tests/install_smoke.py
python -m pip install pyyaml
python tests/official_validate.py
```

## English

- Keep `skills/goal-mode/` limited to `SKILL.md`, `agents/openai.yaml`, `references/goal-workflow.md`, and `LICENSE.txt`.
- Do not add README, CHANGELOG, or installation guides to the installable skill package.
- Keep README, CI, and release notes bilingual.

Run the full validation flow before submitting:

```bash
python tests/validate_skill.py
python tests/install_smoke.py
python -m pip install pyyaml
python tests/official_validate.py
```
