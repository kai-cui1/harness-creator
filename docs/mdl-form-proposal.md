# MDL（Methodology Description Language）形态定义提案 v0.1

> **版本**：v0.1（MVP 阶段定稿）
> **日期**：2026-04-23
> **状态**：✅ 已确认（5 项设计决策全部敲定）

---

## 一、设计决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 表达形态 | **混合形态**（结构化骨架 + 自然语言注解） | 真实规范 ~60-70% 隐式知识，纯 schema 无法覆盖；纯自然语言又无法被机器可靠解析 |
| 目标输出 | **Claude Code Skill**（.md 格式） | MVP 验证最快，生态最成熟，用户最熟悉 |
| 首个验证对象 | **磁贴样式规范**（翻译机 3.0） | 自包含、规则完整、复杂度适中、可验证 |

---

## 二、MDL 核心概念模型

### 2.1 双层结构

```
MDL 文档 = 结构化骨架（Frontmatter / YAML） + 自然语言主体（Markdown）
```

**类比**：就像 OpenAPI 规范 — JSON Schema 定义接口结构，`description` 字段承载人类可读的解释。

### 2.2 四层表达层次

```
┌─────────────────────────────────────────────┐
│ L1 元层 (Meta)                              │
│  名称 / 版本 / 作者 / 日期 / 目标平台 /       │
│  目标 Agent / 状态 / 引用关系                │
├─────────────────────────────────────────────┤
│ L2 原则层 (Principles)                      │
│  设计原则 / 适用范围 / 行为假设 /             │
│  优先级与冲突解决                            │
├─────────────────────────────────────────────┤
│ L3 规范层 (Specifications) ← 核心密度区      │
│  ├─ 组件规格 (Component Spec)               │
│  ├─ 交互流程 (Interaction Flow)             │
│  ├─ 异常处理 (Exception Pattern)            │
│  ├─ 信息架构 (Information Architecture)     │
│  └─ 设计模式 (Design Pattern) [P2]          │
├─────────────────────────────────────────────┤
│ L4 实例层 (Instances)                       │
│  具体实例配置 / 变更记录 / 待定项 /           │
│  评审意见                                    │
└─────────────────────────────────────────────┘
```

---

## 三、MDL 文件格式详细定义

### 3.1 整体文件结构

