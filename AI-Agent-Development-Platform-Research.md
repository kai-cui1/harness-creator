# GitHub 开源 AI Agent 开发平台调研报告

> 调研日期：2026年4月22日
> 调研范围：覆盖软件开发生命周期（SDLC：需求 -> 设计 -> 编码 -> 测试 -> 部署）多阶段的 AI Agent 开发平台
> 排序方式：按 GitHub Star 数从高到低

---

## 总览对比表

| 排名 | 项目名称 | Star 数（约） | 定位 | 技术栈 | 开源协议 | SDLC 覆盖度 |
|------|---------|-------------|------|--------|---------|------------|
| 1 | Dify | 100k+ | 生产级 Agent 工作流开发平台 | Python / TypeScript / React | Dify OSS (Apache 2.0 变体) | ★★★★☆ |
| 2 | LangGraph | 50k+ | 有状态语言 Agent 图编排框架 | Python / JavaScript | Apache 2.0 | ★★★☆☆ |
| 3 | AutoGen (Microsoft) | 45k+ | 多智能体 AI 应用编程框架 | Python / .NET | MIT | ★★★☆☆ |
| 4 | MetaGPT | 43k+ | 多智能体框架：首个 AI 软件公司 | Python 3.9+ | MIT | ★★★★★ |
| 5 | OpenHands (原 OpenDevin) | 36k+ | 软件开发 Agent 平台 | Python / TypeScript | MIT | ★★★★★ |
| 6 | CrewAI | 30k+ | 自主 AI Agent 编排框架 | Python | MIT | ★★★☆☆ |
| 7 | Aider | 32k+ | 终端 AI 结对编程工具 | Python | Apache 2.0 | ★★★☆☆ |
| 8 | Cline | 35k+ | IDE 内自主编码 Agent | TypeScript | Apache 2.0 | ★★★★☆ |
| 9 | SWE-agent | 29k+ | 自动化 Issue 修复 Agent | Python | MIT | ★★★☆☆ |
| 10 | AutoDev | 8k+ | IntelliJ AI 驱动编程助手 | Kotlin (IntelliJ Plugin) | MPL 2.0 | ★★★★★ |
| 11 | Devika | 28k+ | 开源 Agentic 软件工程师 | Python + Node.js + Bun | MIT | ★★★★☆ |
| 12 | AI-SDLC Framework | 较新 | AI 增强的全生命周期编排器 | TypeScript / Node.js | Apache 2.0 | ★★★★★ |

---

## 详细分析

### 1. Dify — 生产级 Agent 工作流开发平台

- **GitHub**: https://github.com/langgenius/dify
- **Star 数**: 约 100,000+
- **一句话定位**: 面向生产环境的 Agent 工作流开发平台，支持可视化编排和 RAG 管线
- **核心特性**:
  - 可视化工作流画布（Workflow Canvas），拖拽式构建复杂 AI 工作流
  - 支持 100+ 大语言模型的全面模型接入（OpenAI、Claude、Gemini、本地模型等）
  - 内置 Prompt IDE，提供调试和版本管理能力
  - 完整的 RAG 管线：文档加载、分块、向量化、检索一站式处理
  - Agent 能力：50+ 内置工具（搜索、代码执行、API 调用等）
  - LLMOps 监控：日志追踪、注解评估、运营监控
  - Backend-as-a-Service API：可快速集成到自有应用中
- **技术栈**: Python 后端、TypeScript/React 前端、PostgreSQL/Redis/Weaviate
- **开源状态**: Dify Open Source License（基于 Apache 2.0 带附加条件）
- **部署方式**: Docker Compose、Kubernetes（多 Helm Chart）、Terraform、AWS CDK、阿里云
- **活跃度**: 极高。社区活跃（Discord），贡献者众多，20+ 语言 README
- **SDLC 覆盖**: 主要覆盖工作流编排层，可作为上层平台整合各阶段能力；自身不直接实现编码/测试，但通过 Agent + 工具链可间接覆盖

---

### 2. LangGraph — 有状态语言 Agent 图编排框架

- **GitHub**: https://github.com/langchain-ai/langgraph
- **Star 数**: 约 50,000+
- **一句话定位**: 用于构建有状态、长期运行 Agent 的底层图编排框架
- **核心特性**:
  - **持久化执行**：Agent 可在故障后恢复，支持长时间运行任务
  - **人机协作（Human-in-the-loop）**：可在任意执行点检查和修改 Agent 状态
  - **综合记忆系统**：短期工作记忆 + 长期跨会话持久记忆
  - **LangSmith 调试**：深度可视化 Agent 行为，追踪执行路径和状态转换
  - **生产级部署**：专为有状态长期运行工作流设计的可扩展基础设施
  - 支持循环（cycles）和分支（branching）的工作流图定义
  - 子图（Subgraph）嵌套，支持复杂的多层级 Agent 编排
