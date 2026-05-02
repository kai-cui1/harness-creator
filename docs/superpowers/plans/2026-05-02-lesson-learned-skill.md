# Lesson Learned Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个纯 markdown 的 lesson-learned skill，让 AI 从日常使用中提取经验教训，经用户逐条确认后写入存储。

**Architecture:** SKILL.md 作为主流程编排器，定义 5 步管道（扫描→提取分类→去重→逐条确认→写入索引）。6 个模板文件定义各类型经验的输出格式。运行时产生 lessons.md（完整存储）和 LESSONS.md（表格索引）。纯 markdown 实现，零代码依赖。

**Tech Stack:** Markdown (SKILL.md + 6 templates), Claude Code Skill 系统, AskUserQuestion 交互 API

---

## File Structure (All Files to Create)

```
.claude/skills/lesson-learned/
├── SKILL.md                    # 主流程编排（5 步管道 + 约束规则）
├── templates/
│   ├── bug.md                  # Bug/问题类经验模板
│   ├── pattern.md              # 模式/最佳实践模板
│   ├── tool.md                 # 工具/工作流模板
│   ├── ai-collab.md            # AI 协作经验模板
│   ├── tech-gotcha.md          # 技术陷阱模板
│   └── user-preference.md      # 主人偏好/习惯模板

.claude/lessons/
├── LESSONS.md                  # 索引文件（首次创建时初始化）
# lessons.md 在首次写入经验时自动创建（append 模式）
```

---

### Task 1: 创建 skill 目录结构 + SKILL.md 主流程文件

**Files:**
- Create: `.claude/skills/lesson-learned/SKILL.md`
- Create: `.claude/skills/lesson-learned/templates/` (directory)

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p /Users/kaicui/Documents/work/project/harness-creator/.claude/skills/lesson-learned/templates
mkdir -p /Users/kaicui/Documents/work/project/harness-creator/.claude/lessons
```

- [ ] **Step 2: 编写 SKILL.md 完整内容**

```markdown
---
name: lesson-learned
description: Use when extracting lessons learned from daily usage — bugs fixed, patterns discovered, tool tips, AI collaboration feedback, tech gotchas, or user preferences. Triggers on: "总结经验", "lesson learned", "记录教训", "/lesson-learned", "回顾一下", or when a session ends and worth capturing insights. Core constraint: NEVER write any file without user's explicit per-item confirmation.
---

# Lesson Learned

## Overview

从日常使用中提取经验教训的 Skill。核心原则：**逐条确认，绝不自动写入**。

AI 扫描对话/变更 → 提取结构化经验 → **逐条展示给用户确认** → 仅在用户明确许可后才写入存储。

## When to Use

```
需要提取经验？
  ├── 是 → 会话结束 / 刚完成一个任务 / 用户主动要求 → ✅ 使用本 Skill
  └── 否 → 不使用
```

## 核心约束（强制，优先级最高）

| 规则 | 说明 |
|------|------|
| **绝不自动写文件** | 任何文件的 Write/Edit 操作必须在用户确认后执行 |
| **严格逐条确认** | 一次只展示一条经验，等用户处理完再展示下一条 |
| **禁止批量确认** | 不可一次性展示所有条目让用户批量通过 |
| **允许修改** | 用户选"修改后写入"时，根据具体意见修订草稿后再确认 |
| **允许丢弃** | 用户选"丢弃"时，该条经验不写入任何文件 |

违反以上任何一条 = Skill 执行失败。

## 5 步管道流程

```
Phase 1: 扫描 ──→ Phase 2: 提取分类 ──→ Phase 3: 去重检查 ──→ Phase 4: 逐条确认 ──→ Phase 5: 写入+索引
```

---

### Phase 1: 扫描（确定输入源）

根据触发方式确定扫描范围：

