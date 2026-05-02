# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Harness Creator** — 一套将**工程方法论**转化为 **Agent 可用工具**的方法论整合与抽象平台。

### 核心定位（来自项目拥有者）

> Harness Creator 是一套工具，它的**输入**可以是已有的工程规范，以及基于不同的工程规范产生的各种输出物（比如产品设计文档、交互原型）；它的**核心**是对软件工程不同环节的**方法论的高度整合和抽象**；它的**输出**是针对不同的 coding / UX设计 / 测试执行等 agent 的、**可持续监控和迭代**（因为 agent 和模型都在变化）的一套可用落地工具（skills、plugins 等，具体要看不同 agent 的工作模式）。

### 第二定位：技术学习与调研平台

Harness Creator 同时也是一个** Harness 工程所需各领域技术的学习和调研平台**。在构建 Harness 的过程中，需要系统性地探索和研究多个技术领域：

- **LLM / AI 基础设施层**：多厂商 API 格式、协议转换、统一适配器、Token 管理、成本优化
- **Agent 框架层**：各类 Agent 开发平台的架构模式、工具生态、扩展机制（Skills/MCP/Plugins/Extensions）
- **方法论抽象层**：软件工程各环节规范的结构化表示、知识图谱构建、版本化管理
- **编译/转换层**：MDL（Methodology Description Language）设计、跨框架格式编译、模板引擎
- **质量与迭代层**：Skill 效果评估、A/B 测试、持续监控、自动化回归

这些领域的调研成果会沉淀为项目文档和参考材料，为后续的 Harness 实现提供技术基础。

### 关键特征

- **方法论驱动**：不是从零发明任务，而是将已有工程方法论编码为 Agent 可消费的形式
- **多 Agent 目标**：产出物面向不同类型的 Agent（编程 Agent、UX 设计 Agent、测试 Agent 等），不绑定单一框架
- **持续迭代**：Agent 和模型在快速演进，Harness 产出的工具必须可持续监控和迭代
- **跨环节覆盖**：围绕 SDLC 全链路（需求 → 设计 → 交互 → 技术方案 → 编码 → 测试 → 部署）
- **技术调研先行**：在实现之前先系统性研究各领域技术现状，避免重复造轮子

## 核心概念

| 概念 | 定义 |
|------|------|
| **Harness（工程套件）**：对某个工程环节方法论的完整封装，包含该环节的规范、规则、工作流和质量标准，使 Agent 能在该环节中高效可靠地执行任务 |
| **Skill（技能）**：Harness 中的可复用能力单元，对应具体操作或跨环节能力，是 Agent 直接消费的最小粒度交付物 |
| **方法论抽象（Methodology Abstraction）**：从工程规范/文档/最佳实践中提炼出的结构化知识表示，是 Harness 的输入源 |

## 项目文档索引

| 文档 | 内容 | 状态 |
|------|------|------|
| [idea-raw.md](docs/idea-raw.md) | **项目核心想法（项目拥有者原始表述，最高优先级）** | 活跃 |
| [questions-ai-me.md](docs/questions-ai-me.md) | **产品探讨问答记录（所有产品方向的讨论都记录在此文件）** | 活跃 |
| [API 格式对比报告](docs/api-format-comparison-report.md) | 5 大 LLM 厂商 API 格式差异分析 | v1 |
| [Harness 架构设计 v0.1.0](docs/harness-architecture-v0.1.0) | 初版架构设计（**注意：可能存在方向偏差，需基于 idea-raw.md 对齐**） | 待修订 |
| [AI Agent 开发平台调研](AI-Agent-Development-Platform-Research.md) | 12 个 AI Agent 平台调研（Dify/MetaGPT/OpenHands/Cline 等） | 参考 |
| [MetaGPT vs OpenHands 深度拆解](MetaGPT-OpenHands-Deep-Analysis.md) | 两大框架源码级架构分析 | 参考 |
| [Model Integration 调研](docs/model-integration-research.md) | 传统软件+LLM混合架构的 Model 集成层（MIL）完整分析 | v1 |
| [项目 Roadmap](docs/roadmap.md) | **全局进度追踪、待办事项、里程碑时间线** | 活跃 |
| [软件工程流程规范](docs/00-软件工程标准流程规范/讨论日志-阶段0和1.md) | SDLC 10 阶段完整确认（立项→维护迭代） | ✅ 已确认 |
| [MDL 形态提案](docs/mdl-form-proposal.md) | Methodology Description Language 格式定义 v0.1 | v1 |
| [行业设计标准分析](docs/industry-design-standards-analysis.md) | M3/AntD/HIG 三大设计系统结构化拆解 | v1 |
| [Superpowers 深度分析](docs/superpowers/deep-analysis-v5.0.7.md) | Claude Code 官方插件 14 技能逐行分析 + 11 项缺陷 | v1 |

## 已完成的研究与产出

### LLM API 层
- 5 家主流厂商（OpenAI/Claude/DeepSeek/Qwen/Kimi）API 格式完整对比
- Claude Code Router 协议转换层实战分析
- 统一 LLM 适配器架构设计（参考 CCR 实现）

### Agent 框架层
- 12 个 AI Agent 开发平台调研（按 Star 数排序）
- MetaGPT vs OpenHands 深度技术拆解（架构/源码/设计模式）
- 编程 Agent 框架差异分析（Claude Code / Codex / Cursor / Cline）
- Superpowers v5.0.7 深度分析（14 技能 + 11 项缺陷 + 定制建议）
- GSD 2 深度研究（Context Engineering / Auto Mode / Dispatch Rules）

### Model Integration 层
- 传统软件 + LLM 混合架构的 MIL（Model Integration Layer）完整分析
- 6 大子系统：调用网关 / Prompt 管理 / 上下文组装 / 响应处理 / 运行时保障 / 可观测性
- Harness Creator 场景映射 + MVP 最小集合 + 实施路线图

### 方法论抽象层
- MDL（Methodology Description Language）形态定义 v0.1（5 项决策定稿）
- 行业设计标准结构化拆解（M3/AntD/HIG → 16 类方法论要素 → 4 层表达模型）
- 翻译机 3.0 交互规范分析（2 份独立报告，~70% 自动提取率验证）
- 软件工程标准流程规范（SDLC 10 阶段全部确认）

### 已实现代码
- Phase 1 MDL 引擎：数据模型 / 解析器 / 渲染器 / 校验器（30/30 测试通过）
- 首个真实 MDL 实例：tile-component-spec.mdl.md（磁贴样式规范）
## 项目约定

### 对话归档规范

**判断对话重要的依据1**：判断用户提示词里是否包含【重要】标记
**判断对话重要的依据2**：判断用户提示词长度是否>30字，大于30字直接认为属于重要对话
**每次重要对话会话结束时，将完整对话内容保存到 `logs-important/` 目录。**
规则：
- 按日期分文件：`YYYY-MM-DD-conversation.md`
- 原封不动保存 用户 与 AI 的所有实质性对话内容（**含 AskUserQuestion 的选择性回复内容和用户 notes**）
- 从 Claude Code 会话 JSONL 日志中自动提取生成

- **idea-raw.md 是最高优先级参考**：所有架构和实现决策必须以此文件的核心定位为准
- 输出物以 Harness 和 Skill 为基本交付单元
- 中文为主要工作语言，代码注释和文档优先使用中文
- 探索性讨论鼓励发散，但结论性产出需经确认后写入文档