```markdown
---
# === L1 元层：YAML Frontmatter ===
mdl: "1.0"
name: "磁贴组件设计规范"
version: "0.1.0"
author: "黄林森"
date: "2018-XX-XX"
source: "翻译机3.0交互文档/磁贴样式规范（new）.html"
platform:
  os: "Android 8.1"
  screen: "480x800px"
  device: "讯飞翻译机 3.0"
target_agent: "claude-code-skill"
status: "draft"          # draft | review | published | deprecated
references:
  - name: "翻译机2.0磁贴规范"
    relation: "inherits" # inherits | extends | conflicts | inspired_by
---

# === L2 原则层：Markdown 自然语言 ===

## 设计原则

### 易学性
<!-- 自然语言描述 + 行为假设 -->
用户通过**色块大小和颜色**辅助记忆功能位置，通过 **logo 形状**识别应用功能，通过**文字名称**确认应用功能。

**行为假设**：用户已有手机端操作心智模型，无需重新学习。

### 高效性
屏幕仅 3.1 英寸，误触成本高，因此：
- 扩大操作热区
- 利用手势操作减少点击次数
- 简化界面层级

## 适用范围与约束
- 本规范适用于翻译机 3.0 Home 页面的应用入口磁贴
- 不适用于系统级 UI 元素（状态栏、导航栏等）

---

# === L3 规范层：结构化 + 自然语言混合 ===

## 组件规格：磁贴 (Tile)

### 基本信息

| 属性 | 值 |
|------|-----|
| 组件名 | Tile（磁贴） |
| 类型 | 应用入口组件 |
| 父容器 | Home 页面网格布局 |

### 结构化约束（YAML 代码块）

\```yaml
component:
  name: Tile
  variants:
    - name: wide
      size: "占据一行宽度"
      aspect_ratio: "~2:1"
    - name: small
      size: "占据半行宽度"
      aspect_ratio: "~1:1"

  fixed_fields:           # 必填字段
    - field: app_icon
      type: image
      required: true
      description: "应用图标，固定尺寸"
    - field: app_name
      type: string
      required: true
      max_length: 4       # 中文字符数
      description: "应用名称"

  optional_fields:        # 选填字段（本期不实现）
    - field: dynamic_info
      type: string
      description: "动态信息（如当前语种、流量套餐余量）"
      implementation_status: "deferred"  # deferred | planned | deprecated

  constraints:            # 排除性约束（"不做什么"）
    - rule: "不支持用户自定义尺寸"
      rationale: "固定尺寸保证布局一致性"
    - rule: "不支持用户自定义位置顺序"
      rationale: "后台统一配置上下架"
    - rule: "不支持卸载"
      rationale: "预装应用不可移除"
    - rule: "不承载通知/角标类运营信息"
      rationale: "保持界面简洁"

  visual_spec:
    background: "固定纯色（由 UI 设计师给出色号）"
    layout: "icon 居上 + name 居下"
\```

### 各功能磁贴规格表

| 功能 | 尺寸 | 背景色建议 | APP 名称 | APP Logo | 动态信息 |
|------|------|-----------|----------|----------|---------|
| 拍照翻译 | wide | 待 UI 定 | 拍照翻译 | (icon) | 无 |
| 全球上网 | wide | 待 UI 定 | 全球上网 | (icon) | 流量套餐(延期) |
| 同声传译 | small | 待 UI 定 | 同声传译 | (icon) | 语种(延期) |
| 录音翻译 | small | 待 UI 定 | 录音翻译 | (icon) | 无 |
| 设置 | small | 待 UI 定 | 设置 | (icon) | 无 |
| 个人中心 | small | 待 UI 定 | 个人中心 | (icon) | 绑定状态(延期) |
| 人工翻译 | small | 待 UI 定 | 人工翻译 | (icon) | 无 |
| 口语学习 | small | 待 UI 定 | 口语学习 | (icon) | 无 |
| SOS | small | 待 UI 定 | SOS | (icon) | 无 |

### 设计理由（Rationale）

每个磁贴元素的设计理由：

| 元素 | 设计理由 | 用户价值 |
|------|---------|---------|
| 背景色块 | 不同功能使用不同颜色 | 通过色块辅助记忆功能位置 |
| App Logo | 每个应用有独特图标 | 通过 logo 形状快速识别 |
| 应用名称 | 4 字以内中文名称 | 通过文字精确确认功能 |
| 固定尺寸 | 只有 wide/small 两种 | 降低认知负荷，形成空间预期 |
| 固定位置 | 后台配置，用户不可调 | 保证每次看到的一致性 |

---

## 交互流程：SOS 紧急联络（参考示例）

### 流程图（伪代码风格）

\```yaml
interaction_flow:
  name: "SOS 紧急联络"
  trigger:
    type: "hardware_button"
    element: "背部 SOS 物理按键"
    condition: "长按 ≥ 3 秒"

  steps:
    - step: 1
      action: "设备震动 2 秒"
      feedback: "触觉反馈 — 确认触发"

    - step: 2
      decision: "网络是否已连接?"
      branches:
        - condition: false  # 未联网
          action: "显示异常弹窗"
          dialog:
            title: "网络未连接"
            message: "SOS 暂时不能用"
            buttons: ["连接网络", "取消"]
          exit: true

        - condition: true   # 已联网
          goto_step: 3

    - step: 3
      decision: "SOS 功能是否已开启?"
      branches:
        - condition: false  # 未开启
          action: "显示引导弹窗"
          dialog:
            title: "紧急联络功能尚未开启"
            message: "请先在设置中开启紧急联络"
            buttons: ["去开启", "取消"]
          exit: true

        - condition: true   # 已开启
          goto_step: 4

    - step: 4
      action: "发送短信 + GPS 位置给紧急联络人"
      feedback:
        - toast: "正在发送短信..."  # 持续至发送完成
        - toast: "短信已发送"        # 显示 5 秒后消失
\```

---

## 异常处理模式（参考示例）

### 统一异常框架

\```yaml
exception_pattern:
  name: "统一异常页面"
  structure:
    page_title: "{当前功能名}"
    icon: "统一错误图标"
    description: "人性化文案（非技术术语）"
    recovery_action: "引导性按钮文案"
    back_navigation: "左上角返回按钮（始终存在）"

  categories:
    - type: "service_error"
      user_message: "服务不稳定，请稍后再试"
      recovery: "刷新"
      auto_retry: false

    - type: "network_error"
      user_message: "请先连接网络，再使用此功能"
      recovery: "连接网络"
      auto_retry: false

    - type: "timeout"
      threshold: "8 秒"
      loading_message: "加载中..."
      error_message: "加载超时，请检查网络"
      recovery: "重试"

    - type: "input_invalid"
      user_message: "没听清，请再说一次"
      recovery: "重新输入（自动回到录音状态）"
\```

---

# === L4 实例层 ===

## 变更记录

| 序号 | 时间 | 需求名 | 修订内容 | 提出人 |
|------|------|--------|---------|--------|
| 1 | 2018-XX-XX | 磁贴规范初版 | 新增磁贴组件规范 | 黄林森 |
| ... | ... | ... | ... | ... |

## 待定项

| 标记 | 内容 | 影响范围 | 建议 |
|------|------|---------|------|
| `(待定)` | 背景具体色号 | 所有磁贴 | 等 UI 输出 |
| `(本期不实现)` | 动态信息字段 | wide 磁贴 | 下期迭代 |
| `(可能会去掉)` | 某功能磁贴 | Home 页布局 | 待产品确认 |

## 评审决议

> （留空，待评审后填写）
```

