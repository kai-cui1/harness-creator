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
