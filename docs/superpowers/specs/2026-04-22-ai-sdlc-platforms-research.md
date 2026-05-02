# GitHub AI 全链路开发平台 Top 10 深度调研报告

> 调研时间：2026年4月22日
> 调研方向：AI 驱动的全链路/多阶段软件开发平台
> 排序维度：社区热度 (60%) + 可借鉴性 (40%)
> 输出深度：深度拆解（含架构、源码、设计模式、Harness 映射）

---

## 一、Top 10 总览

| 排名 | 项目 | Stars | 核心定位 | SDLC 覆盖 | 可借鉴度 |
|:----:|------|:-----:|----------|:---------:|:--------:|
| 1 | **Dify** | ~138k | LLM 应用工作流开发平台 | ★★★★☆ | ★★★★★ |
| 2 | **n8n** | ~185k+ | 工作流自动化 + AI 编排平台 | ★★★☆☆ | ★★★★☆ |
| 3 | **Open WebUI** | ~100k+ | 自托管 AI 平台（Pipelines + RAG） | ★★★☆☆ | ★★★★☆ |
| 4 | **MetaGPT** | ~44k | 多智能体软件研发框架（SDLC 原生） | ★★★★★ | ★★★★★ |
| 5 | **AutoGen** (Microsoft) | ~45k+ | 多 Agent 对话式协作框架 | ★★★★☆ | ★★★★☆ |
| 6 | **LangGraph** | ~20k+ | 有状态 Agent 图编排框架 | ★★★☆☆ | ★★★★★ |
| 7 | **LobeChat / LobeHub** | ~40k | MCP 插件生态 + Agent 协作平台 | ★★★☆☆ | ★★★★☆ |
| 8 | **Bolt.new / bolt.diy** | ~30k+ | 浏览器内 AI 全栈应用生成 | ★★★☆☆ | ★★★★☆ |
| 9 | **OpenHands** (原 OpenDevin) | ~36k-72k | 自主软件开发 Agent | ★★★★★ | ★★★★☆ |
| 10 | **Flowise** | ~35k+ | 可视化 AI 工作流构建器 | ★★★☆☆ | ★★★☆☆ |

---

## 二、逐项深度分析

---

### #1 Dify — LLM 应用工作流开发平台

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/langgenius/dify |
| **Stars** | ~138,000+（持续增长中） |
| **Forks** | ~21,600+ |
| **协议** | Dify Open Source License（基于 Apache 2.0） |
| **技术栈** | Python (Flask/FastAPI) + React/Next.js + PostgreSQL/Redis |
| **月提交量** | 3,200+ commits/month（极高活跃度） |

#### 核心定位

面向生产环境的 **AI Agent 工作流开发平台**。提供可视化画布编排 AI 应用，从 Prompt 工程到 RAG 到 Agent 再到生产部署的全链路覆盖。

#### 架构设计

```
┌──────────────────────────────────────────────────┐
│                  用户层                           │
│   Web UI │ REST API │ WebSocket (SSE Streaming)  │
├──────────────────────────────────────────────────┤
│               API 控制器层                        │
│   app/chat/workflow/knowledge/tool controllers    │
├──────────────────────────────────────────────────┤
│                核心业务层                         │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │ Workflow    │ │ Model        │ │ RAG       │  │
│  │ Engine ★    │ │ Runtime      │ │ Pipeline  │  │
│  │ (图引擎)     │ │ (统一模型抽象)│ │ (检索增强) │  │
│  └─────────────┘ └──────────────┘ └───────────┘  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐  │
│  │ Agent       │ │ Tools        │ │ Prompt    │  │
│  │ Orchestration│ │ System       │ │ Templates │  │
│  └─────────────┘ └──────────────┘ └───────────┘  │
├──────────────────────────────────────────────────┤
│              数据层 / 异步任务                     │
│  PostgreSQL │ Redis │ Celery │ Vector DB         │
└──────────────────────────────────────────────────┘
```

#### 源码关键模块

| 模块路径 | 职责 | Harness 映射 |
|----------|------|-------------|
| `api/core/workflow/graph_engine/` | **事件驱动 DAG 执行引擎** — 事件循环 + 拓扑排序 + 并行调度 | → Harness Orchestrator/Scheduler |
| `api/core/workflow/nodes/node_factory.py` | **节点工厂** — 字符串类型→具体类实例的映射注册表 | → Harness ActionRegistry + ActionFactory |
| `api/core/app/apps/` | **4 种应用类型执行器** — Chatbot/Agent/Workflow/Completion 的多态分发 | → Harness Task Type Dispatcher |
| `api/core/model_runtime/` | **统一模型运行时** — 50+ LLM Provider 的统一接口抽象 | → Harness AI Provider Adapter Layer |
| `api/core/tools/` | **工具系统** — ToolProvider 管理 + 声明式 YAML 配置 + 动态注册 | → Harness Skill/Plugin System |
| `api/extensions/` | **插件框架** — Tool/Model/Extension 三类插件，目录扫描自动加载 | → Harness Extension Framework |