| 触发方式 | 输入源 | 扫描策略 |
|---------|--------|---------|
| **会话结束自动** | 当前对话上下文 | 回顾本次对话：关键决策、错误修复、用户纠正、踩过的坑、新发现的好做法 |
| **手动 + 无参数** | 当前对话上下文 | 同上 |
| **手动 + git 范围** | git diff | 分析指定范围的代码变更（commit / branch / working tree）|
| **手动 + 文件/片段** | 用户指定的内容 | 分析用户提供的内容 |

**扫描输出：** 一段自然语言描述的"原始观察列表"，包含本次对话/变更中所有值得记录的点。

**如果扫描结果为空（没有值得记录的经验）：**
- 告知用户"本次没有发现值得记录的新经验"
- 直接结束，不进入后续阶段

---

### Phase 2: 提取分类

将原始观察列表中的每条 → 匹配到 6 类模板之一 → 生成结构化草稿。

#### 类型映射表

| 类型 | 识别信号 | 模板文件 |
|------|---------|---------|
| **bug** | 修复了 bug、debug 过程、报错解决、从错误中恢复 | `templates/bug.md` |
| **pattern** | 好的设计决策、架构选择、代码组织方式、正面模式 | `templates/pattern.md` |
| **tool** | 学到新工具用法、命令技巧、快捷键、工作流优化 | `templates/tool.md` |
| **ai-collab** | 纠正了 AI 行为、发现好的 prompt 方式、协作效率提升 | `templates/ai-collab.md` |
| **tech-gotcha** | 特定技术/工具的坑或陷阱（如 Mermaid 中文引号问题）| `templates/tech-gotcha.md` |
| **user-preference** | 用户表达的习惯、喜好、风格倾向、个人工作偏好 | `templates/user-preference.md` |

#### 草稿生成规则

对每条观察：
1. 判断属于哪个类型（参考上方识别信号）
2. 读取对应 `templates/{type}.md` 获取格式规范
3. 按格式填充内容，生成完整草稿
4. 分配临时 ID（格式 `DRAFT-{序号}`）
5. 加入「待确认队列」

**如果某条观察无法清晰归类：**
- 使用 AskUserQuestion 询问用户认为应该归入哪类
- 选项：[bug] [pattern] [tool] [ai-collab] [tech-gotcha] [user-preference] [跳过此条]

**如果待确认队列为空：**
- 告知用户"未提取到有效经验"
- 直接结束

---

### Phase 3: 去重检查

对待确认队列中的每条草稿：

1. 尝试读取 `.claude/lessons/LESSONS.md` 索引文件
2. 如果文件不存在（首次使用）→ 所有条目标记为 `NEW`，跳到 Phase 4
3. 如果文件存在 → 对每条草稿搜索索引中的相似标题/标签
4. 判断重复标准：
   - **高度重复**：同一主题 + 同一类型 + 核心内容一致 → 标记 `DUPLICATE_OF: {已有ID}`
   - **相关但不重复**：主题相关但角度不同 → 标记为 `NEW`，在展示时注明"与 L-xxxxxx 相关"
   - **无关联** → 标记为 `NEW`

**去重结果不影响队列顺序**，只是给每条草稿附加元信息供 Phase 4 展示。

---

### Phase 4: 逐条确认（核心阶段）

对待确认队列中的每条草稿，按顺序逐一处理：

#### 4.1 展示草稿

向用户展示完整的经验草稿：

```markdown
---
## 经验 #{N}/{Total} — 待确认

**类型：** {type}
**去重状态：** NEW / DUPLICATE_OF L-xxxxxx / RELATED TO L-xxxxxx

---

{完整草稿内容（含 frontmatter + body）}
```

#### 4.2 请求确认

使用 AskUserQuestion：

