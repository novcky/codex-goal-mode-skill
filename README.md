# Codex Goal Mode Skill

[English](README.en.md)

一个干净、可分发的 Codex Skill，用于无人值守的长期目标工作流。

当用户明确使用 `/goal` 启动目标时，`goal-mode` 会初始化可持久化的目标文件，每轮只执行一个可验证任务，记录证据与风险，并在出现红旗时停止，避免无人值守任务偏航。

## 安装

在 Codex 中使用 `$skill-installer` 从 GitHub 安装：

```text
Use $skill-installer to install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

安装后重启 Codex，让新 skill 生效。

## 使用

```text
/goal 实现这个功能，完成验证，并持续推进直到目标完成。
```

安装后的 skill 名称是 `goal-mode`，显式调用方式是 `$goal-mode`。

## 仓库结构

```text
skills/goal-mode/
  SKILL.md
  agents/openai.yaml
  references/goal-workflow.md
tests/
  validate_skill.py
```

`skills/goal-mode/` 是实际可安装的 skill 包。README、测试和 CI 只放在仓库级，避免污染分发包。详细流程在 `references/goal-workflow.md`。

## 验证

```bash
python tests/validate_skill.py
```

## 许可证

MIT