#### 工作流引擎核心机制

Dify 的 GraphEngine 是其最具技术价值的模块：

1. **DSL 配置驱动**：工作流以 JSON DSL 存储，描述节点、边、变量关系
2. **图解析**：JSON DSL → 内存 DAG 结构（节点对象 + 有向边）
3. **拓扑排序**：Kahn 算法确定合法执行顺序
4. **事件循环**：主循环查找"入边已完成"的就绪节点，触发执行
5. **异步并行**：asyncio.gather() 并行执行无依赖节点
6. **变量池 (VariablePool)**：全局键值存储，节点通过 `${node_id.output}` 引用上游输出
7. **条件分支/循环/错误恢复**：If-Else 节点路由 + Iteration 节点 + 错误状态码检测

#### 最值得借鉴的设计模式

| # | 模式 | 说明 | 迁移建议 |
|---|------|------|---------|
| 1 | **节点工厂模式** | NODE_TYPE_MAPPING 字典 + Factory.create() | Harness 建立 ActionRegistry + ActionFactory |
| 2 | **事件驱动的 DAG 引擎** | 事件循环 + 拓扑排序 + 并行调度 | Harness Pipeline 从线性升级为 DAG 编排 |
| 3 | **声明式插件架构** | YAML 元数据 + 基类继承 + 目录扫描注册 | Harness Skill 采用声明式配置降低扩展门槛 |
| 4 | **统一模型运行时** | 统一 invoke/stream/tokens/count 接口 | Harness 多模型对接必须的抽象层 |
| 5 | **变量池数据总线** | 命名空间化全局键值存储 | Harness Step 间数据传递的核心机制 |
| 6 | **应用类型多态分发** | BaseAppRunner → 4 种子类 | Harness 不同 Task 类型的执行策略分发 |
| 7 | **RAG 管道可插拔** | 分块/向量化/检索/重排各环节 Strategy 可替换 | Harness 数据处理管道的策略模式参考 |

#### 与 Harness 套件的概念映射

| Dify 概念 | Harness 对应 | 关系说明 |
|-----------|-------------|---------|
| Workflow (工作流) | Pipeline / Job | DAG 结构的任务编排，直接对应 |
| Workflow Node (节点) | Step / Task | 原子执行单元 |
| Tool (工具) | Skill / Action | 可被调用的能力单元 |
| Tool Provider | Skill Bundle / Category | 相关能力的组织容器 |
| Application Type | Task Type / Executor Profile | 决定请求的处理策略 |
| GraphEngine | Orchestrator / Scheduler | 任务编排和调度核心 |
| Variable Pool | Shared State / Output Mapping | Step 间数据传递中介 |
| Plugin System | Extension Framework | 能力的可插拔扩展 |

---

### #2 n8n — 工作流自动化 + AI 编排平台

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/n8n-io/n8n |
| **Stars** | ~185,000+（GitHub 上最高的工作流类项目之一） |
| **Forks** | ~4,500+ |
| **协议** | Fair-code（源码可用，有商业使用限制） |
| **技术栈** | TypeScript (91.4%) + Vue.js + Node.js |
| **最新版本** | v2.17.3（2026.04.20），583 个 Release |

#### 核心定位

面向技术团队的**工作流自动化平台**，原生集成 LangChain/AI 能力，支持 400+ 第三方服务连接。一切皆节点的 DAG 编排体系。

#### 架构亮点

1. **Universal Node 抽象**：所有能力（HTTP 请求、数据库操作、AI 调用、代码执行）统一抽象为 "Node"，每个 Node 有 inputs/outputs/parameters 三个标准接口
2. **Cluster Node 分类法**：Node 按 Cluster 组织（Trigger/Action/AI/Code/Logic/Data 等），便于浏览和发现
3. **Expression 数据引用系统**：通过 `{{ $json.field }}` / `{{ $node["name"].json.output }}` 表达式在节点间引用数据，比硬编码字段映射灵活得多
4. **Sub-workflow 复用**：工作流可以调用其他工作流作为子流程，实现模块化复用
5. **原生 AI 集成**：LangChain Node、Vector Store Node、Embedding Node、LLM Chain Node 等一等 AI 专用节点
6. **400+ 集成节点**：覆盖主流 SaaS 服务、数据库、API、协议

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 迁移价值 |
|---|------|------|----------------|
| 1 | **Universal Node 抽象** | 一切皆节点，统一 I/O/P 接口 | Harness Skill 应采用统一接口规范 |
| 2 | **Expression 系统** | `{{ $json }}` 表达式语言实现灵活的数据引用 | Harness 变量引用语法的参考 |
| 3 | **Cluster 分类组织** | 节点按功能域分类，而非扁平列表 | Harness Skill 的分类组织方式 |
| 4 | **Sub-workflow 复用** | 工作流嵌套调用，模块化组合 | Harness Pipeline 的复合/嵌套能力 |
| 5 | **凭证分离管理** | Connection/Credential 独立于 Node 存储 | Harness 敏感信息管理的安全实践 |
| 6 | **Fair-code 商业模式** | 开源核心 + 商业增值，平衡社区与可持续性 | Harness 项目商业化可参考 |