```
问题："以上经验是否准确？如何处理？"

选项（根据去重状态动态调整）：

通用选项：
  [确认写入]     — 原样写入 .claude/lessons/lessons.md 并更新索引
  [修改后写入]   — 用户指出需要调整的地方，AI 修订后再二次确认
  [丢弃]         — 不写入任何文件，跳过此条

仅 DUPLICATE 时额外出现：
  [合并到已有]   — 将此条的关键点追加到已有条目 L-xxxxxx 中
```

#### 4.3 处理用户选择

| 用户选择 | 动作 |
|---------|------|
| **确认写入** | 标记为 `CONFIRMED`，进入 Phase 5 写入 |
| **修改后写入** | 询问具体修改意见 → 修订草稿 → 再次展示修订版 → 重新走 4.1-4.2 |
| **丢弃** | 标记为 `DISCARDED`，不写入，处理下一条 |
| **合并到已有** | 读取已有条目 → 追加关键差异点 → 更新已有条目 → 处理下一条 |

#### 4.4 循环直到队列清空

每条处理完后自动展示下一条。全部处理完毕后进入 Phase 5。

**中途退出：** 如果用户选择"暂停"，保存当前队列状态（已处理的 + 未处理的），告知用户可随时重新触发继续。

---

### Phase 5: 写入 + 索引更新

对所有标记为 `CONFIRMED` 的草稿执行写入操作。

#### 5.1 确保 storage 目录就绪

```bash
# 确保目录存在
.claude/lessons/    # 项目级存储
~/.claude/lessons/  # 全局存储（可选同步）
```

#### 5.2 初始化 LESSONS.md（如不存在）

如果是首次使用（LESSONS.md 不存在），创建初始索引文件：

```markdown
# Lessons Index
> 最后更新: {YYYY-MM-DD HH:MM} | 总计: 0 条 active / 0 条 superseded

| ID | 日期 | 类型 | 标题 | 标签 | 状态 |
|----|------|------|------|------|------|
```

#### 5.3 写入每条确认的经验

对每条 CONFIRMED 草稿：

**a) 追加写入 `lessons.md`**

- 文件路径：`.claude/lessons/lessons.md`
- 如果文件不存在则创建（含 YAML frontmatter 头部说明）
- **始终追加（append），永不修改已有内容**
- 分配正式 ID：`L-{YYYYMMDD}-{NNN}`（NNN 为当日递增序号）

**b) 更新 `LESSONS.md` 索引**

- 在表格的表头行之后插入一行新记录（最新的在最前）
- 字段：ID | date | type | title（取自草稿）| tags | status=active

#### 5.4 全局同步询问（可选）

所有项目级写入完成后：

```
AskUserQuestion:
  "已完成 {N} 条经验的写入。是否同步到全局记忆中心？"
  选项：
  [同步到全局]     — 追加到 ~/.claude/lessons/global-lessons.md
  [仅保留项目级]   — 只在当前项目中保留，不同步
```

#### 5.5 完成汇报

输出最终摘要：

```markdown
## Lesson Learned 完成

**本次结果：**
- 确认写入：{N} 条
- 修改后写入：{M} 条
- 丢弃：{K} 条
- 合并到已有：{L} 条

**存储位置：**
- 项目级：.claude/lessons/lessons.md ({total} 条)
- 索引：.claude/lessons/LESSONS.md
- 全局：{已同步 / 未同步}

**新增条目 ID：** {L-xxx, L-yyy, ...}
```

---

## 模板文件引用

6 类经验的详细格式规范见各模板文件：

| 模板 | 路径 | 用途 |
|------|------|------|
| Bug 模板 | `./templates/bug.md` | Symptom / Root Cause / Fix / Prevention / Time Cost |
| Pattern 模板 | `./templates/pattern.md` | Scenario / Decision / Rationale / When to Apply |
| Tool 模板 | `./templates/tool.md` | Tool Name / Feature / Commands / Gotchas |
| AI 协作模板 | `./templates/ai-collab.md` | Situation / Wrong Behavior / Better Way / Prompt Tip |
| 技术陷阱模板 | `./templates/tech-gotcha.md` | Technology / Trap / Reason / Safe Pattern |
| 用户偏好模板 | `./templates/user-preference.md` | Domain / Preference / Reason / Trigger Condition |

