# Lesson Learned Skill 设计文档

> 日期: 2026-05-02
> 状态: Design Approved (待实现)
> 范围: MVP — 经验总结 + 逐条确认核心功能

## 1. 目标与约束

### 目标
构建一个 Skill，让 AI Agent 能从日常使用中**自动提取经验教训**，并以**逐条确认**的方式写入存储，不未经用户许可修改任何文件。

### 核心约束
1. **绝不自动写文件**：每条经验必须经用户确认后才写入
2. **逐条确认**：一次只展示一条，禁止批量确认
3. **纯 markdown 实现**：无代码依赖，SKILL.md + 模板文件

### 触发方式
- **会话结束自动触发**：重要对话结束时（参考 CLAUDE.md 中「重要对话」定义）
- **用户手动触发**：输入 `/lesson-learned` 或「总结经验」

## 2. 文件结构

```
.claude/skills/lesson-learned/
├── SKILL.md                    # 主流程编排（5 步管道）
├── templates/
│   ├── bug.md                  # Bug/问题类模板
│   ├── pattern.md              # 模式/最佳实践模板
│   ├── tool.md                 # 工具/工作流模板
│   ├── ai-collab.md            # AI 协作经验模板
│   ├── tech-gotcha.md          # 技术陷阱模板
│   └── user-preference.md      # 主人偏好/习惯模板

# 运行时产生（首次写入时自动创建）
.claude/lessons/
├── lessons.md                  # 所有经验的完整存储（按时间追加）
└── LESSONS.md                  # 索引文件（表格形式）

~/.claude/lessons/              # 全局记忆中心（跨项目共享，MVP 可选同步）
└── global-lessons.md           # 全局经验索引
```

## 3. 5 步管道流程

```
Phase 1: 扫描 ──→ Phase 2: 提取分类 ──→ Phase 3: 去重检查 ──→ Phase 4: 逐条确认 ──→ Phase 5: 写入+索引
```

### Phase 1: 扫描（确定输入源）

| 触发方式 | 输入源 | 扫描策略 |
|---------|--------|---------|
| 会话结束自动 | 当前对话上下文 | 回顾关键决策、错误修复、用户纠正 |
| 手动 + 无参数 | 当前对话上下文 | 同上 |
| 手动 + 指定范围 | git diff / 指定文件 / 对话片段 | 按用户指定范围扫描 |

### Phase 2: 提取分类

从扫描结果中识别经验 → 匹配到 6 类模板：

| 类型 | 识别信号 | 模板文件 |
|------|---------|---------|
| **bug** | 修复了 bug、debug 过程、报错解决 | templates/bug.md |
| **pattern** | 好的设计决策、架构选择、代码组织 | templates/pattern.md |
| **tool** | 学到新工具用法、命令技巧、快捷键 | templates/tool.md |
| **ai-collab** | 纠正 AI 行为、发现好的 prompt 方式 | templates/ai-collab.md |
| **tech-gotcha** | 特定技术坑/陷阱（如 Mermaid 中文引号） | templates/tech-gotcha.md |
| **user-preference** | 用户表达的习惯、喜好、风格倾向 | templates/user-preference.md |

每条提取为结构化草稿 → 进入"待确认队列"。

### Phase 3: 去重检查

对队列中每条经验：
1. 读 `LESSONS.md` 索引，搜索相似主题已有记录
2. 高度重复 → 标记 `DUPLICATE_OF: {ID}`，提示用户选择：合并 / 保留新 / 丢弃
3. 无重复 → 标记 `NEW`，进入 Phase 4

### Phase 4: 逐条确认（核心约束）

对每条 `NEW` 经验：

```
展示完整草稿（含类型标签、内容、去重状态）
    ↓
AskUserQuestion:
  "这条经验是否准确？如何处理？"
  [确认写入]     — 原样写入 lessons.md
  [修改后写入]   — 根据用户意见修订后写入
  [丢弃]         — 不写入
  [合并到已有]   — 仅 DUPLICATE 时出现
```

**规则**：
- 严格逐条，一次一条
- 禁止批量展示
- 用户选"修改后写入"时根据具体意见修订

### Phase 5: 写入 + 索引更新