#### 与 Harness 的映射

| n8n 概念 | Harness 对应 |
|----------|-------------|
| Node | Skill / Action |
| Workflow | Pipeline / Orchestration |
| Connection (凭证) | Credential / Auth Config |
| Expression `{{ $json }}` | Variable Reference Syntax |
| Cluster | Skill Category / Domain |
| Sub-workflow | Composite Pipeline / Nested Job |
| Execution History | Run Log / Audit Trail |

---

### #3 Open WebUI — 自托管 AI 平台

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/open-webui/open-webui |
| **Stars** | ~100,000+ |
| **协议** | Open WebUI License（基于 Apache 2.0） |
| **技术栈** | Python (后端) + React/Vue (前端) |
| **部署** | Docker/Kubernetes 一键部署，支持 GPU 加速 |

#### 核心定位

功能丰富、可扩展、用户友好的**自托管 AI 平台**，支持完全离线运行。内置 Pipelines 插件框架和 RAG 引擎。

#### 架构亮点

1. **Pipelines 插件框架**：可无缝扩展自定义逻辑和 Python 库，类似中间件管道
2. **RAG 引擎**：支持 9 种向量数据库（ChromaDB/Qdrant/Milvus/Pinecone 等）
3. **企业级功能**：RBAC 权限控制、LDAP/AD 集成、SCIM 2.0、SSO
4. **多媒体能力**：TTS/STT 语音对话、图像生成与编辑（DALL-E/Gemini/ComfyUI）、Web 搜索增强
5. **Ollama/OpenAI API 深度集成**：支持本地 LLM 运行

#### 最值得借鉴的设计

- **Pipelines 中间件模式**：请求/响应经过可配置的 Pipeline 链，每个 Pipeline 是独立的处理阶段 — 这与 Harness 的 Stage/Phase 概念高度一致
- **多后端模型适配**：Ollama/OpenAI 兼容接口 + 本地模型统一接入
- **功能模块化**：RAG/语音/图像/Web搜索 各作为独立模块可按需启用

#### Harness 映射要点

- Open WebUI 的 **Pipeline** 概念直接对应 Harness 的 **Stage/Phase**
- 其 **Function Calling** 扩展机制可作为 Harness Skill 接口设计的参考
- RBAC 权限模型适合 Harness 多租户/团队协作场景

---

### #4 MetaGPT — 多智能体软件研发框架（SDLC 原生）

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/geekan/MetaGPT |
| **Stars** | ~44,000+ |
| **协议** | MIT |
| **技术栈** | Python |
| **学术认可** | ICLR 2025 Oral（"Software Multi-Agent: Code=SOP(Team)"） |

#### 核心定位

**最接近 Harness 套件理念的开源项目**。MetaGPT 的核心理念是 **"Code = SOP(Team)"** — 将软件公司的标准作业程序（SOP）编码为多 Agent 协作流程，原生覆盖 SDLC 全链路。

#### 架构设计（核心亮点）

```
┌────────────────────────────────────────────────────┐
│                   MetaGPT 架构                       │
│                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ Product │  │Architect│  │Project  │  │Engineer│ │
│  │ Manager │  │         │  │Manager  │  │        │ │
│  │(需求分析)│  │(技术方案)│  │(任务分解)│  │(编码)  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───┬────┘ │
│       │            │            │           │      │
│       └────────────┴─────┬──────┴───────────┘      │
│                          ▼                          │
│                   ┌──────────────┐                  │
│                   │  Environment │                  │
│                   │ (消息总线/    │                  │
│                   │  共享记忆)    │                  │
│                   └──────────────┘                  │
│                          │                          │
│                   ┌──────▼──────┐                  │
│                   │    Team     │                  │
│                   │ (编排器/SOP) │                  │
│                   └─────────────┘                  │
└────────────────────────────────────────────────────┘
```

#### SDLC 角色体系（这是 MetaGPT 最独特的设计）