**Phase 2 提取时必须读取对应模板文件以获取准确格式。**

---

## Red Flags — STOP and Check

出现以下信号时停下来检查：

- 用户尚未确认就准备调用 Write/Edit 工具 → **立即停止，回到 Phase 4**
- 一次性展示多条经验要求批量确认 → **拆分为逐条展示**
- 准备修改 lessons.md 中已有内容（而非追加）→ **只追加，不改历史**
- 跳过 Phase 4 直接进入 Phase 5 → **回到 Phase 4 逐条确认**
- 队列中还有未处理条目但准备结束 → **继续处理剩余条目或明确询问用户**

**以上任何一项未通过 = Skill 执行失败。**
```

- [ ] **Step 3: 验证 SKILL.md 格式正确**

确认文件包含以下关键段落：
- [ ] frontmatter（name + description）
- [ ] 核心约束表（5 条规则）
- [ ] Phase 1-5 完整流程
- [ ] Red Flags 段落
- [ ] 无 TBD/TODO 占位符

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/lesson-learned/SKILL.md
git commit -m "feat(lesson-learned): add SKILL.md with 5-phase pipeline flow"
```

---

### Task 2: 编写 bug 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/bug.md`

- [ ] **Step 1: 编写 bug.md**

```markdown
# Bug / 问题类经验模板

## 适用场景

修复了 bug、经历 debug 过程、解决了报错、从错误状态中恢复。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: bug
date: {YYYY-MM-DD}
source: {session-auto | manual | git:{commit_hash}}
tags: [{相关技术}, {相关模块}, {错误类型}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [BUG] {简短标题}

## Context（背景）

{什么场景下发生的？当时在做什么任务？}

## Content

### Symptom（症状）

{表现是什么？报错信息？异常行为？}

### Root Cause（根因）

{为什么出错？根本原因是什么？}

### Fix（修复方案）

{怎么解决的？具体的修复步骤或代码变更？}

### Prevention（预防措施）

{如何避免再次发生？有什么编码习惯或检查可以防止？}

### Time Cost（时间成本）

{花了多长时间定位和修复？用于衡量严重程度}

## Takeaway（一句话总结）

{下次遇到类似问题时记住的关键点}
```

## 示例

```markdown
---
id: L-20260502-001
type: bug
date: 2026-05-02
source: session-auto
tags: [mermaid, rendering, unicode]
duplicate_of: null
status: active
---

# [BUG] Mermaid 流程图中文引号导致渲染失败

## Context（背景）

编写 PRD 时使用 Mermaid 语法绘制业务流程图，包含中文文本的节点。

## Content

### Symptom（症状）

Mermaid 图无法正常渲染，显示语法错误。涉及 3 处流程图的 Line 8/10/18。

### Root Cause（根因）

Mermaid 解析器不支持中文全角标点符号。「」和 ？等字符被当作非法语法。

### Fix（修复方案）

将节点文本中的中文引号「」替换为英文引号 "" 或直接去掉引号。
将中文问号 ？替换为英文问号 ? 或改写为陈述句避免问号。

### Prevention（预防措施）

Mermaid 节点文本统一使用 ASCII 标点符号。建立 checklist：生成含中文的 Mermaid 图时自动检查标点。

### Time Cost（时间成本）

约 20 分钟（排查 + 定位根因 + 逐处修复）

## Takeaway（一句话总结）

Mermaid 节点文本中避免使用中文全角标点，统一用 ASCII 标点或无标点。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 bug 类型：
- 修复了某个报错或异常行为
- 经历了 debug 过程（试了几种方法才解决）
- 发现了某个容易出错的地方并找到了正确做法
- 从错误状态恢复到正常状态的完整过程
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/bug.md
git commit -m "feat(lesson-learned): add bug template with example"
```

