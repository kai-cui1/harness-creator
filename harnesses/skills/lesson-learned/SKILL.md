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

**如果扫描结果为空（没有值得记录的新经验）：**
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
| 用户偏好模板 | `./templates/user-preference.md` | Domain / Preference / Reason | Trigger Condition |

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