| 角色 | 对应 SDLC 阶段 | 输出物 |
|------|---------------|--------|
| **Product Manager (产品经理)** | 需求分析 | PRD（产品需求文档） |
| **Architect (架构师)** | 技术方案设计 | 系统设计文档 + API 设计 |
| **Project Manager (项目经理)** | 任务分解 | 项目计划 + 任务列表 |
| **Engineer (工程师)** | 编码 | 源代码 |
| **QA Engineer (测试工程师)** | 测试 | 测试用例 + 测试代码 |
| **Code Reviewer (审查者)** | 代码审查 | Review 反馈 |
| **Writer (文档工程师)** | 文档 | 技术文档 + 用户手册 |

#### 源码关键模块

| 模块 | 职责 | Harness 映射 |
|------|------|-------------|
| `metagpt/roles/` | **Role 定义** — 每个 SDLC 角色的行为逻辑（_think/_act/_observe/_react 生命周期） | → Harness Role/Skill 定义 |
| `metagpt/actions/` | **Action 实现** — 每个角色可执行的具体操作（写PRD/写代码/写测试等） | → Harness Action/Step |
| `metagpt/team.py` | **Team 编排器** — SOP 流水线定义、角色实例化、消息路由 | → Harness Orchestrator |
| `metagpt/environment.py` | **Environment** — 共享记忆、消息总线、资源管理 | → Harness Shared Context |
| `metagpt/schema/` | **Schema 定义** — PRD/SD/API Design 等结构化文档格式 | → Harness Artifact Schema |
| `metagpt/utils/common.py` | **通用工具** — Git 操作、文件读写、代码解析等 | → Harness Utility Layer |

#### 最值得借鉴的设计（对 Harness 项目价值最高）

| # | 设计 | 说明 | 迁移优先级 |
|---|------|------|----------|
| 1 | **SOP 即代码** | 将软件工程 SOP 编码为可执行的 Agent 协作流程 | **P0 — 核心理念直接复用** |
| 2 | **四层 Role 抽象** | Role(谁做) → Action(做什么) → Environment(在哪做) → Team(怎么编排) | **P0 — Harness 的核心抽象层次** |
| 3 | **结构化文档 Schema** | PRD/SystemDesign/Tasks 等都有严格的 Pydantic Schema 定义 | **P0 — Harness Artifact 的数据模型** |
| 4 | **消息传递流水线** | 角色间通过结构化 Message 通信，含发布/订阅/路由 | **P1 — Skill 间通信协议** |
| 5 | **状态机驱动的动作选择** | Role 内部通过状态机决定下一步动作 | **P1 — Skill 执行的状态管理** |
| 6 | **SDLC 验证流水线** | 每个阶段的产出物会被下游角色验证 | **P1 — Harness 质量门禁机制** |

#### 与 Harness 的概念映射（最完整的映射关系）

| MetaGPT 概念 | Harness 对应 | 映射强度 |
|-------------|-------------|---------|
| **Role（角色）** | **Skill Domain / Role Profile** | ★★★★★ 直接对应 |
| **Action（动作）** | **Skill / Action** | ★★★★★ 直接对应 |
| **Team（团队）** | **Pipeline / Orchestrator** | ★★★★★ 直接对应 |
| **Environment（环境）** | **Execution Context / Shared State** | ★★★★☆ 高度相似 |
| **SOP（标准作业程序）** | **Harness Template / Workflow Definition** | ★★★★★ 核心理念相同 |
| **Message（消息）** | **Inter-Skill Communication Protocol** | ★★★★☆ 需要适配 |
| **Schema（文档结构）** | **Artifact Specification** | ★★★★★ 直接复用思路 |
| **_think/_act/_observe** | **Skill Lifecycle Hooks** | ★★★★☆ 可借鉴生命周期模式 |

---

### #5 AutoGen (Microsoft) — 多 Agent 对话式协作框架

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/microsoft/autogen |
| **Stars** | ~45,000+ |
| **协议** | MIT |
| **出品方** | Microsoft Research |
| **注意** | 已进入维护模式（maintenance mode），推荐关注 AutoGen 0.4.x / Core API |

#### 核心定位

微软出品的**多智能体对话框架**。核心创新是 **Agent 之间通过自然语言"对话"来协作完成任务**，而非传统的函数调用。

#### 架构亮点

1. **对话式协作范式**：Agent 间的通信是结构化的对话（Conversation），包含 sender/receiver/content/context 元数据
2. **Agent 类型系统**：
   - `ConversableAgent` — 基础对话 Agent
   - `AssistantAgent` — AI 助手（LLM 驱动）
   - `UserProxyAgent` — 人类代理（执行代码/审批决策）
   - `GroupChatManager` — 群聊管理员（协调多 Agent 对话）
   - `CodeExecutor` — 代码执行沙箱（Docker/local）