---

### Task 3: 编写 pattern 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/pattern.md`

- [ ] **Step 1: 编写 pattern.md**

```markdown
# 模式 / 最佳实践类经验模板

## 适用场景

好的设计决策、架构选择、代码组织方式、发现了有效的模式或最佳实践。这是**正向**的经验——记录"做得好的地方"以便复用。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: pattern
date: {YYYY-MM-DD}
source: {session-auto | manual | git:{commit_hash}}
tags: [{领域}, {模式名}, {适用场景}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [PATTERN] {简短标题}

## Context（背景）

{在什么项目/任务的什么阶段做出的这个决策？}

## Content

### Scenario（场景）

{面临什么问题或需求？有哪些备选方案？}

### Decision（决策）

{最终选择了什么方案/模式？}

### Rationale（理由）

{为什么选这个？权衡了哪些因素？取舍了什么？}

### When to Apply（适用条件）

{什么情况下可以复用这个模式？有什么前提条件？}

## Takeaway（一句话总结）

{这个模式的核心价值是什么？什么时候该想到用它？}
```

## 示例

```markdown
---
id: L-20260502-002
type: pattern
date: 2026-05-02
source: session-auto
tags: [prd, workflow, skeleton-first]
duplicate_of: null
status: active
---

# [PATTERN] PRD 先骨架后血肉的写作顺序

## Context（背景）

设计 write-prd skill 时确定文档编写流程。

## Content

### Scenario（场景）

需要编写一份完整的产品需求文档，包含概述、业务流程、功能清单、详细设计等多章节。

### Decision（决策）

先写 §2 业务流程 + §3 功能清单定骨架，再逐功能点填充 §4 详细设计。

### Rationale（理由）

先定骨架能确保功能点不遗漏、编号连续；先填细节会导致遗漏和编号跳跃。

### When to Apply（适用条件）

编写任何多章节的结构化文档时：PRD、技术方案、测试计划等。

## Takeaway（一句话总结）

多章节文档先定骨架（流程+清单）再填细节，避免遗漏和返工。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 pattern 类型：
- 做了一个架构/设计决策并且效果不错
- 发现了一种好的代码组织方式
- 解决问题时用到了某种设计模式
- 某种做法比其他替代方案明显更好
- 用户说"这个思路很好"、"这样组织很清晰"
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/pattern.md
git commit -m "feat(lesson-learned): add pattern template with example"
```

---

### Task 4: 编写 tool 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/tool.md`

- [ ] **Step 1: 编写 tool.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/tool.md
git commit -m "feat(lesson-learned): add tool template with example"
```

---

### Task 5: 编写 ai-collab 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/ai-collab.md`

- [ ] **Step 1: 编写 ai-collab.md**

```markdown
# AI 协作经验模板

## 适用场景

与 AI 协作过程中发现的效率提升点：纠正了 AI 的不当行为、发现了更好的 prompt 方式、建立了有效的协作模式。这类经验的核心价值是**让未来的 AI 交互更高效**。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: ai-collab
date: {YYYY-MM-DD}
source: {session-auto | manual}
tags: [{协作场景}, {问题类型}, {prompt-technique}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [AI-COLLAB] {简短标题}

## Context（背景）

{在什么类型的任务中与 AI 协作时发现的？}

## Content

### Situation（场景）

{当时让 AI 做什么任务？期望的输出是什么？}

### What AI Did Wrong（AI 哪里做错了）

{AI 的实际行为哪里不符合预期？}

### What Works Better（更好的做法）

{后来发现什么方式效果更好？}

### Prompt Tip（Prompt 建议）

{下次类似任务时，可以用什么样的 prompt 来引导 AI？给出具体示例。}

## Takeaway（一句话总结）

{这类任务中与 AI 协作的关键要点是什么？}
```

## 示例

