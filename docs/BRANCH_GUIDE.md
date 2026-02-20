# Codex 分支工作指南（`codex-migration`）

## 分支定位

- 本分支只承载 Codex 特化改造（安装器、编排流程、hooks、文档适配）。
- 上游新版本必须先落到基线分支（`master` / `claude`），再同步到本分支。
- 目标是“长期可重放合并”，避免一次性大改导致后续升级失控。

## 远程约定

- `upstream`：官方仓库（只拉取，不推送）
- `origin`：个人 fork（日常推送目标）
- `master`：纯上游基线分支
- `codex-migration`：Codex 特化分支

## 安全同步流程（每次升级都按此顺序）

1. 基线分支先同步上游：
   - `git fetch upstream --tags`
   - `git checkout master`
   - `git rebase upstream/master`
   - `git push origin master`
2. 特化分支吸收基线：
   - `git checkout codex-migration`
   - `git rebase master`
3. 冲突处理原则：
   - 默认先保留上游实现，再最小化叠加 Codex 逻辑。
   - 能删的旧特化补丁优先删（基线已覆盖的残留改动）。
4. 完成验证后再推送：
   - `git push origin codex-migration`

## 变更边界（防止污染）

- 不把实验性功能直接混入本分支；先在临时分支验证再回收。
- 避免“纯格式化”大改，降低下次 rebase 冲突概率。
- 涉及关键路径（`install.py`, `skills/do/**`, `hooks/**`, `codeagent-wrapper/**`）时，提交需附验证命令。

## 提交前最低验证

- `go test ./...`（在 `codeagent-wrapper/` 目录）
- `python3 install.py --status`
- 若改动安装流程：做一次隔离目录 E2E（install -> status -> update -> uninstall）

## 发布与回滚

- 本地构建建议使用 `vX.Y.Z-codex-local` 后缀，避免和官方 release 混淆。
- 覆盖 `~/.codex/bin/codeagent-wrapper` 前先备份为 `.bak-*`。
- 回滚优先 `git revert`；二进制异常时直接恢复最近 `.bak-*`。