3. **Human-in-the-Loop**：UserProxyAgent 可配置为自动执行或需人工审批
4. **工具使用 (Tool Use)**：支持 Function Calling 和 code_execution 两种工具调用方式
5. **多模态支持**：图像/音频等多模态消息传递

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 价值 |
|---|------|------|-------------|
| 1 | **对话协议** | 结构化的 Conversation 作为 Agent 间通信原语 | Skill 间通信协议设计的参考 |
| 2 | **AgentTool 层次化组合** | Agent 可以嵌套包含其他 Agent 作为工具 | Harness 复合 Skill 的设计模式 |
| 3 | **代码执行沙箱** | Docker 隔离的安全代码执行环境 | Harness 编码 Skill 的沙箱需求 |
| 4 | **GroupChat 编排** | 群聊模式下的多 Agent 协调策略 | Harness 多 Skill 并行协调方案 |

#### 注意事项

AutoGen 已进入维护模式，但其**对话式协作范式**和**Agent 抽象设计**仍具有很高的参考价值。建议关注其继任方向（如 AutoGen 0.4.x Core API）。

---

### #6 LangGraph — 有状态 Agent 图编排框架

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/langchain-ai/langgraph |
| **Stars** | ~20,000+（增长迅速） |
| **协议** | MIT |
| **出品方** | LangChain 官方 |
| **企业客户** | Klarna、Replit、Elastic 等 |

#### 核心定位

LangChain 团队出品的**有状态 Agent 编排框架**。将 Agent 工作流建模为**有向图（Graph）+ 状态（State）**，是构建生产级多步骤 AI Agent 的最佳框架之一。

#### 架构核心：Graph + State + HIL

```
┌──────────────────────────────────────────┐
│              LangGraph 核心               │
│                                          │
│  State (状态字典)                         │
│  ├── messages: list[Message]             │
│  ├── current_step: str                   │
│  ├── results: dict                       │
│  └── ... (自定义字段)                      │
│                                          │
│  Graph (有向图)                           │
│  ├── Nodes (节点 = 函数)                  │
│  │   ├── node_a(state) → new_state       │
│  │   ├── node_b(state) → new_state       │
│  │   └── node_c(state) → new_state       │
│  ├── Edges (边 = 条件路由)                │
│  │   ├── node_a → node_b (always)        │
│  │   ├── node_b → {node_c, node_end} (cond)│
│  │   └── node_c → END                    │
│  └── Conditional Edges (条件边)           │
│      └── lambda state: route_name         │
│                                          │
│  Human-in-the-Loop (人机协同)             │
│  ├── interrupt_before(node)               │
│  ├── interrupt_after(node)                │
│  └── Command(resume/value/update)         │
│                                          │
│  Checkpointer (持久化)                    │
│  ├── MemorySaver (内存)                   │
│  ├── PostgresSaver (PostgreSQL)          │
│  └── SqliteSaver (SQLite)                │
└──────────────────────────────────────────┘
```

#### 最值得借鉴的设计（对 Harness 工作流引擎价值最高）

| # | 设计 | 说明 | Harness 迁移价值 |
|---|------|------|----------------|
| 1 | **图编程范式** | 工作流 = 有向图 + 状态字典，节点是纯函数 state→state | **P0 — Harness 工作流引擎的理想基础模型** |
| 2 | **Stateful Execution** | 每个节点接收完整状态、返回状态更新，天然支持断点续传 | **P0 — Harness 长任务/中断恢复的基础** |
| 3 | **Conditional Edges** | Lambda 函数动态决定路由目标，比固定 if-else 更灵活 | **P1 — Harness 动态分支能力** |
| 4 | **Human-in-the-Loop** | interrupt_before/after + Command 恢复机制 | **P1 — Harness 人工审批节点** |
| 5 | **Checkpointer 持久化** | 状态自动序列化到存储，支持长时间运行任务的恢复 | **P1 — Harness 任务持久化** |
| 6 | **Subgraph 嵌套** | 图可以嵌套包含子图，实现模块化 | **P1 — Harness Pipeline 复合** |

#### 与 Harness 的映射

| LangGraph 概念 | Harness 对应 |
|---------------|-------------|
| **Graph** | Pipeline / Workflow Definition |
| **State** | Execution Context / Shared State |
| **Node (函数)** | Step / Action |
| **Edge** | Transition / Routing Rule |
| **Conditional Edge** | Dynamic Branch Condition |
| **Checkpointer** | State Persistence Layer |
| **interrupt_* + Command** | Approval Gate / Human Review |
| **Subgraph** | Nested Pipeline / Composite Skill |

---

