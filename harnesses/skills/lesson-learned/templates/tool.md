# 工具 / 工作流类经验模板

## 适用场景

学到了新工具用法、命令技巧、快捷键、CLI 操作、工作流优化、效率提升技巧。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: tool
date: {YYYY-MM-DD}
source: {session-auto | manual | git:{commit_hash}}
tags: [{工具名}, {功能域}, {平台}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [TOOL] {简短标题}

## Context（背景）

{在使用什么工具做什么任务时发现的？}

## Content

### Tool（工具）

{工具/命令/功能的名称和版本}

### Learned Feature（学到的新功能）

{发现了什么之前不知道的能力？}

### Key Commands（关键命令/操作）

{最常用的命令、参数、快捷键}

### Gotchas（踩坑点）

{使用时容易出错的地方？常见的误区？}

## Takeaway（一句话总结）

{这个工具的这个能力最适合用在什么场景？}
```

## 示例

```markdown
---
id: L-20260502-003
type: tool
date: 2026-05-02
source: session-auto
tags: [git, interactive-rebase, commit-management]
duplicate_of: null
status: active
---

# [TOOL] Git Interactive Rebase 压缩 commit

## Context（背景）

整理 feature branch 时需要将多个 WIP commit 合并为干净的提交。

## Content

### Tool（工具）

Git Interactive Rebase (git rebase -i)

### Learned Feature（学到的新功能）

rebase -i 可以交互式地合并、重排、编辑历史提交，而不改变代码内容。

### Key Commands（关键命令/操作）

```bash
git rebase -i HEAD~3        # 最近 3 个 commit 进入交互模式
git rebase -i main          # 从 main 分叉以来的所有 commit
# 交互界面中：
pick  = 保留此 commit
squash = 合并到上一个 commit（保留消息）
fixup  = 合并到上一个 commit（丢弃消息）
reword = 只修改 commit message
```

### Gotchas（踩坑点）

- 绝不要对已经 push 到公共分支的 commit 做 rebase
- rebase 过程中遇到冲突需要手动解决后 git rebase --continue
- abort 用 git rebase --abort 回退到 rebase 前的状态

## Takeaway（一句话总结）

本地分支整理 commit 用 git rebase -i，但永远不要 rebase 已 push 的公共分支。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 tool 类型：
- 学到了一个新的命令/参数/快捷键
- 发现了工具的某个隐藏功能
- 找到了更高效的操作方式
- 记录了某个工具的正确使用步骤
- 用户分享了一个实用技巧