- **技术栈**: Python / JavaScript（双 SDK）、LangChain 生态集成
- **开源状态**: Apache 2.0
- **活跃度**: 高。LangChain 官方维护，Klarna、Replit、Elastic 等企业用户
- **SDLC 覆盖**: 作为通用 Agent 编排框架，可通过自定义节点覆盖任意 SDLC 阶段；本身是基础设施层，需配合具体 Agent 实现

---

### 3. AutoGen (Microsoft) — 多智能体 AI 应用编程框架

- **GitHub**: https://github.com/microsoft/autogen
- **Star 数**: 约 45,000+
- **一句话定位**: 微软出品的多智能体 AI 应用编程框架（已进入维护模式，推荐迁移至 Microsoft Agent Framework）
- **核心特性**:
  - 分层架构设计：Core API（消息传递/事件驱动）-> AgentChat API（快速原型）-> Extensions API（扩展能力）
  - **多智能体编排**：支持两 Agent 对话、群聊、AgentTool 嵌套等多种模式
  - **MCP Server 集成**：原生支持 Model Context Protocol，可接入 Playwright 等工具服务器
  - **AutoGen Studio**：无代码 GUI 界面，用于快速原型设计和演示多智能体工作流
  - **AutoGen Bench**：Agent 性能基准测试套件
  - **Magentic-One**：基于 AutoGen 构建的 SOTA 多智能体团队（网页浏览、代码执行、文件处理）
  - 跨语言支持：Python 和 .NET
- **技术栈**: Python 3.10+ / .NET、OpenAI/Azure OpenAI
- **开源状态**: MIT License
- **活跃度**: 中等偏下。**注意：AutoGen 已进入维护模式（Maintenance Mode）**，不再接收新功能，由社区维护。新项目建议使用 Microsoft Agent Framework (MAF)
- **SDLC 覆盖**: 通过多 Agent 协作模式可覆盖需求分析到代码生成多个阶段；Magentic-One 展示了端到端任务处理能力

---

### 4. MetaGPT — 多智能体框架：首个 AI 软件公司

- **GitHub**: https://github.com/geekan/MetaGPT
- **Star 数**: 约 43,000+
- **一句话定位**: 模拟软件公司角色分工的多智能体框架，输入一行需求输出完整软件产物
- **核心特性**:
  - **角色模拟**：产品经理（PM）、架构师（Architect）、项目经理（PM）、工程师（Engineer）等多角色协作
  - **端到端产出**：输入一行需求 -> 输出用户故事、需求文档、数据结构设计、API 设计、代码、文档
  - **SOP 驱动**：核心理念 `Code = SOP(Team)`，将标准化流程应用于 LLM 团队
  - **Data Interpreter**：内置数据分析师角色，支持数据分析任务
  - **全球知识库**：支持联网搜索获取最新信息辅助开发
  - 学术成果：AFlow 论文被 ICLR 2025 接收为 Oral（Top 1.8%，LLM Agent 类别 #2）
  - 商业化产品：MGX（MetaGPT X）自然语言编程产品（2025年2月发布）
- **技术栈**: Python 3.9+（不支持 3.12）、GPT-4 / Claude 系列
- **开源状态**: MIT License
- **活跃度**: 高。学术背景强（ICLR 2025 Oral），持续更新且有商业化进展
- **SDLC 覆盖**: ★★★★★ 全覆盖。从需求（PM 角色）-> 设计（架构师）-> 编码（工程师）-> 文档，天然覆盖完整 SDLC

---

### 5. OpenHands (原 OpenDevin) — 软件开发 Agent 平台

- **GitHub**: https://github.com/All-Hands-AI/OpenHands
- **Star 数**: 约 36,000+
- **一句话定位**: 面向软件开发 Agent 的开源平台， Devin 的最强开源替代品之一
- **核心特性**:
  - **全能型 Agent**：可修改代码、运行命令行、浏览网页、调用 API
  - **沙箱执行环境**：Docker 隔离的安全执行环境
  - **Web GUI**：localhost:3000 提供可视化的交互界面
  - **CLI 启动器**：通过 `uv` 一键启动
  - **多模型支持**：最佳适配 Claude Sonnet 4.5，也支持 GPT-4o 等
  - **学术背书**：ICLR 2025 发表论文
  - **云服务**：提供 OpenHands Cloud 托管方案
