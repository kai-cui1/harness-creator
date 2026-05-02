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
