# Harness Creator — 项目 Roadmap

> 最后更新：2026-04-30
> 状态图例：✅ 已完成 | 🔄 进行中 | ⏳ 待开始 | 🚫 搁置/待修订

---

## 一、已完成工作总览

### Phase 0：调研与研究（2026-04-22 ~ 2026-04-30）

| # | 工作项 | 产出物 | 状态 | 日期 |
|---|--------|--------|------|------|
| 0.1 | AI Agent 开发平台调研（12 平台） | `AI-Agent-Development-Platform-Research.md` + `docs/superpowers/specs/2026-04-22-ai-sdlc-platforms-research.md` | ✅ | 04-22 |
| 0.2 | MetaGPT vs OpenHands 深度拆解 | `MetaGPT-OpenHands-Deep-Analysis.md`（69KB，源码级） | ✅ | 04-22 |
| 0.3 | LLM API 格式对比（5 厂商） | `docs/api-format-comparison-report.md`（1294 行） | ✅ | 04-22 |
| 0.4 | 架构设计 v0.1.0（初稿） | `docs/harness-architecture-v0.1.0.md` | 🚫 待修订 | 04-22 |
| 0.5 | 项目核心定位声明 | `docs/idea-raw.md`（最高优先级参考） | ✅ 活跃 | 04-22 |
| 0.6 | 产品探讨 Q&A（5 轮） | `docs/questions-ai-me.md`（持续更新） | ✅ 活跃 | 04-22~27 |
| 0.7 | 翻译机 3.0 交互规范分析（2 份） | `docs/analysis-fanyi3.0-interaction-spec.md` + `docs/superpowers/specs/2026-04-22-translator3-ixd-analysis.md` | ✅ | 04-22 |
| 0.8 | 行业设计标准分析（M3/AntD/HIG） | `docs/industry-design-standards-analysis.md` | ✅ | 04-23 |
| 0.9 | MDL 形态定义 v0.1 | `docs/mdl-form-proposal.md`（5 项决策定稿） | ✅ | 04-23 |
| 0.10 | Model Integration Layer 调研 | `docs/model-integration-research.md`（468 行，6 大子系统） | ✅ | 04-27 |
| 0.11 | Superpowers v5.0.7 深度分析 | `docs/superpowers/deep-analysis-v5.0.7.md`（14 技能逐行，11 项缺陷） | ✅ | 04-29 |
| 0.12 | GSD 2 深度研究 | `docs/superpowers/specs/2026-04-22-gsd2-deep-research.md`（911 行） | ✅ | 04-22 |
| 0.13 | 软件工程标准流程规范（10 阶段） | `docs/00-软件工程标准流程规范/讨论日志-阶段0和1.md` | ✅ | 04-30 |

### Phase 1：MDL 引擎基础层（2026-04-23）

| # | 工作项 | 产出物 | 状态 | 日期 |
|---|--------|--------|------|------|
| 1.1 | MDL 数据模型（Pydantic） | `src/harness_creator/mdl/models.py` | ✅ | 04-23 |
| 1.2 | MDL 解析器 | `src/harness_creator/mdl/parser.py` | ✅ | 04-23 |
| 1.3 | MDL 渲染器（Round-trip） | `src/harness_creator/mdl/renderer.py` | ✅ | 04-23 |
| 1.4 | MDL 校验器 | `src/harness_creator/mdl/validator.py` | ✅ | 04-23 |
| 1.5 | 单元测试（4 模块全覆盖） | `tests/test_mdl_*.py`（30/30 通过） | ✅ | 04-23 |
| 1.6 | 首个 MDL 实例（磁贴规范） | `harnesses/tile-component-spec.mdl.md` | ✅ draft | 04-23 |

### 经验沉淀（01-项目心得/）

| # | 文件 | 核心内容 | 状态 |
|---|------|----------|------|
| E.1 | `我和AI一次关于项目流程的讨论.md` | 发现 roadmap 与 spec 脱节 → 触发流程规范制定 | ✅ |
| E.2 | `架构设计.md` | 架构设计不能替代详细设计 | ✅ |
| E.3 | `详细设计.md` | 详细设计是必须阶段，AI 不允许跨过 | ✅ |
| E.4 | `数据库设计.md` | 每张表需说明目的、与领域模型关系；需全局团队规范 | ✅ |
| E.5 | `关于superpowers的问题和优化.md` | brainstorming 缺 plan 自查；E2E 测试框架 implementation plan 示例 | ✅ |
| E.6 | `关于代码注释.md` | 待补充 | ⏳ |
| E.7 | `关于评审与review.md` | 待补充 | ⏳ |
| E.8 | `缺陷修复与系统调整.md` | 待补充 | ⏳ |
| E.9 | `目录约束优先.md` | 待补充 | ⏳ |

