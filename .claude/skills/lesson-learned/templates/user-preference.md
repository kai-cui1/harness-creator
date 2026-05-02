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