```markdown
---
id: L-20260502-004
type: ai-collab
date: 2026-05-02
source: session-auto
tags: [prd, writing-process, section-by-section]
duplicate_of: null
status: active
---

# [AI-COLLAB] 多章节文档需逐节确认而非一次性输出

## Context（背景）

让 AI 编写 PRD 这类多章节结构化文档时。

## Content

### Situation（场景）

要求 AI 编写一份完整的 PRD 文档（6 个章节）。

### What AI Did Wrong（AI 哪里做错了）

AI 倾向于一次性输出所有章节内容，导致：
- 后面章节的质量下降（注意力分散）
- 用户无法在早期介入调整方向
- 整体结构可能偏离预期但发现太晚

### What Works Better（更好的做法）

每写完一个章节后暂停，展示给用户确认，满意后再继续下一节。

### Prompt Tip（Prompt 建议）

在 prompt 中加入约束：「每写一节之前和我确认写作思路，每完成一节后和我确认再继续下一节」。或在 skill 定义中加入强制性的逐节确认流程。

## Takeaway（一句话总结）

长文档生成必须分节确认，否则后期偏差难以挽回。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 ai-collab 类型：
- 用户纠正了 AI 的行为（"不对，你应该..."、"不是这样"）
- 发现某种 prompt 方式效果明显更好
- AI 的默认行为导致需要大量返工
- 建立了某种高效的协作模式或约定
- 用户表达了关于如何更好使用 AI 的见解
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/ai-collab.md
git commit -m "feat(lesson-learned): add ai-collab template with example"
```

---

### Task 6: 编写 tech-gotcha 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/tech-gotcha.md`

- [ ] **Step 1: 编写 tech-gotcha.md**

```markdown
# 技术陷阱类经验模板

## 适用场景

特定技术、框架、库、工具的已知陷阱或坑。与 bug 模板的区别：**bug 是自己犯的错**，**tech-gotcha 是技术本身的坑**（即使你做对了也会中招的那种）。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: tech-gotcha
date: {YYYY-MM-DD}
source: {session-auto | manual | git:{commit_hash}}
tags: [{技术/工具}, {陷阱类型}, {影响范围}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [GOTCHA] {简短标题}

## Context（背景）

{在使用什么技术/工具做什么事情时遇到的？}

## Content

### Technology（技术/工具）

{涉及哪个技术、框架、库或工具？版本？}

### The Trap（陷阱）

{具体的坑是什么？表现是什么？}

### Why It Happens（原因）

{为什么会这样？底层原因是什么？}

### Safe Pattern（安全写法）

{正确的/安全的做法是什么？给出代码示例或配置示例}

## Takeaway（一句话总结）

{使用这项技术时要时刻记住的一条规则}
```

## 示例

```markdown
---
id: L-20260502-005
type: tech-gotcha
date: 2026-05-02
source: session-auto
tags: [mermaid, unicode, chinese-punctuation]
duplicate_of: null
status: active
---

# [GOTCHA] Mermaid.js 不支持中文全角标点符号

## Context（背景）

在 PRD 文档中使用 Mermaid 语法绘制包含中文的业务流程图。

## Content

### Technology（技术/工具）

Mermaid.js（流程图/图表渲染引擎）

### The Trap（陷阱）

节点文本中使用中文全角标点（如 「」！？）会导致 Mermaid 解析失败，图表无法渲染。不会给出清晰的错误提示，只会静默失败或显示语法错误。

### Why It Happens（原因）

Mermaid 的解析器基于 ASCII 字符集设计，未处理 Unicode CJK 标点符号范围（FF01–FF5E）。这些字符在解析器中被视为非法 token。

### Safe Pattern（安全写法）

```mermaid
## 错误写法（会导致解析失败）
U6[确认归档弹窗] %% 归档流程复用此节点概念
M2(弹窗内容："确定归档「XXX」？...")