确认后：
1. **追加写入** `lessons.md`（append，不改已有内容）
2. **更新索引** `LESSONS.md`（表格顶部插入一行摘要）
3. **询问是否同步全局** `~/.claude/lessons/global-lessons.md`

## 4. 经验条目格式

### 统一外壳（所有类型共用）

```markdown
---
id: L-{YYYYMMDD}-{NNN}
type: {bug|pattern|tool|ai-collab|tech-gotcha|user-preference}
date: {YYYY-MM-DD}
source: {session-auto | manual | git:{commit_hash}}
tags: [{tag1}, {tag2}]
duplicate_of: {null | L-xxxxxx}
status: {active | superseded}
---

# [{类型标签}] {简短标题}

## Context（背景）
{什么场景下发生的}

## Content（内容）
{根据类型的结构化内容}

## Takeaway（一句话总结）
{下次遇到类似情况时记住的关键点}
```

### 各类型 Content 段差异

#### bug（Bug/问题类）

```markdown
## Content
- **Symptom（症状）**: {表现}
- **Root Cause（根因）**: {为什么出错}
- **Fix（修复方案）**: {怎么解决的}
- **Prevention（预防）}: {如何避免再次发生}
- **Time Cost（时间成本）**: {花了多长时间}
```

#### pattern（模式/最佳实践）

```markdown
## Content
- **Scenario（场景）}: {什么情况下用的}
- **Decision（决策）}: {做了什么选择}
- **Rationale（理由）}: {为什么这样选}
- **When to Apply（适用条件）}: {什么情况复用}
```

#### tool（工具/工作流）

```markdown
## Content
- **Tool（工具）}: {工具名}
- **Learned Feature（学到的新功能）}: {发现了什么能力}
- **Key Commands（关键命令）}: {常用命令}
- **Gotchas（踩坑点）}: {容易出错的地方}
```

#### ai-collab（AI 协作经验）

```markdown
## Content
- **Situation（场景）}: {什么任务中}
- **What AI Did Wrong（AI 哪里做错了）}: {具体行为}
- **What Works Better（更好的做法）}: {应该怎么做}
- **Prompt Tip（Prompt 建议）}: {下次可以怎么提示}
```

#### tech-gotcha（技术陷阱）

```markdown
## Content
- **Technology（技术）}: {涉及的技术/工具}
- **The Trap（陷阱）}: {什么坑}
- **Why It Happens（原因）}: {为什么会这样}
- **Safe Pattern（安全写法）}: {正确的做法}
```

#### user-preference（主人偏好）

```markdown
## Content
- **Domain（领域）}: {哪个方面}
- **Preference（偏好）}: {具体习惯/喜好}
- **Reason（原因）}: {为什么有这个偏好}
- **Trigger Condition（触发条件）}: {什么时候该应用此偏好}
```

## 5. 索引文件格式 (LESSONS.md)

```markdown
# Lessons Index
> 最后更新: {YYYY-MM-DD HH:MM} | 总计: {N} 条 active / {M} 条 superseded

| ID | 日期 | 类型 | 标题 | 标签 | 状态 |
|----|------|------|------|------|------|
| L-20260502-001 | 2026-05-02 | tech-gotcha | Mermaid 中文引号陷阱 | mermaid,unicode | active |
| L-20260502-002 | 2026-05-02 | user-preference | PRD 写作需逐节确认 | prd,workflow | active |
```

规则：
- 新条目插入表格顶部（最新在前）
- 按 ID 日期顺序排列
- status 支持 `active` / `superseded`

## 6. Roadmap（后续迭代）

### v0.2 — 记忆系统增强
- [ ] 全局记忆中心完善（身份隔离、按 agent 类型分目录）
- [ ] 项目间记忆选择性同步机制
- [ ] 经验过期/衰减策略

### v0.3 — 智能化增强
- [ ] 自动触发条件细化（不仅靠会话结束，还可基于事件）
- [ ] 经验关联图谱（相关经验互相引用）
- [ ] 定期回顾提醒（如每周回顾本周新增经验）

### v0.4 — 与其他 Skill 集成
- [ ] write-prd 完成后自动触发 lesson-learned
- [ ] 编码完成后自动从 git diff 提取 bug/pattern 类经验
- [ ] 经验反哺：写入的经验在后续同类任务中被自动引用
