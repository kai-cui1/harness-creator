---
# === L1 元层 (Meta Layer) ===
mdl: "1.0"
name: "磁贴组件设计规范"
version: "0.1.0"
author: "黄林森（交互设计）"
date: "2018-XX-XX"
source:
  file: "翻译机3.0交互文档/磁贴样式规范（new）.html"
  product: "讯飞翻译机 3.0（代号「老男孩」）"
platform:
  os: "Android 8.1"
  screen: "480x800px"
  screen_axure: "240x400px"  # Axure 坐标系为实际像素的一半
  device: "讯飞翻译机 3.0"
target_agent: "claude-code-skill"
status: "draft"               # draft | review | published | deprecated
category: "component-spec"     # component-spec | interaction-flow | exception-pattern | design-principle
references: []
---

# 磁贴组件设计规范（Tile Component Specification）

> **来源**：讯飞翻译机 3.0 交互原型文档 — 磁贴样式规范（new）
> **MDL 版本**：1.0
> **转化日期**：2026-04-23

---

## 设计原则（L2 Principle Layer）

### 核心设计策略

本规范遵循翻译机 3.0 的三大设计策略：

| 策略 | 定义 | 在磁贴设计中的体现 |
|------|------|-------------------|
| **易学** | 遵循用户在手机端已形成的习惯，将无意识行为转化为可见之物 | 通过色块+logo+名称三重识别降低学习成本 |
| **高效** | 简化界面和操作流程，扩大展示区域及操作热区 | 固定尺寸减少选择负担，后台统一配置 |
| **愉悦** | 在基本功能满足的情况下增加更多用户关怀 | 每个元素都有明确的用户价值故事 |

### 适用范围

- 本规范适用于**翻译机 3.0 Home 页面**的应用入口磁贴
- 不适用于系统级 UI 元素（状态栏、导航栏、弹窗等）
- 不适用于其他产品形态的磁贴/卡片组件

### 行为假设

- 用户已有手机端操作心智模型（图标=应用、点击=打开）
- 用户通过**色块大小/颜色**辅助记忆功能位置
- 用户通过 **logo 形状**识别应用功能
- 用户通过**文字名称**精确确认应用功能

---

## 组件规格：磁贴 (Tile)（L3 Specification Layer）

### 基本信息

| 属性 | 值 |
|------|-----|
| 组件名 | Tile（磁贴 / 应用入口） |
| 类型 | 应用入口组件 |
| 父容器 | Home 页面网格布局 |
| 尺寸变体 | `wide`（宽磁贴）、`small`（小磁贴） |

### 结构化约束

```yaml
component:
  name: Tile

  variants:
    - name: wide
      description: "占据一行宽度（约屏幕宽度的 50%，即 Axure 坐标 240px）"
      aspect_ratio: "~2:1"
      contains_fixed: ["app_icon", "app_name"]
      contains_optional: ["dynamic_info"]  # 本期不实现

    - name: small
      description: "占据约四分之一屏幕宽度（约 Axure 坐标 120px）"
      aspect_ratio: "~1:1"
      contains_fixed: ["app_icon", "app_name"]
      contains_optional: []                # 小磁贴无动态信息

  fixed_fields:
    - field: app_icon
      type: image
      required: true
      description: "应用图标，固定尺寸（由 UI 设计师给出具体像素值）"
      visual_spec:
        color: "纯色（由 UI 给出具体色号）"
        size: "固定尺寸（由 UI 给出具体像素值）"
        position: "磁贴上方居中"
      rationale: "用户可以通过 logo 的形状来识别应用功能，快速打开应用"

    - field: app_name
      type: string
      required: true
      max_length: 4          # 中文字符数
      description: "应用名称，固定字号（由 UI 给出）"
      visual_spec:
        font_size: "固定（由 UI 给出）"
        alignment: "左对齐"
        color: "纯色（由 UI 给出具体色号）"
      rationale: "用户可以通过文字来识别应用功能，快速打开应用"

  optional_fields:
    - field: dynamic_info
      type: string
      required: false
      implementation_status: deferred   # ★ 本期不实现，延后到后续迭代
      description: "动态信息字段，用于展示语种、流量套餐等实时数据"
      examples:
        - "当前语种（如：中→英）"
        - "流量套餐余量"
      note: "仅做展示用途，不做交互入口（如不做语种切换入口）"

  constraints:                    # 排除性约束（"不做什么"）
    - rule: "不支持用户自定义尺寸"
      rationale: "只有 wide/small 两种，保证布局一致性"

    - rule: "不支持用户自定义位置顺序"
      rationale: "后台可配置上下架顺序，用户端不可调整"

    - rule: "不支持卸载"
      rationale: "预装应用，不可移除"

    - rule: "不承载通知/角标类运营信息"
      rationale: "保持界面简洁，避免信息过载"

    - rule: "不支持自定义背景图/壁纸（本期）"
      status: "future_low_priority"
      rationale: "后期可能会做基于地理位置或特定节日的动态壁纸更新，但优先级低"

  layout_rules:
    home_page:
      row_1: ["wide_tile_1", "wide_tile_2"]           # 第一行：2 个宽磁贴
      row_2_plus: ["small_tile × 4"]                  # 第二行起：每行 4 个小磁贴
      total_small_tiles: 8                            # 共 8 个小磁贴（2 行）
```