- **技术栈**: Python / TypeScript、Docker、React 前端
- **开源状态**: MIT License（enterprise/ 目录除外）
- **活跃度**: 高。从 OpenDevin 成功品牌升级为 OpenHands，社区增长迅速
- **SDLC 覆盖**: ★★★★★ 高覆盖。作为通用型软件开发 Agent，可自主完成从理解需求到编写代码、运行测试、部署的全流程

---

### 6. CrewAI — 自主 AI Agent 编排框架

- **GitHub**: https://github.com/crewAIInc/crewai
- **Star 数**: 约 30,000+
- **一句话定位**: 轻量、快速的自主 AI Agent 角色扮演编排框架
- **核心特性**:
  - **角色驱动设计**：基于 Role-Playing 的 Agent 定义，每个 Agent 扮演特定角色
  - **任务委托机制**：支持 autonomous 模式（Agent 自主决策）和顺序执行模式
  - **工具使用**：Agent 可调用各种工具完成任务
  - **内存系统**：短期/长期/实体记忆多层次记忆
  - **双模式支持**：既支持无代码快速搭建，也支持完全代码控制
  - **生态丰富**：独立 Examples 仓库、Awesome 列表、Marketplace 模板
  - **进程集成**：支持与实际业务流程结合
- **技术栈**: Python、支持多种 LLM 后端
- **开源状态**: MIT License
- **活跃度**: 高。社区活跃，模板市场持续增长
- **SDLC 覆盖**: ★★★☆☆ 中等。作为通用 Agent 编排框架，可通过自定义角色和任务覆盖 SDLC 各阶段，但需要自行组装工作流

---

### 7. Aider — 终端 AI 结对编程工具

- **GitHub**: https://github.com/paul-gauthier/aider
- **Star 数**: 约 32,000+
- **一句话定位**: 在终端中与 LLM 进行 AI 结对编程的命令行工具
- **核心特性**:
  - **Git 原生**：直接在 git 仓库中工作，自动创建带语义信息的 commit
  - **多文件编辑**：可同时编辑多个文件以完成复杂请求
  - **代码库地图**：利用整个 git repo 的地图信息，在大代码库中表现良好
  - **实时协同**：在编辑器中修改文件时，Aider 始终使用最新版本
  - **多模态输入**：支持图片输入（截图转功能）、URL 内容读取、语音编码
  - **广泛 LLM 兼容**：最佳适配 GPT-4o & Claude 3.5 Sonnet，可连接几乎所有 LLM
  - **SWE Bench 表现**：在 SWE Bench 基准测试中名列前茅，解决真实 GitHub Issue
- **技术栈**: Python、Git
- **开源状态**: Apache 2.0
- **活跃度**: 高。个人项目但维护非常积极，社区口碑极佳
- **SDLC 覆盖**: ★★★☆☆ 聚焦编码阶段。主要作为结对编程助手覆盖编码和 bug 修复，不直接涉及需求和设计阶段

---

### 8. Cline — IDE 内自主编码 Agent

- **GitHub**: https://github.com/cline/cline
- **Star 数**: 约 35,000+
- **一句话定位**: 直接在 IDE 中运行的自主编码 Agent，具备文件操作、命令执行、浏览器使用等能力
- **核心特性**:
  - **IDE 原生集成**：VS Code 扩展形式，深度集成开发环境
  - **文件创建/编辑**：带 diff 视图的文件变更，实时监控 linter/compiler 错误并自动修复
  - **终端命令执行**：可直接在终端执行命令（安装依赖、运行构建、部署应用、执行测试）
  - **浏览器操作**：基于 Claude Sonnet Computer Use 能力，可启动浏览器进行点击/输入/滚动/截图
  - **MCP 扩展**：通过 Model Context Protocol 动态创建和安装自定义工具
  - **人机审批循环**：每一步操作都需用户授权，安全可控
  - **检查点系统**：每步快照工作区状态，支持对比和回滚
  - **多模型支持**：OpenRouter、Anthropic、OpenAI、Gemini、AWS Bedrock、Azure、本地模型等
- **技术栈**: TypeScript（VS Code Extension）
- **开源状态**: Apache 2.0
- **活跃度**: 极高。更新频繁，有企业版（SSO、审计、私有部署）
- **SDLC 覆盖**: ★★★★☆ 广覆盖。从理解需求 -> 编写代码 -> 运行测试 -> 浏览器验证 -> 部署命令，覆盖大部分开发阶段

---

### 9. SWE-agent — 自动化 Issue 修复 Agent

