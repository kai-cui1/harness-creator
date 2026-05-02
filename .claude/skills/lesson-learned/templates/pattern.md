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