### #7 LobeChat / LobeHub — MCP 插件生态 + Agent 平台

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/lobehub/lobe-chat |
| **Stars** | ~40,000+ |
| **协议** | LobeHub Community License |
| **技术栈** | Next.js (React) + TypeScript |

#### 核心定位

现代化、设计驱动的 **AI Chat/Agent 平台**。核心差异化在于 **MCP (Model Context Protocol) 插件生态** 和 **Agent Market（505+ Agent）**。

#### 架构亮点

1. **MCP 三层架构**：
   - **协议层**：MCP 标准兼容，标准化工具/资源/提示词发现
   - **市场层**：MCP Marketplace，一键安装社区插件
   - **运行时层**：Plugin Gateway 安全隔离执行
2. **Agent Market**：505+ 预配置 Agent，涵盖编程、写作、分析、创意等领域
3. **多模型支持**：OpenAI/Claude/Gemini/Ollama/本地模型等数十种
4. **Artifacts 支持**：实时渲染 HTML/SVG/文档等产物
5. **Chain of Thought 可视化**：推理过程透明展示

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 价值 |
|---|------|------|-------------|
| 1 | **MCP 兼容** | Skill 接口兼容 MCP 标准，可直接使用 MCP 生态 | **P0 — 打通生态的关键** |
| 2 | **Plugin Gateway** | 插件通过网关隔离执行，安全性好 | **P1 — Skill 沙箱执行** |
| 3 | **Agent-as-Configuration** | Agent 通过声明式配置定义，非硬编码 | **P1 — Harness Template 机制** |
| 4 | **市场生态** | 社区贡献 + 一键安装 + 评分评价 | **P2 — Harness 生态建设参考** |

---

### #8 Bolt.new / bolt.diy — 浏览器内 AI 全栈应用生成

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/stackblitz/bolt.new (商业版) / bolt.diy (开源版) |
| **Stars** | ~30,000+ |
| **协议** | MIT (bolt.diy) |
| **核心技术** | WebContainers（浏览器内 Node.js 运行时） |

#### 核心定位

**AI 驱动的浏览器内全栈 Web 应用开发环境**。基于 WebContainers 技术，AI 在浏览器中拥有对文件系统/Node 服务/包管理器/终端的完整控制权。

#### 架构亮点

1. **WebContainers 技术**：在浏览器中运行完整 Node.js 环境，无需后端服务器
2. **AI 完整控制权**：文件系统读写、npm 包安装、Node 服务启动、终端命令执行
3. **实时预览**：代码修改即时反映在预览窗口
4. **从对话到部署**：聊天过程中逐步生成完整应用，一键部署到生产环境
5. **bolt.diy 开源版本**：社区维护的开源实现，可自托管

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 价值 |
|---|------|------|-------------|
| 1 | **Tool-Use 驱动的环境控制** | AI 通过结构化工具调用控制开发环境 | **P0 — Harness 编码 Skill 的交互模式** |
| 2 | **实时预览反馈闭环** | 生成→预览→修改→再预览的快速迭代 | **P1 — Harness 产物的即时验证** |
| 3 | **"Conversation-as-Development"** | 自然语言对话即开发过程 | **P1 — Harness 的交互范式参考** |
| 4. | **权限分级模型** | 不同操作需要不同权限级别 | **P1 — Harness 安全模型** |

---

### #9 OpenHands (原 OpenDevin) — 自主软件开发 Agent

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/All-Hands-AI/OpenHands |
| **Stars** | ~36k-72k（快速增长中） |
| **协议** | MIT |
| **最新版本** | v1.6.0 |
| **SWE-Bench 得分** | 77.36% |
| **企业客户** | TikTok、Apple、NVIDIA 等 |

#### 核心定位

**自主软件开发 Agent** — 给定一个自然语言任务描述，OpenHands 能够自主完成：理解需求 → 编写代码 → 运行测试 → 修复 Bug → 提交代码的完整循环。

#### 架构核心：五层事件驱动架构

```
┌────────────────────────────────────────┐
│  EventStream (事件流)                    │
│  ← 所有组件间通信的总线                   │
├────────────────────────────────────────┤
│  AgentController (Agent 控制器)          │
│  ← 管理 Agent 生命周期和决策              │
├────────────────────────────────────────┤
│  Runtime (运行时)                        │
│  ← Docker / Local / Remote / Modal       │
├────────────────────────────────────────┤
│  LLM (大模型调用)                        │
│  ← 支持 30+ LLM Provider                │
├────────────────────────────────────────┤
│  Sandbox (沙箱)                          │
│  ← 安全隔离的代码执行环境                 │
└────────────────────────────────────────┘
```

#### CodeAct 范式（核心创新）