---

## 二、待办事项（按优先级排序）

### P0 — 紧急

| # | 待办 | 描述 | 依赖 | 预期产出 |
|---|------|------|------|----------|
| **T001** | **编写 skill:start-ai-project** | 在新 AI 协作项目中指导 AI 建立基础规范：目录规范、AI-用户行为规范（含重要对话记录）、启用 skill 清单及理由、版本管理配置等。任何项目启动时先运行此 skill | 无 | 可执行的 Skill 文件 |
| **T001b** | **编写 skill:write-prd** | 创建产品原型 PRD 编写 Skill：指导 Agent 按照结构化模板输出完整的产品需求文档，覆盖功能描述、交互逻辑、数据结构、异常流程、验收标准等核心章节。面向 UX 设计 Agent / 产品分析场景 | 无 | 可执行的 Skill 文件 + PRD 模板 |

### P1 — 高优（推进 MVP）

| # | 待办 | 描述 | 依赖 | 预期产出 |
|---|------|------|------|----------|
| T002 | 修订架构设计 v0.1.0→v0.2.0 | 基于 idea-raw.md + 10 阶段流程规范 + Superpowers 分析结论，对架构进行方向对齐和修订 | T001（参考 skill 格式） | `docs/harness-architecture-v0.2.0.md` |
| T003 | 细化流程规范的开放问题 | 小项目轻量模式、准入准出标准、阶段间迭代模式、AI 切入点、参考资料对齐 | 无 | 讨论日志更新 |
| T004 | 设计首个 Coding Agent Harness | 以阶段 7（编码实现）为切入点，将编码规范/Code Review/Git 工作流/注释规范 编码为 Harness/Skill | T002 | Harness 定义 + Skill 产物 |
| T005 | MDL → Claude Code Skill 编译器原型 | 实现 MDL 文件到 Claude Code Skill 格式的编译转换 | T002, T004 | 编译器模块 |

### P2 — 中优（完善能力）

| # | 待办 | 描述 | 依赖 | 预期产出 |
|---|------|------|------|----------|
| T006 | Phase 2：Axure HTML 分析器 | 从 Axure 导出的 HTML 原型中自动提取方法论要素（当前 ~70% 自动 / ~30% 人确认） | T004 | HTML 解析模块 |
| T007 | MIL 轻量实现 | 基于 model-integration-research.md 的 MVP 子集 | T005 | MIL 模块 |
| T008 | 补充项目心得（4 篇未完成） | 代码注释/评审 review/缺陷修复/目录约束 | 无 | `01-项目心得/` 下 4 篇文档 |
| T009 | 多版本 Skill 管理 | 同一方法论不同输入源/严格程度/团队偏好 → 多版本 Skill | T004 | 版本管理机制 |

### P3 — 远期（扩展方向）

| # | 待办 | 描述 | 依赖 | 预期产出 |
|---|------|------|------|----------|
| T010 | UX 设计 Agent 支持 | 扩展到 Figma AI / LLM 原型生成场景 | T004+ | UX 方向 Harness |
| T011 | 测试 Agent 支持 | 扩展到 SWE-agent / OpenHands 代码执行 | T004+ | 测试方向 Harness |
| T012 | 更多 SDLC 环节覆盖 | 需求→设计→编码→测试→部署 全链路 | T004+ | 完整 SDLC 套件 |
| T013 | 持续监控与迭代平台 | Skill 效果评估/A/B 测试/自动化回归 | T009+ | 监控平台 |
| T014 | 跨框架编译器后端 | 支持 Codex/Cursor/Cline/MetaGPT 等 | T005 | 多后端编译器 |

---

## 三、技术债务 & 待修订

| # | 问题 | 说明 | 建议 |
|---|------|------|------|
| D1 | 架构 v0.1.0 方向偏差 | 基于"任务编排器"理解编写，已纠正为"方法论编译器" | T002 修订 |
| D2 | roadmap.md 曾长期为空 | 缺少全局进度追踪 | ✅ 本文档补齐 |
| D3 | 项目心得 4 篇未完成 | 代码注释/评审review/缺陷修复/目录约束 | T008 补充 |
| D4 | 无 Git 版本控制 | 项目尚未初始化 Git 仓库 | T001 中应包含 |
| D5 | CLAUDE.md 文档索引可能过期 | 新增文档后索引表未同步更新 | 定期检查 |

---

## 四、关键里程碑时间线