### 各功能磁贴规格表

| 功能 | 尺寸 | 背景 | APP 名称 | APP Logo | 动态信息 |
|------|------|------|----------|----------|---------|
| 拍照翻译 | `wide` | 固定纯色（待 UI 定） | √ | √ | 当前语种（`deferred`） |
| 全球上网 | `wide` | 固定纯色（待 UI 定） | √ | √ | 流量套餐（`deferred`） |
| 同声传译 | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |
| 录音翻译 | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |
| 设置 | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |
| 个人中心 | `small` | 固定纯色（待 UI 定） | √ | √ | 绑定状态（`deferred`） |
| 人工翻译 | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |
| 口语学习 | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |
| SOS | `small` | 固定纯色（待 UI 定） | √ | √ | ×（无） |

### 设计理由汇总（Rationale）

| 元素 | 设计故事 | 用户价值 |
|------|---------|---------|
| **背景色块** | 用户可以通过色块的大小或颜色来辅助记忆功能位置 | 快速定位 → 减少寻找时间 |
| **App Logo** | 用户可以通过 logo 的形状来识别应用功能 | 视觉识别 → 降低阅读成本 |
| **App 名称** | 用户可以通过文字来识别应用功能 | 精确确认 → 避免误操作 |
| **固定尺寸** | 只有 wide/small 两种变体 | 降低认知负荷 → 形成空间预期 |
| **固定位置** | 后台配置，用户不可调 | 保证一致性 → 每次看到相同的布局 |

---

## 实例标注说明（L4 Instance Layer）

### 各功能的特殊说明

| 编号 | 功能 | 特殊规则 |
|------|------|---------|
| 1 | 拍照翻译 | 动态信息 = 当前语种（仅展示，不做语种切换入口） |
| 2 | 全球上网 | 动态信息 = 当前 SIM 卡套餐余量（仅展示） |
| 3 | 其它应用（同声传译/录音翻译/设置等） | 固定信息仅为 icon + 应用名称；无动态信息 |

### 待定项清单

| 标记 | 内容 | 影响范围 | 建议 |
|------|------|---------|------|
| `(待 UI 定)` | 背景具体色号 | 所有 9 个磁贴 | 等 UI 设计师输出色板 |
| `(待 UI 定)` | icon 具体像素尺寸 | 所有 9 个磁贴 | 等 UI 设计师输出规格 |
| `(待 UI 定)` | 名称具体字号 | 所有 9 个磁贴 | 等 UI 设计师输出字体规范 |
| `(本期不实现)` | 动态信息字段 | 拍照翻译/全球上网/个人中心 | v0.2 迭代实现 |
| `(优先级低)` | 动态壁纸更新 | 全部磁贴 | 远期规划，暂不纳入 |

### 变更记录

| 序号 | 时间 | 需求名 | 修订内容 | 提出人 |
|------|------|--------|---------|--------|
| 1 | 2018-XX-XX | 磁贴规范初版 | 新增磁贴组件完整规范（总则 + 规格表 + 设计理由） | 黄林森 |
| 2 | — | MDL 转化 | 从 Axure HTML 转化为 MDL v1.0 格式 | Harness Creator |

---

## 审查检查清单（供 Agent 使用）

当使用本规范审查或生成磁贴相关 UI 时，请逐条检查：

### 必须满足（Must）

- [ ] 磁贴尺寸只能是 `wide` 或 `small`，不存在第三种尺寸
- [ ] 每个磁贴必须包含 app_icon 和 app_name 两个固定字段
- [ ] 用户端不可自定义磁贴的尺寸、位置、顺序
- [ ] 磁贴不可被卸载
- [ ] 磁贴上不显示通知数、角标等运营信息
- [ ] wide 磁贴占据整行宽度（~50% 屏幕宽），small 磁贴占据 ~25% 屏幕宽
- [ ] Home 页第一行是 2 个 wide 磁贴，之后每行 4 个 small 磁贴

### 应该满足（Should）

- [ ] 不同功能的磁贴使用不同的背景色（辅助记忆）
- [ ] app_icon 位于磁贴上半部分居中
- [ ] app_name 位于 icon 下方，左对齐
- [ ] 背景色为纯色（非渐变、非图片）

### 不应该做（Must Not）

- [ ] 不应添加除 icon/name/dynamic_info 之外的额外信息
- [ ] 不应允许用户拖拽排序磁贴
- [ ] 不应在磁贴上叠加 badge/通知数
- [ ] 不应使用非纯色背景（本期）