## 正确写法
U6[确认归档弹窗] %% 归档流程复用此节点概念
M2(弹窗内容：确定归档 XXX？归档后该项目将不可编辑)
```

规则：Mermaid 节点文本中统一使用 ASCII 标点，或完全不用标点。

## Takeaway（一句话总结）

Mermaid 节点文本禁止使用中文全角标点符号，统一 ASCII 或无标点。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 tech-gotcha 类型：
- 某个技术/框架的行为与直觉不符
- 按照官方文档做却出了问题
- 特定版本有已知问题或 breaking change
- 配置项之间有隐含的依赖或冲突
- 跨环境（OS/浏览器/运行时）行为不一致
- 与字符编码/Unicode 相关的问题
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/tech-gotcha.md
git commit -m "feat(lesson-learned): add tech-gotcha template with example"
```

---

### Task 7: 编写 user-preference 模板

**Files:**
- Create: `.claude/skills/lesson-learned/templates/user-preference.md`

- [ ] **Step 1: 编写 user-preference.md**

```markdown
# 主人偏好 / 习惯类经验模板

## 适用场景

记录技能使用者（你）的个人习惯、风格偏好、工作方式倾向。这类经验帮助 AI 在后续协作中更好地适配你的方式，减少反复磨合。

## 输出格式

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: user-preference
date: {YYYY-MM-DD}
source: {session-auto | manual}
tags: [{领域}, {偏好类型}]
duplicate_of: {null | L-xxxxxx}
status: active
---

# [PREF] {简短标题}

## Context（背景）

{在什么场景下表达了这个偏好？}

## Content

### Domain（领域）

{这个偏好属于哪个方面？如：代码风格、文档格式、沟通方式、工具配置等}

### Preference（偏好内容）

{具体的偏好是什么？尽量精确描述}

### Reason（原因）

{为什么有这个偏好？（如有明确原因则填写，如"因为..."、"为了..."）}

### Trigger Condition（触发条件）

{什么时候应该应用这个偏好？AI 在什么情况下应该记住并遵循它？}

## Takeaway（一句话总结）

{AI 在后续协作中关于这一点要记住什么？}
```

## 示例

```markdown
---
id: L-20260502-006
type: user-preference
date: 2026-05-02
source: session-auto
tags: [writing, document-review, workflow]
duplicate_of: null
status: active
---

# [PREF] 多章节文档必须逐节确认才能继续

## Context（背景）

编写 write-prd skill 时，对 AI 输出多章节文档的方式提出要求。

## Content

### Domain（领域）

文档写作 / AI 输出质量控制

### Preference（偏好内容）

当 AI 需要输出包含多个章节的内容时（如 PRD、技术方案、设计文档）：
1. 每章开始前：先输出写作思路（覆盖内容、重点、预判决策点），确认后再写
2. 每章完成后：展示完成摘要（核心产出、数据点），确认后再写下一章
3. 严禁一次性写完多章再统一确认

### Reason（原因）

一次性输出多章节导致：
- 后期章节质量下降（AI 注意力衰减）
- 方向偏差发现太晚，返工成本高
- 用户失去对输出质量的控制感

### Trigger Condition（触发条件）

任何时候 AI 需要输出超过 1 个章节的结构化内容时，自动启用此偏好。

## Takeaway（一句话总结）

长文档 = 分节确认。宁可慢一点，也要保证每节质量可控。
```

## 提取提示词（给 AI 的指导）

当观察到以下信号时，考虑提取为 user-preference 类型：
- 用户表达了对某种方式的明确偏好（"我喜欢..."、"我习惯..."）
- 用户纠正了 AI 的输出风格（"不要太啰嗦"、"给我简洁版本"）
- 用户设定了工作流程上的规则（"每次都要..."、"以后都按这个来"）
- 用户对交互方式提出了要求（"先问我再..."、"确认后再..."）
- 用户分享了个人工作习惯或方法论偏好
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/lesson-learned/templates/user-preference.md
git commit -m "feat(lesson-learned): add user-preference template with example"
```

---

### Task 8: 初始化 LESSONS.md 索引文件 + 验证整体集成

**Files:**
- Create: `.claude/lessons/LESSONS.md`

- [ ] **Step 1: 创建 LESSONS.md 初始索引文件**

```markdown
# Lessons Index
> 最后更新: -- | 总计: 0 条 active / 0 条 superseded