- **GitHub**: https://github.com/princeton-nlp/SWE-agent
- **Star 数**: 约 29,000+
- **一句话定位**: 普林斯顿大学出品的自动化软件工程 Agent，自动修复 GitHub Issues
- **核心特性**:
  - **Agent-Computer Interface (ACI)**：创新性的 Agent-计算机接口抽象，简化 Agent 与系统的交互
  - **SWE-bench 表现**：完整测试集 12.47% 解决率，SWE-bench Lite 23% 解决率
  - **Issue 驱动**：以 GitHub Issue 为输入，自动定位问题、编写修复、验证结果
  - **EnIGMA 模式**：进攻性网络安全能力，NYU CTF 基准上 3x SOTA 表现
  - **交互式 Agent 工具**：丰富的内置工具集
  - **输出摘要器**：针对长输出的智能摘要能力
- **技术栈**: Python、GPT-4 / Claude 系列
- **开源状态**: MIT License
- **活跃度**: 中等。学术研究项目，普林斯顿 NLP 组维护
- **SDLC 覆盖**: ★★★☆☆ 聚焦测试/修复阶段。专注于 bug 修复这一特定环节，不覆盖需求/设计阶段

---

### 10. AutoDev — IntelliJ AI 驱动编程助手

- **GitHub**: https://github.com/unit-mesh/auto-dev
- **Star 数**: 约 8,000+
- **一句话定位**: IntelliJ IDEA 的 AI 驱动全栈编程助手，覆盖 SDLC 全流程
- **核心特性**:
  - **Sketch 编码 Agent**：类似 Cursor Composer 的 IDE 画布功能（AutoDev 2.0 核心特性）
  - **Auto Development 模式**：
    - AutoSQL：上下文感知的 SQL 生成
    - AutoPage：上下文感知的 Web 页面生成（React）
    - Auto Testing：自动生成单元测试并运行/修复
    - Auto Document：自动生成文档
  - **SDLC 全流程支持**：
    - VCS：自动生成/improve commit message、release note
    - Code Review：生成代码审查内容
    - Smart Refactoring：AI 重命名、代码味道检测、重构建议
    - Dockerfile/CI-CD：根据项目自动生成配置文件
  - **自定义 AI Agent 语言 DevIns/Shire**：可编写自定义 Agent 并集成
  - **多语言支持**：Java、Python、Go、Kotlin、JS/TS、C/C++、Rust 等
  - **内置微调模型**：DeepSeek 6.7B（AutoDev Coder）
  - **企业用户**：ThoughtWorks 等公司在使用
- **技术栈**: Kotlin（IntelliJ Platform SDK）、Chapi AST 引擎
- **开源状态**: MPL 2.0 License
- **活跃度**: 中等偏高。中国开发者主导，持续迭代中
- **SDLC 覆盖**: ★★★★★ 最全面的 SDLC 覆盖之一。从编码 -> 测试 -> 文档 -> Code Review -> CI/CD -> 部署配置，几乎覆盖所有阶段

---

### 11. Devika — 开源 Agentic 软件工程师

- **GitHub**: https://github.com/stitionai/devika
- **Star 数**: 约 28,000+
- **一句话定位**: 第一个开源实现的 Agentic Software Engineer，Devin 的开源替代品
- **核心特性**:
  - **高级 AI 规划推理**：将高层指令分解为可执行步骤
  - **多模型支持**：Claude 3、GPT-4、Gemini、Mistral、Groq、Ollama 本地模型
  - **网页浏览研究**：无缝的网络搜索和信息收集能力
  - **多语言编码**：支持多种编程语言的代码生成
  - **动态状态跟踪**：Agent 状态的可视化和追踪
  - **项目管理**：基于项目的组织和管理工作空间
  - **聊天界面**：自然语言交互方式
  - **可扩展架构**：支持添加新功能和集成
- **技术栈**: Python 3.10-3.11、Node.js 18+、Bun、Playwright
- **开源状态**: MIT License
- **活跃度**: 中等。项目处于早期实验阶段，部分功能未完成；已有后续项目 Opcode（Devika 第二代）
- **SDLC 覆盖**: ★★★★☆ 高覆盖。从理解需求 -> 研究 -> 规划步骤 -> 编写代码，覆盖主要开发阶段

---

### 12. AI-SDLC Framework — AI 增强的全生命周期编排器

