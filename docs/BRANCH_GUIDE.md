# Claude 基线分支工作指南（`master`）

## 分支定位

- 本分支是上游官方版本的本地对照基线，不承载 Codex 特化逻辑。
- 任何 Codex 改造都应进入 `codex-migration`，不要反向写回本分支。
- 目标是始终保持“干净、可追踪、可快速对比上游”。

## 日常维护流程

1. 拉取上游并同步标签：
   - `git fetch upstream --tags`
2. 更新基线分支：
   - `git checkout master`
   - `git rebase upstream/master`
3. 快速自检：
   - `git status`
   - `git log --oneline -1`
4. 推送到 fork：
   - `git push origin master`

## 与 Codex 分支协作

- 升级节奏固定为：`master` 先更新 -> `codex-migration` 再 `rebase master`。
- 如果上游已覆盖某些历史特化补丁，应在 `codex-migration` 清理残留，而不是改动本分支。
- 本分支只负责“提供稳定基线”，不承担编排策略迭代。

## 禁止事项

- 禁止在本分支提交 Codex 专属改造（如安装器策略、特化 hooks、定制流程脚本）。
- 禁止从 `codex-migration` 反向 merge 到 `master`。
- 禁止无目的的大规模格式化改动，避免干扰上游 diff 对照。

## 每次发布前建议记录

- 当前上游标签：`git describe --tags --always`
- 当前提交指纹：`git rev-parse --short HEAD`
- 与上游差异：`git rev-list --left-right --count master...upstream/master`