OpenHands 采用 **CodeAct** 范式：Agent 的每一步动作都是一段**可执行的脚本/代码块**，而非简单的文本回复或函数调用。

```python
# Agent.step() 核心流程:
# 1. init_state()     — 初始化状态
# 2. step()           — 主循环
# 3. _get_action_event() — LLM 生成动作（代码块/命令）
# 4. _execute_action_event() — 在沙箱中执行
# 5. 收集结果 → 更新状态 → 回到 step()
```

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 价值 |
|---|------|------|-------------|
| 1 | **CodeAct 脚本生成范式** | Agent 输出可执行代码而非纯文本 | **P0 — Harness 编码 Skill 的执行模式** |
| 2 | **_ActionBatch 并行执行** | 不可变批次三阶段生命周期（init/validate/commit） | **P1 — Harness 并行任务管理** |
| 3 | **Security by Design** | 沙箱隔离 + 权限控制 + 操作审计 | **P0 — Harness 安全基线** |
| 4 | **EventStream 总线** | 所有组件通过事件流松耦合通信 | **P1 — Harness 事件架构** |
| 5 | **Condensation 压缩** | 长对话历史压缩，控制上下文窗口 | **P1 — Harness 长任务上下文管理** |

---

### #10 Flowise — 可视化 AI 工作流构建器

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/FlowiseAI/Flowise |
| **Stars** | ~35,000+ |
| **协议** | Apache 2.0 |
| **技术栈** | Node.js (Express) + React + LangChain |

#### 核心定位

基于 **LangChain** 的**可视化拖拽式 AI Agent 流程构建器**。无需编码即可创建 LLM 应用链。

#### 架构亮点

1. **可视化画布 UI**：拖拽节点、连线、配置参数，前端生成 JSON DSL
2. **基于 LangChain 封装**：每个节点底层是对 LangChain Chain/Agent/Tool 的封装
3. **Monorepo 架构**：server/ui/components/api-documentation 清晰分离
4. **DAG 执行引擎**：后端根据画布配置构建并执行 LangChain 图
5. **丰富的预制节点**：Document Loader/Text Splitter/Embedding/Vector Store/LLM/Memory/Tool 等

#### 最值得借鉴的设计

| # | 设计 | 说明 | Harness 价值 |
|---|------|------|-------------|
| 1 | **可视化画布 + DAG 执行** | 前端画布编辑 → 后端 DAG 执行的两层分离 | **P1 — Harness UI 层参考** |
| 2. | **组件节点化** | 每个 AI 能力封装为独立可配置的节点 | **P1 — Harness Skill 的 UI 表示** |
| 3. | **LangChain 生态对接** | 利用成熟生态而非重复造轮子 | **P2 — 技术选型参考** |

---

## 三、跨项目综合分析与融合建议

### 3.1 三大架构流派对比

| 流派 | 代表项目 | 核心范式 | 适用场景 |
|------|---------|---------|---------|
| **工作流/DAG 编排派** | Dify、n8n、Flowise、LangGraph | 图/节点/边/状态 | 确定/半确定性的流程编排 |
| **多 Agent 协作派** | MetaGPT、AutoGen、OpenHands | 角色/对话/消息/环境 | 需要"角色扮演"的复杂协作 |
| **对话即开发派** | Bolt.new、LobeChat | 自然语言→代码→预览 | 交互式/迭代式的创作场景 |

### 3.2 对 Harness 套件的融合建议（按优先级排列）

#### P0 — 核心架构层（必须采纳）

```
┌─────────────────────────────────────────────────────┐
│              Harness 套件推荐架构融合                │
│                                                      │
│  引擎层:  LangGraph (Graph + State)                 │
│           ↓                                         │
│  编排层:  Dify (Event-Driven DAG + NodeFactory)     │
│           ↓                                         │
│  角色层:  MetaGPT (SOP + Role/Action Schema)        │
│           ↓                                         │
│  执行层:  OpenHands (CodeAct + Sandbox)             │
│           ↓                                         │
│  生态层:  LobeChat (MCP 兼容 + Plugin Gateway)      │
│           ↓                                         │
│  交互层:  Bolt.new (Conversation-as-Dev + Preview)  │
│                                                      │
│  基础设施: n8n (Expression + Universal Node 抽象)    │
└─────────────────────────────────────────────────────┘
```

**具体建议：**

1. **工作流引擎**：以 **LangGraph 的 Graph+State 模型**为基础，融入 **Dify 的事件驱动 DAG 引擎**和**节点工厂模式**
2. **SDLC 角色体系**：直接参考 **MetaGPT 的 Role/Action/Schema 四层抽象**，这是与 Harness 套件理念最匹配的设计
3. **Skill 执行模式**：采用 **OpenHands 的 CodeAct 范式**（输出可执行脚本）+ **沙箱隔离**
4. **扩展协议**：**兼容 MCP 标准**（参考 LobeChat），打通外部工具/数据源生态
5. **变量/数据系统**：参考 **n8n 的 Expression 系统** + **Dify 的 Variable Pool**

