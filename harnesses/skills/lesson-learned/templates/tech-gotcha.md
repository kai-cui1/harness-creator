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
