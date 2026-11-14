# 中文翻译层（`zh` 分支）

本仓库是 [`anthropics/financial-services`](https://github.com/anthropics/financial-services) 的中文增强副本。官方内容只进 `main`，中文翻译只进 `zh`，不向上游提交 PR。

## 分支模型

| 分支 | 角色 | 规则 |
| --- | --- | --- |
| `main` | 官方 `upstream/main` 纯净镜像 | 只做 `git merge --ff-only upstream/main`，永不提交本地改动 |
| `zh` | 长期翻译分支 | 所有 `-zh` 提交；每次同步后 `git rebase main` |
| `origin/zh` | 备份 | 只推自己的 fork |

远程约定：`origin` = 自己的 fork（可推），`upstream` = 官方仓库（`pushurl` 已设为 `no_push`）。

## 放置规则

翻译目录 `<skill>-zh/` 与英文技能目录同处一层，位置随上游结构：

- `plugins/vertical-plugins/<vertical>/skills/<skill>-zh/`
- `plugins/agent-plugins/<agent>/skills/<skill>-zh/`
- `plugins/partner-built/<vendor>/skills/<skill>-zh/`

新增/调整翻译时同步更新本文件的“命名映射”表。

## 同步流程

```bash
git fetch upstream
git switch main && git merge --ff-only upstream/main
git switch zh   && git rebase main
git tag zh-sync-$(git rev-parse --short upstream/main)
git push --force-with-lease origin zh    # rebase 改写了历史，备份分支需要 force-with-lease
```

- 冲突通常只出现在上游重命名/移动/删除技能目录时，按下面的映射表处理。
- `git log --oneline main..zh` 可查看翻译层相对官方的全部提交。

## 同步基线

- 最近一次翻译基线：`zh-sync-3e32c22`（上游 `main@3e32c22`，2026-11-14 同步）
- 历史上还保留了 `zh-sync-1415e01`（翻译层初次对齐时的基线）

## 命名映射（英文 → 中文目录）

上游技能重命名后，翻译目录需一并改名，并同步 frontmatter `name`：

| 上游英文技能 | 中文目录 | 备注 |
| --- | --- | --- |
| `3-statement-model` | `3-statement-model-zh` | 原 `3-statements-zh`，2026-11 对齐 |
| `audit-xls` | `audit-xls-zh` | 原 `check-model-zh`，2026-11 对齐 |
| `ib-check-deck` | `ib-check-deck-zh` | 原 `check-deck-zh`，2026-11 对齐 |
| `meeting-prep-agent/{client-report,client-review,investment-proposal}` | 同名 `-zh` | 原 `wealth-management` 插件，上游 #349 移除后并入该 agent |
| `comps-analysis` | `comps-analysis-zh` | frontmatter `name` 仍为 `fsi-comps-analysis-zh` |
| `strip-profile` | `strip-profile-zh` | frontmatter `name` 仍为 `fsi-strip-profile-zh` |
| `earnings-preview-beta` | `earnings-preview-beta-zh` | frontmatter `name` 仍为 `earnings-preview-single-zh` |

## 校验

- `python3 scripts/check.py`：官方 CI 校验。注意它要求 `plugins/agent-plugins/*/skills/*` 在 `vertical-plugins` 下有同名源，`-zh` 目录会报 `no vertical source`（预期噪声，与上游自身 `client-report` 等同类报错一致）。
- 中文侧自检标准：目录名与 frontmatter `name` 一致；每个 `-zh` 目录都有同名英文技能目录。
- 不要在翻译提交里改动 `plugin.json` 的 `version`；官方 pre-commit 钩子若已启用，用 `git commit --no-verify` 跳过。