#### P1 — 重要能力层（强烈建议采纳）

- **Human-in-the-Loop**：来自 LangGraph 的 interrupt/Command 机制
- **状态持久化**：LangGraph Checkpointer 模式
- **消息/通信协议**：AutoGen 的结构化 Conversation 或 MetaGPT 的 Message 传递
- **可视化编排 UI**：Flowise 的画布 + Dify 的节点面板
- **安全模型**：OpenHands 的 Security by Design + LobeChat 的 Plugin Gateway

#### P2 — 增值体验层（可选采纳）

- **Agent 市场/模板市场**：LobeChat Agent Market 模式
- **实时预览反馈闭环**：Bolt.new 的即时预览
- **Fair-code 商业模式**：n8n 的可持续开源模式
- **长对话压缩**：OpenHands Condensation 机制

### 3.3 不建议直接迁移的设计

| 设计 | 来源 | 原因 | 替代建议 |
|------|------|------|---------|
| AutoGen 的纯对话协议 | AutoGen | 已进入维护模式；对话协议开销较大 | 改用结构化 Message + 类型系统 |
| Flowise 的 LangChain 强依赖 | Flowise | 绑定单一生态，灵活性不足 | 抽象为 Provider 模式，可切换后端 |
| n8n 的单体架构 | n8n | 规模大了之后扩展困难 | 采用微服务/模块化架构 |
| Dify 的重前端设计 | Dify | 前端占比过高，核心逻辑耦合在 UI | 前后端分离，核心引擎独立于 UI |

---

## 四、调研结论与行动建议

### 4.1 核心发现

1. **MetaGPT 是与 Harness 套件理念最接近的项目** — "SOP = Code" 的核心理念、SDLC 原生角色体系、结构化文档 Schema，几乎可以直接作为 Harness 的理论蓝图
2. **Dify 的工作流引擎是最成熟的工程实现** — 138k Stars、事件驱动 DAG、节点工厂、生产级验证，可作为 Harness 引擎层的工程参考
3. **LangGraph 的 Graph+State 模型是最优雅的抽象** — 纯函数节点 + 不可变状态更新 + 条件边，适合作为 Harness 工作流的数学模型
4. **MCP 正成为 AI 工具互操作的事实标准** — LobeChat 等项目已全面拥抱 MCP，Harness 应考虑兼容
5. **三大流派正在融合** — 工作流编排、多 Agent 协作、对话即开发的边界越来越模糊，Harness 可以取各家之长

### 4.2 对 Harness 套件研发的分阶段建议

| 阶段 | 重点 | 参考 |
|------|------|------|
| **Phase 1: 概念建模** | 定义 Harness/Skill/Role/Artifact 的数据模型和 Schema | MetaGPT Schema + Dify 节点类型 |
| **Phase 2: 引擎原型** | 实现 Graph+State 工作流引擎 + 节点工厂 + 变量池 | LangGraph + Dify GraphEngine |
| **Phase 3: SDLC Skill 集** | 实现需求/设计/编码/测试/部署各阶段的 Skill | MetaGPT Role/Action + OpenHands CodeAct |
| **Phase 4: 扩展生态** | MCP 兼容 + 插件系统 + 模板市场 | LobeChat MCP + n8n Expression |
| **Phase 5: 可视化与部署** | 画布编排 UI + 沙箱执行 + 一键部署 | Flowise UI + Bolt.new Preview + OpenHands Sandbox |

---

## 五、附录：所有项目 GitHub 地址汇总

| # | 项目 | GitHub |
|---|------|--------|
| 1 | Dify | https://github.com/langgenius/dify |
| 2 | n8n | https://github.com/n8n-io/n8n |
| 3 | Open WebUI | https://github.com/open-webui/open-webui |
| 4 | MetaGPT | https://github.com/geekan/MetaGPT |
| 5 | AutoGen | https://github.com/microsoft/autogen |
| 6 | LangGraph | https://github.com/langchain-ai/langgraph |
| 7 | LobeChat | https://github.com/lobehub/lobe-chat |
| 8 | Bolt.new / bolt.diy | https://github.com/stackblitz/bolt.new / https://github.com/stackblitz/bolt.diy |
| 9 | OpenHands | https://github.com/All-Hands-AI/OpenHands |
| 10 | Flowise | https://github.com/FlowiseAI/Flowise |

---

*报告完成时间：2026年4月22日*
*调研方法：Web Search + GitHub API + 源码分析 + 技术博客交叉验证*