```
04-22  ┃ 项目启动 ┃ 大规模调研（API/Agent/架构/翻译机）
        ┃           ┃ idea-raw.md 核心定位 + Round 1 方向纠正
04-23  ┃ MDL 定稿  ┃ 行业标准分析 + MDL 形态 v0.1 + Phase 1 编码(30/30✅)
        ┃           ┃ 首个真实 MDL 实例（磁贴规范）
04-27  ┃ MIL 调研  ┃ Model Integration Layer 完整分析
04-29  ┃ SP 分析   ┃ Superpowers v5.0.7 深度分析（11 项缺陷）
04-30  ┃ 流程规范  ┃ 软件 工程 10 阶段全部确认 + Roadmap 建立
------  ┃-----------┃------------------------------------------------
 TBD   ┃ P0 紧急  ┃ T001: start-ai-project + T001b: write-prd ← 当前焦点
 TBD   ┃ P1 高优  ┃ 架构修订 → 首个 Coding Harness → MDL 编译器
 TBD   ┃ P2 中优  ┃ Axure 分析器 → MIL 实现 → 心得补充 → 版本管理
 TBD   ┃ P3 远期  ┃ UX/测试扩展 → 全链路覆盖 → 监控平台 → 跨框架
```

---

## 五、T001 详情：skill:start-ai-project

**优先级**：P0 紧急
**动机**：每次启动新的 AI 协作项目时，都需要重复建立一套基础规范。将这个过程固化为 Skill，确保：
- 项目结构一致且规范
- AI 与用户的协作行为有明确约定
- 所需工具/skill 一键配置到位
- 版本管理等基础设施就绪

### Skill 应覆盖的内容域

| # | 内容域 | 具体条目 |
|---|--------|----------|
| 1 | **项目目录规范** | 推荐目录结构（docs/src/tests/logs 等）、命名约定、文件组织原则 |
| 2 | **AI-用户行为规范** | 重要对话判定规则（如长度>30字或含【重要】标记）、对话归档机制（logs-important/ 按日期分文件）、CLAUDE.md 维护约定 |
| 3 | **Skill 启用清单** | 列出推荐启用的 skill 及每个 skill 的使用理由（何时用、解决什么问题） |
| 4 | **版本管理配置** | 是否使用 Git、.gitignore 推荐、分支策略建议、commit 规范 |
| 5 | **项目配置初始化** | settings.json / settings.local.json 基础配置、环境变量、权限设置 |
| 6 | **项目元信息** | 项目名称、描述、目标、初始 MEMORY.md 建立 |

### 使用方式

```
新项目启动时执行：/start-ai-project
或：请运行 start-ai-project skill 来初始化本项目
```

### 预期输出物

- `CLAUDE.md`（项目指引文件）
- `MEMORY.md`（记忆索引）
- 目录结构（按规范创建）
- Git 初始化（如选择）
- 对话归档机制就绪

---

## 五b、T001b 详情：skill:write-prd

**优先级**：P0 紧急
**动机**：产品原型阶段需要输出结构化的 PRD（产品需求文档），但不同团队/项目的 PRD 格式差异大、质量参差不齐。将 PRD 编写过程固化为 Skill，确保：
- PRD 结构完整且规范（不遗漏关键章节）
- 交互逻辑描述清晰，可供 UX 设计 Agent 直接消费
- 数据结构定义明确，为后续技术方案提供输入
- 验收标准可量化，支撑测试 Agent 执行验证

### Skill 应覆盖的内容域

| # | 内容域 | 具体条目 |
|---|--------|----------|
| 1 | **PRD 模板结构** | 产品概述 / 用户角色与场景 / 功能需求清单 / 交互流程说明 / 页面/组件结构 / 数据模型 / 异常流程处理 / 非功能需求 / 验收标准 / 附录 |
| 2 | **交互逻辑描述规范** | 状态机表达、用户操作路径、页面跳转规则、反馈机制（loading/成功/错误/空状态） |
| 3 | **数据结构定义** | 实体关系、字段定义（类型/必填/默认值/约束）、API 接口契约雏形 |
| 4 | **异常与边界场景** | 空数据/网络异常/权限不足/并发冲突/数据校验失败等场景的处理策略 |
| 5 | **验收标准模板** | 每个功能点的 Given-When-Then 格式验收条件，可直接映射到测试用例 |
| 6 | **与下游衔接** | 标注哪些章节供 UX 设计 Agent 参考、哪些供 Coding Agent 参考、哪些供测试 Agent 参考 |

### 使用方式

```
产品原型阶段执行：/write-prd <产品名称>
或：请运行 write-prd skill 来编写 [XXX] 的 PRD
```

### 预期输出物

- 可执行的 Skill 文件（`skill:write-prd`）
- PRD 模板文件（含各章节的填写指引和示例）
- 与 SDLC 阶段 3（产品设计）的对齐说明
