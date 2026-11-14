# 中文翻译层（`zh` 分支）

本仓库是 [`anthropics/financial-services`](https://github.com/anthropics/financial-services) 的中文增强副本。官方内容只进 `main`，中文翻译只进 `zh`，不向上游提交 PR。

## 分支模型

| 分支 | 角色 | 规则 |
| --- | --- | --- |
| `main` | 官方 `upstream/main` 纯净镜像 | 只做 `git merge --ff-only upstream/main`，永不提交本地改动 |
| `zh` | 长期翻译分支 | 所有 `-zh` 提交；每次同步后 `git rebase main` |
| `origin/zh` | 备份 | 只推自己的 fork |

> fork 的 `main` 已改为官方镜像（2026-11-14，重写历史，与 `upstream/main` 一致），**禁止在其上提交**。旧指针保存在标签 `fork-main-backup-1415e01`，需要回滚时可用 `git push --force origin fork-main-backup-1415e01:main`。

远程约定：`origin` = 自己的 fork（可推），`upstream` = 官方仓库（`pushurl` 已设为 `no_push`）。

`zh` 分支于 2026-11-14 从纯净 `main` 重建（旧历史保留在标签 `zh-archive-20261114`），重建后的提交粒度为**一个插件一个提交**，单个技能的补译/修订单独提交。

## 放置规则

翻译目录 `<skill>-zh/` 与英文技能目录同处一层，位置随上游结构：

- `plugins/vertical-plugins/<vertical>/skills/<skill>-zh/`
- `plugins/agent-plugins/<agent>/skills/<skill>-zh/`
- `plugins/partner-built/<vendor>/skills/<skill>-zh/`

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

## 现状（2026-11-14 重建后）

51 个中文技能已迁入。复核口径：章节数、条目数、代码块数与英文源逐项比对。

- **43 个技能**与英文源结构一致（条目数、代码块数 1:1），抽查语义与术语无误。
- **8 个技能曾落后于英文源**，逐个单独补译，进度如下：

| 技能 | 补译前 | 现状 |
| --- | --- | --- |
| `lbo-model-zh` | 274 / 217 行 | 已完成，274 / 256 行，条目 127:127 |
| `audit-xls-zh` | 结构已重写 | 已按新版重译，156 / 156 行 |
| `ib-check-deck-zh` | 缺环境检查等 | 已完成，标题 11:11 |
| `comps-analysis-zh` | 661 / 612 行 | 已完成，661 / 661 行，条目 178:178 |
| `3-statement-model-zh` | 408 / 368 行 | 已完成，408 / 408 行，条目 121:121 |
| `strip-profile-zh` | 385 / 266 行 | 已完成，385 / 385 行，代码块 22:22 |
| `datapack-builder-zh` | 656 / 598 行 | 已完成，656 / 656 行，代码块 8:8 |
| `dcf-model-zh` | 1264 / 772 行 | **待补译**（缺 26 节，工作量最大） |

- `competitive-analysis-zh` 比英文源更详细（条目 115 vs 56），属译文扩写，暂不精简。

## 命名映射（英文 → 中文目录）

| 上游英文技能 | 中文目录 | 备注 |
| --- | --- | --- |
| `3-statement-model` | `3-statement-model-zh` | 原 `3-statements-zh`，2026-11 对齐 |
| `audit-xls` | `audit-xls-zh` | 原 `check-model-zh`，2026-11 对齐 |
| `ib-check-deck` | `ib-check-deck-zh` | 原 `check-deck-zh`，2026-11 对齐 |
| `meeting-prep-agent/{client-report,client-review,investment-proposal}` | 同名 `-zh` | 原 `wealth-management` 插件，上游 #349 移除后并入该 agent |

frontmatter `name` 现已全部与目录名一致。

## 校验

- `python3 scripts/check.py`：官方 CI 校验。注意它要求 `plugins/agent-plugins/*/skills/*` 在 `vertical-plugins` 下有同名源，`-zh` 目录会报 `no vertical source`（预期噪声，与上游自身 `client-report` 等同类报错一致）。
- 中文侧自检标准：
  1. 目录名 == frontmatter `name`；
  2. 每个 `-zh` 目录都有同名英文技能目录；
  3. `^#{1,4} ` 章节数、`- ` 条目数、` ``` ` 代码块数与英文源一致（允许译文扩写，不允许缺失）；
  4. 正文不残留整段未翻译英文（代码块内除外）。
- 不要在翻译提交里改动 `plugin.json` 的 `version`；官方 pre-commit 钩子若已启用，用 `git commit --no-verify` 跳过。
