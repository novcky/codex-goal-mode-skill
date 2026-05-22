# Codex Goal Mode Skill

[English](README.en.md)

一个可从 GitHub 安装的 Codex Skill，用于无人值守的长期目标工作流。

当用户明确使用 `/goal` 启动目标时，`goal-mode` 会初始化持久化的目标文件，每轮只执行一个可验证任务，记录证据与风险，并在触发停止条件时暂停，避免无人值守任务跑偏。

## 安装

在 Codex 中使用 `$skill-installer` 从 GitHub 的 `main` 分支安装最新代码：

```text
$skill-installer install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

固定版本安装示例：

```text
$skill-installer install https://github.com/novcky/codex-goal-mode-skill/tree/v0.3.2/skills/goal-mode
```

安装后重启 Codex，让新 Skill 生效。

版本记录见 [Releases](https://github.com/novcky/codex-goal-mode-skill/releases)。

## 更新

`$skill-installer` 不会覆盖已存在的 Skill 目录。更新前先删除旧版本：

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\goal-mode"
```

macOS / Linux：

```bash
rm -rf ~/.codex/skills/goal-mode
```

然后重新运行安装命令，并重启 Codex。

## 使用

```text
/goal 实现这个功能，完成验证，并持续推进直到目标完成。
```

安装后的 Skill 名称是 `goal-mode`，显式调用方式是 `$goal-mode`。

## 工作方式

- 首次 `/goal` 会在当前项目根目录创建 `goal-N/input.md`、`goal-N/plan.md` 和 `goal-N/tasks.md`。
- 兼容 Codex 将 `/goal` 转换成内部 `goal_context` 的会话形态。
- 同时会维护项目根目录的 `goal-current`，用于后续会话恢复当前活动目标。
- 后续每轮会读取这三份文件，只推进 `tasks.md` 中的一个未完成任务，并记录验证证据、剩余风险和下一步。
- 默认不会创建 git commit；只有 `/goal` 请求明确要求提交时才会提交。
- 触发停止条件时会暂停任务执行，先修复工作流状态或记录阻塞原因。

## 核心结构

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

`skills/goal-mode/` 是实际可安装的 Skill 包。README、测试和 CI 只放在仓库级，保持分发包精简。详细流程在 `references/goal-workflow.md`。

## 贡献与安全

- [问题反馈](https://github.com/novcky/codex-goal-mode-skill/issues)
- [贡献指南](CONTRIBUTING.md)
- [安全政策](SECURITY.md)

## 快速自检

```bash
python tests/validate_skill.py
```

如果你在本地习惯用 `uv`，也可以运行 `uv run python tests/validate_skill.py`。

贡献前的完整校验步骤见 [贡献指南](CONTRIBUTING.md)。

## 许可证

MIT，见 [LICENSE](LICENSE)。可安装 Skill 包内也包含 [LICENSE.txt](skills/goal-mode/LICENSE.txt)。