| ID | 日期 | 类型 | 标题 | 标签 | 状态 |
|----|------|------|------|------|------|

<!--
  本文件由 lesson-learned skill 自动维护。
  新条目插入到表格顶部（最新在前）。
  手动修改可能导致与 lessons.md 不同步。
-->
```

- [ ] **Step 2: 验证完整文件结构**

```bash
# 验证所有文件存在
ls -la .claude/skills/lesson-learned/SKILL.md
ls -la .claude/skills/lesson-learned/templates/bug.md
ls -la .claude/skills/lesson-learned/templates/pattern.md
ls -la .claude/skills/lesson-learned/templates/tool.md
ls -la .claude/skills/lesson-learned/templates/ai-collab.md
ls -la .claude/skills/lesson-learned/templates/tech-gotcha.md
ls -la .claude/skills/lesson-learned/templates/user-preference.md
ls -la .claude/lessons/LESSONS.md
```

预期：所有 8 个文件均存在且非空。

- [ ] **Step 3: 验证 SKILL.md frontmatter 可被识别**

确认 SKILL.md 的 frontmatter 包含：
- `name: lesson-learned`
- `description:` 包含 triggers 关键词（"总结经验", "lesson learned", "/lesson-learned" 等）

- [ ] **Step 4: 最终 Commit**

```bash
git add .claude/lessons/LESSONS.md
git commit -m "feat(lesson-learned): initialize LESSONS.md index file"
```

---

## Self-Review Checklist

### Spec 覆盖度

| Spec 要求 | 对应 Task |
|----------|----------|
| 5 步管道流程（扫描→提取→去重→确认→写入）| Task 1 (SKILL.md Phase 1-5) |
| 6 类经验模板 | Task 2-7 |
| 逐条确认约束（核心）| Task 1 (SKILL.md Phase 4 + 核心约束) |
| 绝不自动写文件 | Task 1 (SKILL.md 核心约束表) |
| bug 类（Symptom/Cause/Fix/Prevention/Cost）| Task 2 |
| pattern 类（Scenario/Decision/Rationale/Apply）| Task 3 |
| tool 类（Tool/Feature/Commands/Gotchas）| Task 4 |
| ai-collab 类（Situation/Wrong/Better/PromptTip）| Task 5 |
| tech-gotcha 类（Tech/Trap/Reason/SafePattern）| Task 6 |
| user-preference 类（Domain/Pref/Reason/Trigger）| Task 7 |
| LESSONS.md 索引格式 | Task 8 |
| lessons.md append-only 存储模式 | Task 1 (SKILL.md Phase 5.3) |
| 去重检查机制 | Task 1 (SKILL.md Phase 3) |
| 全局可选同步 | Task 1 (SKILL.md Phase 5.4) |
| Roadmap 后续迭代 | Design Doc (不在实现范围) |

### 占位符扫描

- [ ] 无 TBD / TODO
- [ ] 无 "适当处理" / "添加验证" 等模糊描述
- [ ] 每个 Step 都有实际内容（代码/文本/命令）

### 一致性检查

- [ ] SKILL.md 中引用的模板文件名与 Task 2-7 创建的文件名一致
- [ ] 各模板中的字段名与 SKILL.md Phase 2 描述一致
- [ ] LESSONS.md 表头字段与 SKILL.md Phase 5.3(b) 描述一致
- [ ] ID 格式 `L-{YYYYMMDD}-{NNN}` 在所有文件中统一