---

## 四、关键设计决策说明

### 4.1 为什么选 YAML Frontmatter + Markdown 主体？

| 考量 | YAML+MD 的优势 | 纯 JSON Schema | 纯 Markdown+标签 |
|------|---------------|----------------|-----------------|
| **机器可读性** | Frontmatter 可直接解析为结构化数据 | 最强 | 弱（依赖 AI 解析标签） |
| **人类可写性** | 高（任何文本编辑器可写） | 低（需要 IDE/工具辅助） | 最高 |
| **表达力** | 结构化字段 + 自由 Markdown 正文 | 受 schema 限制 | 最自由但最不稳定 |
| **工具链成熟度** | 极高（Hugo/Jekyll/GitHub 全支持） | 中等 | 低（需自建工具） |
| **Git 友好** | 天然 diff 友好 | 可读但冗长 | 天然 diff 友好 |

### 4.2 不确定性表达机制

MDL 使用以下标记来表达规则的状态：

| 标记 | 含义 | 示例 |
|------|------|------|
| *(无标记)* | 确定性规则 | `max_length: 4` |
| `implementation_status: deferred` | 确定要做但本期不做 | 动态信息字段 |
| `(待定)` | 值尚未确定 | 背景色号 |
| `(本期不实现)` | 明确不在本期范围 | 动态信息展示 |
| `(可能会去掉)` | 存在争议，可能删除 | 某功能入口 |
| `status: deprecated` | 已废弃的规则 | 旧版某约束 |

### 4.3 MVP 范围边界

**包含（必须实现）**：
- L1 元层完整定义
- L2 原则层基本结构
- L3 组件规格（核心 — 以磁贴规范为验证对象）
- L3 排除性约束表达
- L3 设计理由（Rationale）字段
- L4 变更记录和待定项基础结构

**不包含（延后到 v0.2+）**：
- L3 交互流程完整语法（SOS 作为参考示例保留，但不做编译目标）
- L3 异常处理模式完整语法
- L3 信息架构表达
- L3 设计模式
- L3 视觉基础（色彩/字体/间距等）
- 编译器实现（MDL → Claude Code Skill 的转换逻辑）
- 版本管理自动化
- 引用/导入机制

---

## 五、从 MDL 到 Claude Code Skill 的编译路径（概念性）

```
MDL 文件 (.mdl.md)
    │
    ▼  [MDL Parser — 提取结构化数据]
    │
中间表示 (IR — JSON)
    │
    ▼  [Skill Compiler — 针对 Claude Code 格式优化]
    │
Claude Code Skill (.md)
    │
    ├── 元信息 → Skill 头部注释
    ├── 设计原则 → Skill 的指导原则段落
    ├── 组件规格 → Skill 的规则列表 / 检查清单
    ├── 排除性约束 → Skill 的 "Don't" 列表
    ├── 设计理由 → Skill 的背景说明（帮助 Agent 理解 why）
    └── 实例表 → Skill 的参考示例
```

**注意**：MVP 阶段编译路径可以是**手动或半自动**的 — 先验证 MDL 表达能力是否足够，再考虑自动化编译。

---

## 六、设计决策结论（2026-04-23 确认）

### Q1: 文件扩展名 → `.mdl.md`
双扩展名明确标识 MDL 身份，同时保留 Markdown 工具链兼容性。

### Q2: Schema 校验 → MVP 需要，保持轻量
只校验 L1 元层 + L3 组件规格骨架字段，自然语言注解部分不校验。

### Q3: 多文件 vs 单文件 → 支持两种模式
- 单文件模式：小型 Harness（MVP 先实现这个）
- 多文件模式：大型 Harness，用入口文件 + 子文件引用（v0.2+）

### Q4: 自然语言注解结构化程度 → 三级梯度
- YAML 代码块 → 强结构化（机器必须解析）
- Markdown 表格 → 半结构化（机器应能解析，容错率高）
- 普通段落 → 纯自然语言（机器辅助理解）

### Q5: 格式兼容性 → 遵循通用 Web 标准，不追求领域格式兼容
遵循 GFM + YAML Front Matter 标准，借鉴 ADR 的元数据格式风格。
