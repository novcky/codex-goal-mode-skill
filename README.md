# Codex Goal Mode Skill

[English](README.en.md)

一个可从 GitHub 安装的 Codex Skill，用于无人值守的长期目标工作流。

当用户明确使用 `/goal` 启动目标时，`goal-mode` 会初始化持久化的目标文件，每轮只执行一个可验证任务，记录证据与风险，并在触发停止条件时暂停，避免无人值守任务跑偏。

## 安装

在 Codex 中使用 `$skill-installer` 从 GitHub 的 `main` 分支安装最新代码：

```text
$skill-installer install https://github.com/novcky/codex-goal-mode-skill/tree/main/skills/goal-mode
```

安装后重启 Codex，让新 Skill 生效。

需要固定到某个版本或试用预发布版本时，可在 [Releases](https://github.com/novcky/codex-goal-mode-skill/releases) 中选择对应 tag。

## 更新

`$skill-installer` 不会覆盖已存在的 Skill 目录。更新前先删除旧版本：

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\skills\goal-mode"
```

macOS / Linux：

```bash
rm -rf ~/.codex/skills/goal-mode
```

然后重新运行上面的安装命令，并重启 Codex。

## 使用

```text
/goal 实现这个功能，完成验证，并持续推进直到目标完成。
```

安装后的 Skill 名称是 `goal-mode`，显式调用方式是 `$goal-mode`。

## 工作方式

- 首次 `/goal` 会在当前项目根目录创建 `goal-N/input.md`、`goal-N/plan.md` 和 `goal-N/tasks.md`。
- 兼容 Codex 将 `/goal` 转换成内部 `goal_context` 的会话形态。
- 首轮只初始化 goal 文件，最后只输出 `GOAL_INIT_DONE`；后续会话才开始执行 Task 1。
- 初始化时会记录 `Language policy: zh-CN` 或 `Language policy: en-US`；中文或中英混合目标默认中文，英文目标默认英文。
- 后续进度说明、任务记录和最终报告会沿用该语言；`GOAL_INIT_DONE`、文件路径、命令、错误输出和 commit 标记等机器文本保持原样。
- 同时会维护项目根目录的 `goal-current`，用于后续会话恢复当前活动目标。
- 后续每轮会读取这三份文件，只推进 `tasks.md` 中的一个未完成任务，并记录验证证据、剩余风险和下一步。
- 任务、checkpoint 和最终审核记录会保留短证据摘要，引用命令、提交、文件和风险，避免复制大段输出导致长期目标文件膨胀。
- 在 Windows/WSL 证据采集时优先使用 `pwsh -NoProfile` 或 `powershell -NoProfile`；遇到 shell profile 噪音时先用 no-profile 或 non-login shell 复核。
- 如果当前项目是 git 仓库且某个 task 修改了代码，验证通过并更新 `tasks.md` 后会创建一次 task 边界提交。
- 如果仓库 hook 拒绝默认的 goal-mode commit 标题，会改用仓库接受的标题，并在 commit body 和 `tasks.md` 保留 `Goal-mode boundary:` 边界标记。
- 每次 task 边界提交、跳过提交或提交失败记录之后都会停止；checkpoint 和最终审核会在后续会话中单独执行。
- 首轮初始化文件不会单独提交；在 git 仓库中，它们会随第一个 task 边界提交进入版本库。
- 如果 checkpoint 只更新 `tasks.md`，会使用 `goal-N checkpoint after task M: complete` 创建 checkpoint 跟踪提交。
- 如果最终审核只更新 `tasks.md`，会使用 `goal-N final review: complete` 创建 final-review 跟踪提交。
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
  goal_mode_scenarios.py
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
python tests/goal_mode_scenarios.py
```

如果你在本地习惯用 `uv`，也可以运行 `uv run python tests/validate_skill.py` 和 `uv run python tests/goal_mode_scenarios.py`。

贡献前的完整校验步骤见 [贡献指南](CONTRIBUTING.md)。

## 许可证

MIT，见 [LICENSE](LICENSE)。可安装 Skill 包内也包含 [LICENSE.txt](skills/goal-mode/LICENSE.txt)。