- **GitHub**: https://github.com/ai-sdlc-framework/ai-sdlc
- **Star 数**: 较新项目（快速增长中）
- **一句话定位**: 声明式 AI 增强软件开发生命周期治理框架，驱动 AI 编码 Agent 完成全流程
- **核心特性**:
  - **完整编排流水线**：WATCH -> ASSESS -> ROUTE -> EXECUTE -> VALIDATE -> DELIVER -> LEARN 七步闭环
  - **渐进式自治**：Agent 通过表现获得信任等级（Intern -> Junior -> Senior -> Principal），四级自治体系
  - **质量门禁**：每个阶段强制执行质量检查（测试覆盖率、安全扫描、Lint）
  - **Agent 无关**：支持 Claude Code、Copilot、Cursor、Codex、任何 OpenAI 兼容 API
  - **代码库智能**：复杂度分析、架构模式检测、热点识别、情景记忆、工作流模式挖掘
  - **动作治理**：三层强制执行（Orchestrator + Hooks + Branch Protection）
  - **NVIDIA 沙箱**：内核级隔离（Landlock 文件系统 + seccomp 系统调用过滤）
  - **Claude Code 插件**：6 个 Hook + 5 个命令 + 3 个审查 Agent + MCP Server
  - **工作流模式自动检测**：观察开发者-AI 交互序列，自动发现重复模式并提议自动化
  - **Web Dashboard**：Next.js 构建的成本/自治/代码库视图仪表板
- **技术栈**: TypeScript / Node.js 20+、Python/Go SDK
- **开源状态**: Apache 2.0
- **活跃度**: 新项目但架构完善。当前版本 v1alpha1，采用 Kubernetes 风格 API 成熟度模型
- **SDLC 覆盖**: ★★★★★ 专门为 SDLC 设计。这是列表中唯一一个专门围绕"AI 增强 SDLC 治理"理念构建的框架，天然覆盖完整生命周期

---

## 分析总结

### 按 SDLC 覆盖完整性排名

| 项目 | SDLC 覆盖 | 特色优势 |
|------|----------|---------|
| **MetaGPT** | ★★★★★ | 天然模拟软件公司角色分工，一行需求 -> 完整产出 |
| **OpenHands** | ★★★★★ | 通用型软件开发 Agent，最接近 Devin 能力 |
| **AutoDev** | ★★★★★ | IDE 深度集成，唯一覆盖 Code Review + CI/CD 的 IDE 插件 |
| **AI-SDLC Framework** | ★★★★★ | 专门为 SDLC 治理设计，渐进式自治 + 质量门禁 |
| **Cline** | ★★★★☆ | IDE 内全能力 Agent，浏览器操作 + MCP 扩展 |
| **Devika** | ★★★★☆ | 开源 Devin 替代，规划推理能力强 |
| **Dify** | ★★★★☆ | 平台级工作流引擎，适合作为上层编排层 |

### 按成熟度和生产就绪度排名

| 项目 | 成熟度 | 说明 |
|------|--------|------|
| **Dify** | 最高 | 生产级平台，大量企业用户，完整的运维监控体系 |
| **LangGraph** | 很高 | LangChain 官方出品，Klarna/Elastic 等大厂使用 |
| **Cline** | 很高 | 更新极快，已有企业版，社区爆发式增长 |
| **Aider** | 高 | 个人项目但极其稳定，SWE Bench 表现顶尖 |
| **AutoGen** | 中（维护中）| 功能丰富但已进入维护模式 |
| **MetaGPT** | 中高 | 学术+商业双轨发展，ICLR 2025 Oral |
| **OpenHands** | 中高 | 从 OpenDevin 成功升级，学术+社区双轮驱动 |
| **CrewAI** | 中高 | 生态完善，模板市场活跃 |
| **AutoDev** | 中 | 功能全面但主要面向中文社区 |
| **AI-SDLC Framework** | 中低 | 架构先进但处于 v1alpha1 阶段 |
| **SWE-agent** | 中 | 学术研究项目，特定领域表现优秀 |
| **Devika** | 中低 | 早期实验阶段，已有下一代计划 |

### 选型建议

- **需要快速构建 AI 应用/工作流平台** -> 选择 **Dify**
- **需要有状态的复杂 Agent 编排** -> 选择 **LangGraph**
- **需要模拟完整软件团队协作** -> 选择 **MetaGPT**
- **需要类 Devin 的自主软件开发 Agent** -> 选择 **OpenHands** 或 **Devika**
- **需要在 IDE 内获得 AI Agent 能力** -> 选择 **Cline**（VS Code）或 **AutoDev**（IntelliJ）
- **需要终端结对编程体验** -> 选择 **Aider**
- **需要治理 AI Agent 的完整 SDLC 流程** -> 选择 **AI-SDLC Framework**
- **需要灵活的角色扮演 Agent 编排** -> 选择 **CrewAI**
- **需要自动化 Bug 修复** -> 选择 **SWE-agent**

---

*报告完毕。数据来源：各项目 GitHub 仓库页面及官方文档，截至 2026 年 4 月 22 日。*
