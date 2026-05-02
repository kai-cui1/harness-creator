# MetaGPT vs OpenHands 深度技术拆解分析报告

> 分析日期：2026年4月22日
> 分析对象：MetaGPT（~44.3k Stars）与 OpenHands（71.7k Stars）
> 分析维度：架构设计、核心源码、设计模式、Harness Suite 映射对比

---

## 一、基础信息对比

### 1.1 MetaGPT 基础信息

| 维度 | 详情 |
|------|------|
| **GitHub** | https://github.com/geekan/MetaGPT |
| **Star 数** | ~44,300+ |
| **Fork 数** | ~5,500+ |
| **最新版本** | 持续迭代中（主分支活跃） |
| **开源协议** | MIT License |
| **技术栈** | Python 3.9-3.11（不支持 3.12）、Pydantic v2 |
| **一句话定位** | **多智能体软件研发框架 —— 首个 AI 软件公司，输入一行需求输出完整 SDLC 产物** |
| **核心理念** | `Code = SOP(Team)` —— 将标准化操作流程编码为多 Agent 协作工作流 |
| **学术成果** | AFlow 论文被 ICLR 2025 接收为 Oral（Top 1.8%，LLM Agent 类别全球 #2） |
| **商业化进展** | MGX（MetaGPT X）于 2025年2月发布，登顶 ProductHunt #1 |
| **使用方式** | CLI: `metagpt "Create a 2048 game"` / API: `generate_repo()` |

### 1.2 OpenHands 基础信息

| 维度 | 详情 |
|------|------|
| **GitHub** | https://github.com/OpenHands/OpenHands（原 All-Hands-AI/OpenDevin） |
| **Star 数** | **71,700+**（AI 软件开发 Agent 领域最高 Star 项目） |
| **Fork 数** | ~9,000 |
| **最新版本** | **v1.6.0**（2026年3月30日发布） |
| **总提交数** | 6,550+ commits |
| **总 Release 数** | 101 个 |
| **开源协议** | MIT License（enterprise/ 目录除外） |
| **技术栈** | Python 72.7% + TypeScript 25.5%、Docker、React |
| **一句话定位** **自主软件开发 Agent 平台 —— Devin 的最强开源替代品，ICLR 2025 发表论文的通用型软件工程师 Agent** |
| **核心理念** | **CodeAct 范式** —— "代码即动作"，Agent 通过编写和执行代码来完成所有任务 |
| **学术成果** | ICLR 2025 发表论文 "OpenHands: An Open Platform for AI Software Developers as Generalist Agents"，23位作者，13项任务评估 |
| **SWE-Bench 得分** | **77.36%**（业界领先水平） |
| **产品分层** | SDK（可组合 Python 库）→ CLI → Local GUI → Cloud（托管）→ Enterprise（K8s 自部署） |
| **企业客户** | TikTok、VMware、Roche、Amazon、C3 AI、Netflix、Mastercard、Red Hat、MongoDB、Apple、NVIDIA、Google |

### 1.3 核心价值主张对比

| 对比维度 | MetaGPT | OpenHands |
|---------|---------|-----------|
| **核心隐喻** | AI 软件公司（多角色协作） | AI 软件工程师（全能单 Agent） |
| **任务模式** | 结构化 SDLC 流水线（需求→设计→编码→测试） | 自主探索式编程（ReAct 循环 + CodeAct） |
| **Agent 数量** | 多 Agent（PM + Architect + Engineer + QA + ...） | 单 Agent 主导（但支持扩展） |
| **协作机制** | SOP 编排的消息传递管道 | EventStream 事件驱动循环 |
| **执行环境** | 直接文件系统操作 | Docker 沙箱隔离环境 |
| **适用场景** | 从零生成完整项目 / SDLC 自动化 | 现有代码库修改 / Issue 修复 / 功能增强 |
| **产出物** | 用户故事、PRD、API 设计、数据结构、源码、测试用例 | 可运行的代码变更、命令执行结果、浏览器交互结果 |

---

## 二、架构设计深度分析

### 2.1 MetaGPT 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户入口层                               │
│   CLI (metagpt "requirement") / API (generate_repo())       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Team（团队编排器）                        │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│   │   PM    │→│Architect│→│Engineer │→│   QA    │        │
│   │(产品经理)│ │(架构师)  │ │(工程师)  │ │(测试员)  │        │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│          ↑            ↑           ↑          ↑               │
│          └────────────┴───────────┴──────────┘               │
│                        │                                     │
│              ┌─────────▼─────────┐                          │
│              │   Environment     │                          │
│              │  （消息总线/环境）  │                          │
│              └───────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    基础设施层                                 │
│   LLM 接口 (OpenAI/Claude) │ 文件系统 │ 工具链 │ 记忆系统    │
└─────────────────────────────────────────────────────────────┘
```

#### 核心模块划分与职责

| 模块 | 路径 | 职责 |
|------|------|------|
| **Role（角色）** | `metagpt/roles/` | Agent 的抽象基类与具体角色实现（PM/Architect/Engineer/QA/Researcher/DataInterpreter） |
| **Action（动作）** | `metagpt/actions/` | 角色可执行的具体原子操作（WritePRD/WriteDesign/WriteCode/RunTests 等） |
| **Environment（环境）** | `metagpt/environment/` | 运行时容器，管理消息路由、角色注册、成本追踪 |
| **Team（团队）** | `metagpt/team.py` | 顶层编排器，组装角色并驱动多轮协作执行 |
| **Memory（记忆）** | `metagpt/memory/` | 多层次记忆系统（短期/长期/工作记忆） |
| **Tools（工具）** | `metagpt/tools/` | 外部工具集成（搜索引擎、代码执行、文件操作等） |
| **Prompt（提示词）** | `metagpt/prompt/` | 所有 LLM 提示词模板管理 |
| **Config（配置）** | `metagpt/config/` | 全局配置管理（LLM 密钥、模型参数等） |

#### Agent 协作/编排机制详解

MetaGPT 的协作机制基于 **消息传递（Message Passing）** 模式：

1. **Environment 作为消息中枢**：所有 Role 注册到 Environment 中，通过 Environment 进行消息收发
2. **Publish-Subscribe 模式**：
   - 每个 Role 有一个 `watch` 集合，声明自己关注哪些消息类型
   - 当 Role 发布消息时，Environment 根据 `watch` 集合将消息路由给订阅者
   - 消息携带 `send_to` 地址信息，支持点对点定向投递
3. **有序流水线执行**：
   - PM 先产出用户故事和 PRD → 消息发布到 Environment
   - Architect 监听到 PRD 消息 → 读取后进行架构设计 → 输出 API 设计和数据结构
   - Engineer 监听到设计文档 → 读取后编写代码
   - QA 监听到代码 → 编写并运行测试用例
4. **三种 React 模式**（详见下文源码分析）

### 2.2 OpenHands 整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                       用户交互层                                   │
│   Web GUI (localhost:3000) / CLI / SDK API / Cloud / Enterprise   │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Server（HTTP 会话管理）                        │
│   Session 管理 │ 身份认证 │ WebSocket 连接 │ RESTful API          │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                  AgentController（控制器）                         │
│   ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐   │
│   │  初始化 Agent  │→│ 管理 State   │→│  驱动主执行循环         │   │
│   │ init_state()  │ │ State 更新   │ │ while True: step()    │   │
│   └──────────────┘  └─────────────┘  └──────────────────────┘   │
└──────────────────────────────┬───────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────────┐ ┌────────────────┐ ┌────────────────────────┐
│    LLM (LiteLLM) │ │  EventStream   │ │      Runtime           │
│  模型调度/网关    │ │  （事件中心）    │ │  （动作执行引擎）        │
│  100+ 模型支持    │ │  ActionEvent   │ │  ┌─────────────────┐  │
│                  │ │  ObservationEvt│ │  │ Docker Runtime  │  │
│                  │ │  MessageEvent  │ │  │ Local Runtime   │  │
│                  │ │  SystemPrompt  │ │  │ Remote Runtime  │  │
│                  │ │  TokenEvent    │ │  │ Modal Runtime   │  │
│                  │ │                │ │  │ Runloop Runtime │  │
│                  │ │                │ │  └─────────────────┘  │
└──────────────────┘ └────────────────┘ └────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Sandbox（沙箱执行环境）                         │
│   Bash 命令执行 │ 浏览器控制 │ 文件系统操作 │ 网络请求隔离            │
└──────────────────────────────────────────────────────────────────┘
```

#### 核心模块划分与职责

| 模块 | 路径 | 职责 |
|------|------|------|
| **Agent** | `openhands-sdk/openhands/sdk/agent/agent.py` | 核心 Agent 实现，包含状态机、动作批处理、安全分析、Critic 自评 |
| **AgentController** | `openhands/agent/controller.py` | 初始化 Agent、管理 State、驱动主执行循环 |
| **EventStream** | `openhands/runtime/event_stream.py` | 中央事件枢纽，所有 Actions 和 Observations 都流经此处 |
| **Runtime** | `openhands/runtime/` | 执行引擎，将 Action 转换为 Observation（含 4 种实现） |
| **State** | `openhands/state/state.py` | 任务状态管理，维护对话历史、错误状态等 |
| **LLM** | `openhands/llm/` | 基于 LiteLLM 的模型网关，统一 100+ 模型接口 |
| **Server** | `openhands/server/` | HTTP 服务层，处理会话管理和客户端通信 |
| **Sandbox** | `openhands/runtime/sandbox/` | Docker/本地/远程沙箱环境，提供安全的代码执行空间 |

#### EventStream 架构详解

OpenHands 的核心创新在于 **EventStream 事件驱动架构**：

```
[User Request]
     │
     ▼
[SystemPromptEvent] ──→ 初始化系统提示词
     │
     ▼
[MessageEvent] ──→ 用户消息入队
     │
     ▼
  ┌─────────────────────────────────────┐
  │         Agent.step() 执行循环         │
  │                                      │
  │  1. 准备 LLM Messages（含 Condensation 压缩）
  │  2. 调用 LLM.completion()
  │  3. 解析响应 → 分发处理：
  │     ├─ TOOL_CALLS → ActionEvent(s)
  │     │     ├─ 安全风险提取 (LLMSecurityAnalyzer)
  │     │     ├─ Critic 自评 (CriticMixin)
  │     │     └─ 用户确认检查 (Confirmation Policy)
  │     │           │
  │     │           ▼
  │     │     _ActionBatch.prepare() ──→ 截断/分区/并行执行
  │     │           │
  │     │           ▼
  │     │     [ObservationEvent] 或 [AgentErrorEvent]
  │     │
  │     ├─ CONTENT → [MessageEvent]
  │     ├─ REASONING_ONLY → [TokenEvent]
  │     └─ EMPTY → 忽略
  │                                      │
  └─────────────────────────────────────┘
     │
     ▼
[CondensationRequest] ──→ 上下文窗口超限时触发压缩
     │
     ▼
[FinishEvent] ──→ 任务完成（或继续循环）
```

---

## 三、源码关键模块解读

### 3.1 MetaGPT 核心源码解读

#### 文件一：`metagpt/roles/role.py` —— Role 基类（绝对核心，约 500+ 行）

这是整个 MetaGPT 框架的灵魂文件。以下是逐模块深度解析：

```python
# ==================== 枚举定义 ====================

class RoleReactMode(Enum):
    """Agent 反应模式枚举"""
    REACT = "react"              # 标准 ReAct 模式：思考→行动 循环
    BY_ORDER = "by_order"        # 按序执行：按 actions 列表顺序依次执行
    PLAN_AND_ACT = "plan_and_act" # 先规划后执行：先由 Planner 制定计划，再逐步执行


# ==================== 数据模型 ====================

class RoleContext(BaseModel):
    """Role 运行时上下文 —— Agent 的"大脑状态""""
    env: Optional[Environment] = None      # 运行环境引用
    msg_buffer: MessageQueue = Field(default_factory=MessageQueue)  # 消息缓冲区
    memory: Memory = Field(default_factory=Memory)        # 长期记忆
    working_memory: Memory = Field(default_factory=Memory) # 工作记忆（当前回合）
    state: int = -1                                  # 当前状态编号（状态机指针）
    todo: Optional[Action] = None                    # 当前待执行的 Action
    watch: set[str] = set()                          # 关注的消息类型集合
    news: list[Message] = []                         # 新接收到的消息列表
    react_mode: RoleReactMode = RoleReactMode.REACT  # 反应模式
    max_react_loop: int = 1                          # 最大反应循环次数


# ==================== Role 类定义 ====================

class Role(BaseRole, SerializationMixin, ContextMixin, BaseModel):
    """
    Role —— MetaGPT 中 Agent 的核心抽象

    设计哲学：
    - 一个 Role = 一个专业角色（如产品经理、架构师、工程师）
    - 每个 Role 拥有一组 Action（能力）和特定的行为模式（react_mode）
    - 通过 Environment 进行消息传递实现协作

    继承链：BaseRole（接口定义）→ SerializationMixin（序列化）→ ContextMixin（上下文）→ BaseModel（Pydantic 数据校验）
    """

    name: str = ""                    # 角色名称
    profile: str = ""                 # 角色描述/人设
    goal: str = ""                    # 角色目标
    constraints: str = ""             # 角色约束条件
    status: str = ""                  # 当前状态描述
    actions: list[Action] = []        # 该角色可执行的动作列表
    scenarios: list[str] = []         # 适用场景
    roles: set["Role"] = set()        # 子角色集合（支持角色嵌套）

    # 运行时上下文（通过 ContextMixin 注入）
    _rc: RoleContext = PrivateAttr(default_factory=RoleContext)

    # ========== 核心生命周期方法 ==========

    def _think(self) -> bool:
        """
        【核心方法】基于 LLM 的状态决策

        这是 MetaGPT Agent "智能"的来源 —— 通过 LLM 决定下一步该做什么。

        决策逻辑分支：
        1. 单动作快捷路径：如果只有 1 个 action，直接设为 todo，返回 True
        2. 恢复模式：如果 state 不为 -1，说明是恢复执行，保持当前 state
        3. BY_ORDER 模式：state 递增，按顺序选择下一个 action
        4. 完整 LLM 决策：使用 STATE_TEMPLATE prompt 让 LLM 选择状态编号
           - 返回 0 到 n_states 之间的数字（对应某个 action）
           - 返回 -1 表示完成所有工作

        技术细节：
        - 使用 self.rc.state 作为状态机指针
        - states 列表将状态编号映射到 action 索引
        - LLM 返回的是数字编号，不是文本
        """
        # ... (完整实现约 40 行)

    def _act(self) -> Message:
        """
        【核心方法】执行当前选中的 Action

        执行流程：
        1. 获取当前 todo（由 _think() 设定）
        2. 调用 action.run(self.rc.history) 执行
            - 传入历史消息作为上下文
            - Action 内部会调用 LLM 生成具体内容
        3. 将结果包装为 AIMessage 返回

        关键设计：Action 与 Role 分离
        - Action 是纯执行单元，不知道自己在哪个 Role 中
        - Role 负责"决定做什么"，Action 负责"具体怎么做"
        """
        todo = self.rc.todo
        if isinstance(todo, Action):
            result = await todo.run(self.rc.history)  # 传入历史消息作为上下文
            return AIMessage(content=result, cause_by=type(todo))

    def _observe(self) -> int:
        """
        【核心方法】观察环境中的新消息

        消息过滤流程：
        1. 从 Environment 的 msg_buffer 读取所有待处理消息
        2. 按 watch 集合过滤：只保留角色关注的消息类型
        3. 按 send_to 过滤：只保留发送给当前角色的消息
        4. 将过滤后的消息存入 memory（长期记忆）
        5. 返回新消息数量

        设计要点：
        - 这是"发布-订阅"模式的订阅端实现
        - watch 集合在角色初始化时设定，决定了角色的"感知范围"
        - 支持通配符匹配和精确匹配
        """
        # ... (完整实现约 20 行)

    def _react(self) -> int:
        """
        【核心方法】标准 ReAct 执行循环

        伪代码：
        ```
        actions_taken = 0
        while actions_taken < max_react_loop:
            if not _think():  # LLM 决定结束
                break
            _act()           # 执行动作
            actions_taken++
        ```

        这是最常用的执行模式，实现了 Reasoning + Acting 的闭环。
        """
        actions_taken = 0
        while actions_taken < self.rc.max_react_loop:
            if not await self._think():  # LLM 返回 -1（完成信号）
                break
            msg = await self._act()       # 执行动作

            # 消息发布逻辑...
            self.publish_message(msg)
            actions_taken += 1

    def _plan_and_act(self) -> int:
        """
        【核心方法】先规划后执行模式

        执行流程：
        1. 创建 Planner 实例
        2. Planner 根据当前目标和上下文制定执行计划
        3. 计划是一系列有序的任务（每个任务对应一个 Action）
        4. 按顺序执行计划中的任务
        5. 支持动态调整计划（根据中间结果重新规划）

        适用场景：复杂任务需要提前规划执行步骤时
        """
        # 创建 Planner 并制定计划
        plan = await self._create_plan()
        # 按顺序执行计划中的任务
        for task in plan.tasks:
            self.rc.todo = task.action
            await self._act()

    async def run(self, with_message: Message = None) -> None | Message:
        """
        【入口方法】Role 的主执行入口

        完整生命周期：
        1. observe()  —— 从环境接收消息
        2. react()    —— 思考并行动（内部调用 _think + _act 循环）
        3. publish_message() —— 将结果消息发布到 Environment

        这是 Team 调用每个 Role 的唯一入口点。
        """
        if with_message:
            self.put_message(with_message)
        await self._observe()
        response = await self._react()  # 根据 react_mode 分发到 _react 或 _plan_and_act
        self.publish_message(response)
        return response
```

**关键设计洞察**：

1. **状态机驱动的动作选择**：`_think()` 方法让 LLM 返回一个数字（状态编号），这个数字映射到 `states` 列表中的某个 Action。这是一种极其优雅的设计——将非结构化的 LLM 输出转化为确定性的程序控制流。

2. **Role-Action 分离原则**：Role 负责"决策"（做什么），Action 负责"执行"（怎么做）。这种分离使得 Action 可以在不同 Role 之间复用。

3. **三种 React 模式的策略模式应用**：`REACT`（通用 ReAct 循环）、`BY_ORDER`（确定性顺序执行）、`PLAN_AND_ACT`（先规划后执行），覆盖了从简单到复杂的各种任务场景。

#### 文件二：`metagpt/team.py` —— 团队编排器（约 130 行）

```python
class Team:
    """
    Team —— 多角色协作的顶层编排器

    职责：
    1. 组装角色团队（hire）
    2. 管理项目预算（investment）
    3. 驱动多轮协作执行（run）
    """

    env: Environment          # 运行环境（消息中枢）
    investment: float = 0.0   # 项目预算（用于 LLM API 成本控制）
    idea: str = ""            # 产品创意/需求描述

    def hire(self, roles: list[Role]) -> None:
        """招聘角色：将 Role 注册到 Environment 中"""
        for role in roles:
            self.env.add_role(role)

    def run_project(self, idea: str, investment: float = 0.0) -> None:
        """启动项目：设置需求和预算"""
        self.idea = idea
        self.investment = investment

    async def run(self, n_round: int = 3) -> None:
        """
        主执行循环 —— 驱动 n_round 轮协作

        每轮执行流程：
        1. 检查预算是否耗尽（NoMoneyException）
        2. 依次调用每个 Role 的 run() 方法
        3. Role 内部通过 Environment 进行消息传递
        4. 轮次间自然形成流水线依赖关系

        典型的 3 轮执行：
        Round 1: PM 产出需求文档 → Environment 广播
        Round 2: Architect 读取需求 → 产出架构设计 → Engineer 开始编码
        Round 3: Engineer 完成编码 → QA 编写测试 → 输出最终产物
        """
        for i in range(n_round):
            # 预算检查
            self.env.get_cost_summary()  # 可能抛出 NoMoneyException

            # 驱动所有角色执行一轮
            for role in self.env.roles:
                await role.run()
```

#### 文件三：MetaGPT 目录结构与角色清单

```
metagpt/
├── roles/                    # ★★★ 角色定义（核心目录）
│   ├── role.py              # Role 基类（上述详细分析）
│   ├── pm.py                # 产品经理（ProductManager）
│   │   ├── 动作: WriteUserStory, WritePRD, AnalyzeRequirements
│   │   ├── 输出: 用户故事列表、产品需求文档
│   │   └── 监听: 用户原始需求
│   ├── architect.py          # 架构师（Architect）
│   │   ├── 动作: WriteDesign, DefineAPIs, DefineDataStructure
│   │   ├── 输出: 系统架构图、API 接口定义、数据模型
│   │   └── 监听: PRD 文档
│   ├── engineer.py           # 工程师（Engineer）
│   │   ├── 动作: WriteCode, DebugCode, RefactorCode
│   │   ├── 输出: 源代码文件
│   │   └── 监听: 架构设计文档 + API 定义
│   ├── qa.py                 # 测试工程师（QA Engineer）
│   │   ├── 动作: WriteTests, RunTests, AnalyzeTestResults
│   │   ├── 输出: 测试用例、测试报告
│   │   └── 监听: 源代码
│   ├── researcher.py         # 研究员（Researcher）
│   │   ├── 动作: WebSearch, SummarizePapers, CollectData
│   │   ├── 输出: 研究报告、数据摘要
│   │   └── 监听: 研究需求
│   └── data_interpreter.py   # 数据分析师（Data Interpreter）
│       ├── 动作: WriteCode, ExecuteCode, AnalyzeData
│       ├── 输出: 数据分析结果、图表
│       └── 监听: 数据分析需求
│
├── actions/                  # 动作定义（Role 的能力单元）
│   ├── write_doc.py         # 文档编写动作
│   ├── write_code.py        # 代码编写动作
│   ├── design_api.py        # API 设计动作
│   ├── run_code.py          # 代码执行动作
│   └── search.py            # 搜索动作
│
├── environment/             # 环境与消息系统
│   ├── environment.py       # Environment 类（消息中枢）
│   └── message_queue.py     # MessageQueue（消息队列实现）
│
├── memory/                   # 记忆系统
│   ├── memory.py            # Memory 基类
│   ├── long_term_memory.py  # 长期记忆
│   └── working_memory.py    # 工作记忆
│
├── tools/                    # 工具链
│   ├── web_browser.py       # 网页浏览工具
│   ├── terminal.py          # 终端工具
│   ├── file_tool.py         # 文件操作工具
│   └── search_engine.py     # 搜索引擎工具
│
├── team.py                   # Team 编排器
├── config/                   # 配置管理
└── prompt/                   # 提示词模板
    ├── role_templates.py    # 角色提示词模板
    └── action_templates.py  # 动作提示词模板
```

### 3.2 OpenHands 核心源码解读

#### 文件一：`openhands-sdk/openhands/sdk/agent/agent.py` —— Agent 类（1053 行，SDK V1 重构版）

这是 OpenHands 2025 年重构后的 Software Agent SDK 核心实现。以下是其架构级深度解析：

```python
# ==================== 类继承体系 ====================

class Agent(CriticMixin, ResponseDispatchMixin, AgentBase):
    """
    Agent —— OpenHands 的核心智能体实现

    继承链设计（Mixin 模式）：
    - CriticMixin:       自评能力 —— Agent 在执行前对自身决策进行批判性评估
    - ResponseDispatchMixin: 响应分发 —— 将 LLM 响应分发到不同处理逻辑
    - AgentBase:         基础接口 —— 定义 Agent 的核心契约

    设计哲学（CodeAct 范式）：
    "代码即动作" —— Agent 不直接调用预定义的工具函数，
    而是通过编写代码（Python/Bash）来间接完成所有操作。
    这赋予了 Agent 无限的表达能力和灵活性。
    """

    # ==================== 核心数据结构 ====================

    @dataclass(frozen=True, slots=True)
    class _ActionBatch:
        """
        【关键创新】不可变动作批次 —— 并行执行的核心抽象

        设计理念：
        - 不可变（frozen）：一旦创建就不能修改，保证线程安全
        - slots 模式：内存优化，减少属性访问开销
        - 三阶段生命周期：prepare → emit → finalize

        解决的问题：
        1. LLM 可能一次返回多个 Tool Call（并行机会）
        2. 某些 Tool Call 可能依赖前一个的结果（阻塞依赖）
        3. FinishTool 出现后的 Tool Call 应该被截断（语义完整性）

        工作流程：
        prepare():
          - 在 FinishTool 处截断后续动作
          - 将动作分为 blocked（有依赖）和 unblocked（无依赖）两组
          - 并行执行所有 unblocked 动作
        emit():
          - 按原始顺序发射 Observation 事件（保证因果顺序）
        finalize():
          - 如果有 FinishTool，进入迭代优化阶段
          - 否则标记批次完成
        """
        actions: list[ActionEvent]
        parallel_tool_executor: 'ParallelToolExecutor'
        runtime: 'Runtime'

        async def prepare(self) -> '_ActionBatch.Prepared':
            """准备阶段：截断、分区、并行执行"""
            # 1. 找到 FinishTool 位置，截断后续
            # 2. 分析依赖关系，分区
            # 3. 并行执行 unblocked 组
            pass

        async def emit(self, prepared: Prepared) -> list[Observation]:
            """发射阶段：按序发射结果"""
            pass

        async def finalize(self, emitted: list[Observation]):
            """完成阶段：迭代优化或标记完成"""
            pass

    # ==================== 核心方法 ====================

    async def init_state(self, state: State) -> None:
        """
        【入口方法】初始化会话状态

        关键职责：
        1. 强制 SystemPromptEvent 顺序不变量：
           - SystemPromptEvent 必须出现在前 3 个事件中
           - 这保证了 LLM 总是在正确的系统提示词上下文中工作
        2. 准备系统提示词（静态 + 动态内容分离）：
           - 静态部分：角色定义、可用工具列表、约束条件（可缓存）
           - 动态部分：当前任务状态、历史操作摘要（每次重建）
        3. 初始化对话历史和成本追踪
        """
        # SystemPromptEvent 位置验证
        sp_events = [e for e in state.history if isinstance(e, SystemPromptEvent)]
        assert len(sp_events) > 0, "SystemPromptEvent is required"

        # 静态/动态内容分离构建系统提示词
        system_prompt = self._build_system_prompt(static=self._static_prompt_content,
                                                   dynamic=self._dynamic_prompt_content(state))

    async def step(self) -> None:
        """
        【核心方法】单步执行 —— Agent 的"心跳"

        这是主执行循环中被调用的核心方法。每一步的完整流程：

        ┌─────────────────────────────────────────────┐
        │ 1. 检查 pending_actions（确认模式）          │
        │    → 如果有待确认动作，等待用户确认           │
        ├─────────────────────────────────────────────┤
        │ 2. 检查 blocked_messages（阻塞消息）          │
        │    → 如果有未解析的阻塞消息，优先处理         │
        ├─────────────────────────────────────────────┤
        │ 3. 准备 LLM Messages                        │
        │    → 从 State.history 构建                  │
        │    → 触发 Condensation（如果上下文超长）     │
        ├─────────────────────────────────────────────┤
        │ 4. 调用 LLM.completion()                    │
        │    → LiteLLM 统一接口，支持 100+ 模型        │
        ├─────────────────────────────────────────────┤
        │ 5. 分发响应（ResponseDispatchMixin）         │
        │    ├─ TOOL_CALLS → _execute_actions()       │
        │    │   → _ActionBatch 三阶段执行            │
        │    ├─ CONTENT → MessageEvent                │
        │    ├─ REASONING_ONLY → TokenEvent           │
        │    └─ EMPTY → 忽略                          │
        └─────────────────────────────────────────────┘
        """
        # Phase 1: 确认检查
        if self.state.pending_actions:
            await self._handle_pending_actions()
            return

        # Phase 2: 阻塞消息检查
        if self.state.blocked_messages:
            await self._handle_blocked_messages()
            return

        # Phase 3: 准备 LLM 输入
        messages = self._prepare_messages(state)

        # Phase 4: Condensation（上下文压缩）
        try:
            resp = await self.llm.completion(messages)
        except LLMContextWindowExceedError:
            # 触发压缩后重试
            condensation_request = CondensationRequest(...)
            messages = await self.condenser.condense(messages)
            resp = await self.llm.completion(messages)

        # Phase 5: 响应分发
        if resp.tool_calls:
            await self._execute_actions(resp.tool_calls)
        elif resp.content:
            self.event_stream.add_event(MessageEvent(content=resp.content))
        elif resp.reasoning:
            self.event_stream.add_event(TokenEvent(content=resp.reasoning))

    async def _get_action_event(self, tool_call: ToolCall) -> ActionEvent:
        """
        【关键方法】Tool Call → ActionEvent 转换

        转换管线（Pipeline 模式）：
        1. 参数解析：将 LLM 返回的 JSON 参数解析为结构化数据
        2. 参数规范化：标准化参数格式（处理别名、默认值等）
        3. 安全风险提取：_extract_security_risk(tool_call)
           → 调用 LLMSecurityAnalyzer 分析此工具调用的安全风险等级
        4. 摘要提取：生成此操作的简短摘要（用于日志和 UI 显示）
        5. Critic 自评：critic.evaluate(action, context)
           → Agent 自身对即将执行的操作进行合理性检查
        6. 用户确认检查：_requires_user_confirmation(action, risk)
           → 高风险操作需用户确认后才执行

        返回：完整的 ActionEvent（包含所有元数据和审批状态）
        """
        # 参数解析与规范化
        arguments = self._parse_arguments(tool_call.arguments)
        arguments = self._normalize_arguments(arguments, tool_call.name)

        # 安全风险分析
        risk = await self._extract_security_risk(tool_call)

        # Critic 自评
        critic_result = await self.critic.evaluate(
            action=tool_call,
            context=self.state.summary
        )

        # 确认策略检查
        confirmation_required = self._requires_user_confirmation(
            action=tool_call,
            security_risk=risk
        )

        return ActionEvent(
            action=tool_call.name,
            arguments=arguments,
            security_risk=risk,
            critic_evaluation=critic_result,
            confirmation_required=confirmation_required,
        )

    async def _execute_action_event(self, event: ActionEvent) -> ObservationEvent | AgentErrorEvent:
        """
        【关键方法】单个动作事件执行

        执行包装：
        1. 可观测性包装（Observability Wrapping）：
           - 记录开始时间、执行时长
           - 捕获异常并转换为 AgentErrorEvent
        2. Runtime 委托执行：
           - 调用 self.runtime.run(event.action, event.arguments)
           - Runtime 根据动作类型分派到不同执行器：
             * Bash 命令 → Bash Runtime
             * 文件操作 → Filesystem Runtime
             * 网页操作 → Browser Runtime
             * API 调用 → HTTP Runtime
        3. 结果封装：
           - 成功 → ObservationEvent（包含输出内容、退出码等）
           - 失败 → AgentErrorEvent（包含错误信息、堆栈跟踪）
        """
        try:
            observation = await self.runtime.run(
                action=event.action,
                arguments=event.arguments
            )
            return ObservationEvent(observation)
        except Exception as e:
            return AgentErrorEvent(error=str(e), traceback=format_exc())

    async def _extract_security_risk(self, tool_call: ToolCall) -> SecurityRisk:
        """
        【安全特性】每次工具调用的安全风险分析

        集成 LLMSecurityAnalyzer：
        - 分析工具调用参数是否包含危险操作
        - 检测潜在的数据泄露风险
        - 识别可能的资源滥用模式
        - 返回风险等级（LOW/MEDIUM/HIGH/CRITICAL）

        这是 OpenHands 企业级安全能力的核心组件。
        """
        return await self.security_analyzer.analyze(tool_call)
```

**关键设计洞察**：

1. **_ActionBatch 不可变批次模式**：这是 OpenHands 最精巧的设计之一。通过将一批 Tool Call 封装为不可变对象，并在 prepare/emit/finalize 三阶段中分别处理截断、分区、发射和优化，完美解决了并行执行与顺序保证之间的矛盾。

2. **安全内建（Security by Design）**：每次工具调用都经过 `_extract_security_risk()` 分析，而非事后审计。这种"默认安全"的设计理念值得所有 Agent 框架学习。

3. **CriticMixin 自评机制**：Agent 在执行操作前先自我审查，这类似于人类的"三思而后行"。通过 Mixin 模式注入，保持了核心 Agent 类的简洁性。

4. **Condensation 上下文压缩**：当对话历史超出 LLM 上下文窗口时，自动触发压缩机制。这对长时间运行的编程任务至关重要——一次编程会话可能产生数千条事件。

#### 文件二：OpenHands Runtime 系统

```python
# openhands/runtime/base.py（抽象基类）

class Runtime(ABC):
    """
    Runtime —— 动作执行引擎的抽象基类

    职责：将 ActionEvent 转换为 ObservationEvent

    提供的能力：
    - bash sandbox: Shell 命令执行
    - browser: 浏览器自动化控制
    - filesystem: 文件系统读写操作
    """

    @abstractmethod
    async def ainit(self) -> None:
        """异步初始化（Docker 容器创建等耗时操作）"""

    @abstractmethod
    async def run(self, action: Action, arguments: dict) -> Observation:
        """执行动作并返回观察结果"""


# 四种 Runtime 实现：

class DockerRuntime(Runtime):
    """
    Docker Runtime（默认/推荐）

    工作原理：
    1. 为每个会话创建独立的 Docker 容器
    2. 容器内预装完整开发环境（Python/Node/Git 等）
    3. 通过 docker exec 执行命令
    4. 网络隔离 + 文件系统隔离 = 安全沙箱

    优势：
    - 最强安全性（完全隔离）
    - 环境一致性（预装依赖）
    - 支持快照和回滚

    代价：
    - 需要 Docker daemon
    - 启动较慢（秒级）
    - 资源开销较大
    """
    pass


class LocalRuntime(Runtime):
    """
    Local Runtime（本地开发用）

    工作原理：
    - 直接在主机上执行命令（subprocess）
    - 使用用户目录作为工作空间
    - 无隔离（适合可信环境）

    适用场景：
    - 本地快速开发和调试
    - 不想启动 Docker 时
    - 已信任的代码执行环境
    """
    pass


class RemoteRuntime(Runtime):
    """
    Remote Runtime（HTTP 远程执行）

    工作原理：
    - 通过 HTTP 与远程 ActionExecutionServer 通信
    - Server 端负责实际执行
    - 支持 ActionExecutionClient/Server 分布式模式

    适用场景：
    - 企业级部署（集中管理沙箱）
    - 云原生架构
    - 需要共享执行资源的场景
    """
    pass


class ModalRuntime(Runtime):
    """
    Modal Runtime（Serverless 执行）

    工作原理：
    - 利用 Modal 的 Serverless 基础设施
    - 按需启动执行环境
    - 用完即销毁，零闲置成本

    适用场景：
    - 弹性负载场景
    - 不想管理服务器
    - 按量付费偏好
    """
    pass
```

#### 文件三：EventStream 事件流系统

```python
class EventStream:
    """
    EventStream —— OpenHands 的中央事件枢纽

    设计模式：Mediator（中介者）/ Event Bus（事件总线）

    所有组件之间的通信都通过 EventStream 进行，
    组件之间不直接引用彼此。

    事件类型体系：
    ┌────────────────────────────────────────────┐
    │              Event（基类）                   │
    ├────────────────────────────────────────────┤
    │  Input Events（输入事件）：                   │
    │  ├── MessageEvent      用户/AI 文本消息      │
    │  ├── SystemPromptEvent 系统提示词更新        │
    │  └── CommandEvent      控制命令（暂停/恢复）  │
    ├────────────────────────────────────────────┤
    │  Processing Events（处理事件）：              │
    │  ├── ActionEvent       Agent 决定执行的动作   │
    │  ├── ObservationEvent  动作执行后的观察结果    │
    │  ├── AgentErrorEvent   执行错误              │
    │  └── TokenEvent        LLM 推理 token        │
    ├────────────────────────────────────────────┤
    │  Control Events（控制事件）：                 │
    │  ├── CondensationRequest 上下文压缩请求       │
    │  ├── StopEvent         停止信号              │
    │  └── FinishEvent        完成信号              │
    └────────────────────────────────────────────┘
    """

    def add_event(self, event: Event) -> None:
        """添加事件到流中（线程安全）"""

    def get_events(self, event_type: type[Event]) -> list[Event]:
        """按类型获取事件"""

    def subscribe(self, event_type: type[Event], handler: Callable) -> None:
        """订阅特定类型的事件"""
```

---

## 四、值得学习的设计模式

### 4.1 共通设计模式（两者均采用）

#### 模式 1：ReAct（Reasoning + Acting）循环

| 项目 | 实现方式 | 特点 |
|------|---------|------|
| **MetaGPT** | `_react()` 方法：`while loop { _think() → _act() }` | 状态机增强版 ReAct，LLM 返回状态编号 |
| **OpenHands** | `step()` 方法：`prompt → LLM → action → runtime → observe` | EventStream 驱动的持续循环，支持中断/恢复 |

**学习价值**：ReAct 是目前最成熟的 Agent 执行范式。两者的实现都展示了如何将"思考-行动"循环工程化——MetaGPT 偏向结构化状态机，OpenHands 偏向事件驱动流。

#### 模式 2：消息传递/事件驱动通信

| 项目 | 实现方式 | 特点 |
|------|---------|------|
| **MetaGPT** | Environment 消息总线 + `watch` 集合过滤 | 类型化消息 + 发布订阅 + 点对点混合路由 |
| **OpenHands** | EventStream 中央事件枢纽 + 类型化事件体系 | 单向事件流 + 异步处理 + 时间线回放 |

**学习价值**：两种方案代表了 Agent 通信的两大流派。MetaGPT 的方案更适合结构化工作流（SDLC 各阶段有明确的消息类型），OpenHands 的方案更适合自由探索式任务（事件类型更灵活）。

### 4.2 MetaGPT 独有的设计模式

#### 模式 3：SOP 即代码（Code = SOP(Team)）

**核心理念**：将人类软件公司的标准操作流程（SOP）直接编码为多 Agent 协作的程序结构。

```
人类软件公司 SOP:              MetaGPT 编码实现:

需求分析阶段    ──────────────→  PM Role (WriteUserStory → WritePRD)
架构设计阶段    ──────────────→  Architect Role (WriteDesign → DefineAPIs)
编码实现阶段    ──────────────→  Engineer Role (WriteCode × N)
测试验证阶段    ──────────────→  QA Role (WriteTests → RunTeams)
```

**学习价值**：这是 MetaGPT 最核心的创新。它证明了"流程即代码"的理念在 AI Agent 领域同样适用。对于 Harness Suite 来说，这意味着可以将 SDLC 各阶段的最佳实践编码为可复用的 Agent 工作流模板。

#### 模式 4：Role-Based Agent 抽象（基于角色的 Agent 建模）

MetaGPT 的 Role 抽象质量极高，体现在以下几个层面：

```python
# 层次 1：角色身份（我是谁？）
Role.name = "Alex"
Role.profile = "Senior Product Manager"
Role.goal = "Extract structured requirements from user ideas"
Role.constraints = "Output in Markdown, follow PRD template"

# 层次 2：能力边界（我能做什么？）
Role.actions = [WriteUserStory, WritePRD, ClarifyRequirements]

# 层次 3：感知范围（我关注什么？）
Role.watch = {"RequirementMessage", "UserFeedbackMessage"}

# 层次 4：行为模式（我怎么工作？）
Role.react_mode = RoleReactMode.REACT  # 或 BY_ORDER / PLAN_AND_ACT
```

**学习价值**：四层建模（身份-能力-感知-行为）提供了完整的 Agent 角色定义框架。比简单的 "name + prompt" 模式丰富得多，特别适合模拟真实组织中的专业分工。

#### 模式 5：状态机驱动的动作选择

```python
# MetaGPT 的状态机机制
self.states = [WriteUserStory, WritePRD, ClarifyRequirements]  # 状态列表
self.state = -1  # 当前状态指针

def _think(self):
    # LLM 返回一个数字：0, 1, 2 或 -1（完成）
    next_state = llm.decide(STATE_TEMPLATE, self.states)
    self.state = next_state
    self.rc.todo = self.states[next_state]  # 数字 → Action 映射
```

**学习价值**：将 LLM 的非结构化输出约束为有限状态机的状态转移，极大提高了可控性和可调试性。相比完全自由的 LLM 生成，状态机模式让 Agent 行为可预测、可回放、可审计。

#### 模式 6：任务分解与结果验证流水线

MetaGPT 天然实现了 SDLC 阶段间的验证机制：

```
[PM 输出: PRD 文档]
     │
     ▼
[Architect 验证] ←── PRD 是否足够清晰？能否据此设计？
     │
     ▼
[Architect 输出: 架构设计 + API 定义]
     │
     ▼
[Engineer 验证] ←── API 定义是否可实现？数据结构是否合理？
     │
     ▼
[Engineer 输出: 源代码]
     │
     ▼
[QA 验证] ←── 代码是否符合设计？测试是否通过？
     │
     ▼
[最终产物: 文档 + 代码 + 测试]
```

**学习价值**：每个 SDLC 阶段的输出都是下一阶段的输入，天然形成了"生产者-消费者"验证关系。这种流水线式的质量门禁（Quality Gate）机制是企业级软件开发的核心实践。

### 4.3 OpenHands 独有的设计模式

#### 模式 7：CodeAct 范式（代码即动作）

**核心理念**：Agent 不调用预定义的工具函数，而是通过编写和执行代码来完成所有操作。

```
传统 Tool-Use 模式:          CodeAct 模式:

Agent → call_search(q)       Agent → write Python code:
Agent → call_read_file(f)        import requests
Agent → call_write_file(f,c)     r = requests.get("...")
Agent → call_test(cmd)           print(r.json())
                              Agent → execute code in sandbox
                              Agent → read output
```

**优势**：
- **无限表达能力**：代码可以做任何事情，不受预定义工具集限制
- **组合灵活性**：可以将多个操作组合在一个脚本中
- **错误恢复**：代码可以包含 try/except、重试逻辑等
- **可审计性**：代码本身就是完整的操作记录

**学习价值**：CodeAct 是 OpenHands 在 SWE-Bench 上取得 77.36% 高分的关键原因之一。对于 Harness Suite 来说，这意味着可以让 Agent 通过编写 Harness 脚本/配置来完成复杂的测试编排任务，而不是提供大量细粒度的 API。

#### 模式 8：_ActionBatch 不可变并行执行模式

```python
@dataclass(frozen=True, slots=True)
class _ActionBatch:
    """三阶段不可变动作批次"""

    async def prepare(self) -> Prepared:
        """阶段 1: 准备"""
        # 1a. 在 FinishTool 处截断（语义完整性）
        truncated = self._truncate_at_finish()
        # 1b. 依赖分析 + 分区
        blocked, unblocked = self._partition_by_dependencies(truncated)
        # 1c. 并行执行无依赖动作
        results = await ParallelToolExecutor.execute_all(unblocked)
        return Prepared(blocked, unblocked, results)

    async def emit(self, prepared: Prepared) -> list[Observation]:
        """阶段 2: 发射（按原始顺序）"""
        # 保证事件发射顺序与 LLM 输出一致
        # 即使是并行执行的，也按逻辑顺序通知下游
        return [obs for obs in prepared.in_order()]

    async def finalize(self, emitted: list[Observation]):
        """阶段 3: 完成"""
        if self._contains_finish():
            await self._iterative_refinement(emitted)  # 迭代优化
        else:
            self._mark_batch_complete()
```

**学习价值**：这是并发编程在 Agent 框架中的典范实现。frozen dataclass 保证不可变性，三阶段生命周期清晰分离关注点，依赖自动检测和分区实现了最大化并行度。对于 Harness Suite 的并行测试执行子系统有直接参考价值。

#### 模式 9：安全内建（Security by Design）架构

```python
# 每次 Tool Call 都经过的安全管线
async def _get_action_event(self, tool_call: ToolCall) -> ActionEvent:
    # Step 1: 参数解析
    args = parse(tool_call.arguments)

    # Step 2: 安全风险分析（LLM 驱动的动态风险评估）
    risk = await self._extract_security_risk(tool_call)
    # → LOW: 直接执行
    # → MEDIUM: 记录日志后执行
    # → HIGH: 需要用户确认
    # → CRITICAL: 拒绝执行

    # Step 3: Critic 自评
    critic_score = await self.critic.evaluate(tool_call, context)

    # Step 4: 确认策略判定
    if self._requires_user_confirmation(tool_call, risk):
        self.state.pending_actions.append((tool_call, risk))
        return ConfirmationRequiredEvent(...)

    return ActionEvent(action=tool_call, risk=risk, approved=True)
```

**学习价值**：OpenHands 将安全从"外部附加品"变为"内建基础设施"。每次工具调用都必须经过风险分析和确认流程。对于企业级 Harness 平台来说，这种安全模型可以直接借鉴——特别是在 Agent 自主执行测试、部署等高风险操作时。

#### 模式 10：Condensation 上下文压缩系统

```
问题：长时间运行的编程会话产生大量事件
┌─────────────────────────────────────┐
│ 事件 1-100: 正常处理（在上下文窗口内） │
│ 事件 101-200: 上下文警告             │
│ 事件 201+: 上下文溢出！              │
│                                     │
│ LLMContextWindowExceedError ⚠️       │
└─────────────────────────────────────┘

解决方案：Condensation 压缩
┌─────────────────────────────────────┐
│ 原始历史（2000+ 事件）               │
│           ↓ condenser.condense()    │
│ 压缩后历史（~200 事件）              │
│  - 保留系统提示词（不可压缩）         │
│  - 保留最近 N 条事件（高保真）        │
│  - 中间事件摘要为关键结论（有损压缩）  │
│  - 保留错误和异常（诊断必需）         │
└─────────────────────────────────────┘
```

**学习价值**：对于需要长时间运行的 Agent 任务（如全回归测试、持续监控），上下文管理是核心挑战。OpenHands 的 Condensation 系统提供了一个经过大规模验证的解决方案。

---

## 五、与 Harness Suite 的映射对比分析

### 5.1 概念映射表

| MetaGPT 概念 | OpenHands 概念 | Harness Suite 等价/近似概念 | 迁移可行性 |
|-------------|---------------|--------------------------|-----------|
| **Role（角色）** | **Agent（智能体）** | **Skill / Role Profile** | **高** — Harness 可引入角色化 Agent 定义 |
| **Action（动作）** | **Tool Call / ActionEvent** | **Step / Command / Operation** | **高** — 本质相同，都是原子操作单元 |
| **Environment（环境）** | **EventStream + Runtime** | **Execution Environment / Test Runner** | **中** — 需要适配 Harness 的分布式执行模型 |
| **Team（团队）** | **AgentController** | **Pipeline / Workflow Orchestrator** | **高** — Pipeline 编排是 Harness 的核心能力 |
| **Message（消息）** | **Event（事件）** | **Event / Log Entry / Report** | **高** — 事件体系可直接对应 |
| **Memory（记忆）** | **State / History** | **Test Context / Execution History** | **中** — Harness 的上下文传递可作为简化版记忆 |
| **SOP（标准流程）** | **CodeAct（代码即动作）** | **Template / Blueprint / Recipe** | **高** — 模板化是 Harness 的成熟能力 |
| **PM Role** | — | **Requirement Analyzer / Test Planner** | **高** — 需求分析→测试用例生成的映射自然 |
| **Architect Role** | — | **Test Architect / Strategy Designer** | **高** — 测试架构设计（分层策略、覆盖率目标） |
| **Engineer Role** | **Agent（主体）** | **Test Creator / Script Writer** | **高** — 测试脚本生成是核心场景 |
| **QA Role** | **CriticMixin** | **Validation / Assertion Engine** | **极高** — 结果验证是测试的本质 |
| **_think()（LLM 决策）** | **step() 中的 LLM 调用** | **Decision Point / Condition** | **中** — Harness 的条件逻辑是确定性的，LLM 决策是新增能力 |
| **_react() 循环** | **step() 循环** | **Loop / Retry / Iteration** | **高** — 循环执行是 CI/CD 的基础原语 |
| **watch（消息订阅）** | **Event 订阅** | **Trigger / Webhook / Listener** | **高** — 事件触发是 Harness 的成熟机制 |
| **Docker Runtime** | **Docker Runtime** | **Container Executor / Docker Runner** | **极高** — 几乎一一对应 |
| **_ActionBatch** | — | **Parallel Stage / Matrix Build** | **高** — 并行执行模式高度一致 |
| **Security Risk Analysis** | **LLMSecurityAnalyzer** | **Permission Model / RBAC / Policy** | **中** — Harness 有权限体系，但缺少 LLM 级别的动态风险评估 |
| **Condensation** | — | **Log Truncation / Report Summarization** | **低—中** — Harness 通常不需要超长上下文，但报告摘要可参考 |

### 5.2 可迁移至 Harness Suite 的核心设计

#### 设计 A：MetaGPT 的 SOP 编排模式 → Harness 测试流水线模板

**迁移方案**：将 MetaGPT 的"需求→设计→编码→测试" SOP 编排模式适配为 Harness 的"需求分析→测试策略→脚本生成→执行验证"流水线。

```
MetaGPT SOP:                    Harness 适配:

PM: 分析需求                     ──→  RequirementAgent: 分析需求文档，提取测试点
  ↓                                ↓
Architect: 设计架构                ──→  StrategyAgent: 设计测试策略（分层/覆盖率/优先级）
  ↓                                ↓
Engineer: 编写代码                 ──→  ScriptingAgent: 生成测试脚本（Gherkin/代码）
  ↓                                ↓
QA: 编写&运行测试                  ──→  ValidationAgent: 执行测试并验证结果
```

**具体实施建议**：
1. 在 Harness 中引入 `Role` 抽象：每个 Role 对应测试生命周期的一个阶段
2. 使用 `watch` 机制实现阶段间的数据传递：需求文档 → 测试策略 → 测试脚本 → 执行结果
3. 复用 `BY_ORDER` 模式：测试流水线天然是顺序执行的
4. 引入 `PLAN_AND_ACT` 模式：对于复杂测试场景，先生成测试计划再逐步执行

**预期收益**：将 Harness 从"测试执行平台"升级为"智能测试全生命周期平台"，覆盖测试左移（需求阶段的测试分析）到测试右移（生产环境的监控验证）。

#### 设计 B：OpenHands 的 CodeAct 范式 → Harness 测试脚本自主生成

**迁移方案**：让 Harness Agent 通过编写 Harness 脚本/配置来完成测试任务，而非调用预定义 API。

```
传统方式:                          CodeAct 方式:

Agent.call_api(                   Agent.write_script("""
  "create_test",                    # Harness 测试脚本
  name="Login Test",                name: "Login Flow Test"
  steps=[...]                       steps:
)                                    - navigate: "/login"
                                     - fill: "#email" → "test@example.com"
                                     - fill: "#password" → "secret123"
                                     - click: "#submit"
                                     - assert: url contains "/dashboard"
                                   """)
                                   harness.execute(script)
```

**具体实施建议**：
1. 提供 Harness DSL（领域特定语言）：定义一套简洁的测试描述语法
2. 建立 Sandbox 执行环境：在隔离容器中运行生成的脚本
3. 集成安全分析：对生成的脚本进行安全扫描（借鉴 OpenHands 的 LLMSecurityAnalyzer）
4. 支持 Critic 自评：Agent 生成脚本后自行审查其完整性和正确性

**预期收益**：Agent 可以组合任意 Harness 能力，不受 API 边界限制；生成的脚本人类可读可编辑；天然支持版本控制和代码审查。

#### 设计 C：OpenHands 的 _ActionBatch 并行模式 → Harness 并行测试执行

**迁移方案**：将 _ActionBatch 的三阶段并行执行模式应用于 Harness 的测试套件并行执行。

```
_ActionBatch 模式:                 Harness 并行测试:

prepare():                         Stage 1: 分析依赖
  截断(FinishTool)                   └─ 分析测试间的数据依赖
  分区(blocked/unblocked)            └─ 确定可并行组
  并行执行(unblocked)
                                   Stage 2: 并行执行
emit():                              └─ 并行执行无依赖的测试
  按序发射结果
                                   Stage 3: 汇总结果
finalize():                          └─ 按测试套件顺序汇总报告
  迭代优化(如有 FinishTool)           └─ 失败重试 / 增量执行
```

**具体实施建议**：
1. 依赖分析引擎：自动检测测试间的数据依赖（数据库状态、共享资源等）
2. 动态分区算法：根据依赖图将测试分为多个并行组
3. 结果有序汇并：即使并行执行，也按定义顺序生成报告
4. 快速失败（FailFast）：检测到关键失败时及时截断后续测试（类似 FinishTool 截断）

**预期收益**：显著缩短大规模测试套件的执行时间；保持报告的可读性和可追溯性；支持智能的重试和增量执行。

#### 设计 D：MetaGPT 的状态机 + OpenHands 的安全管线 → Harness Agent 安全执行框架

**迁移方案**：结合两者的优势，构建一个既可控又安全的 Harness Agent 执行框架。

```
                    ┌─────────────────────────┐
                    │   Harness Agent Controller │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ 状态机引擎    │  │ 安全管线      │  │ Critic 自评   │
    │ (from MetaGPT)│  │ (from OH)    │  │ (from OH)    │
    │              │  │              │  │              │
    │ • 状态定义   │  │ • 风险分析   │  │ • 合理性检查  │
    │ • 转移规则   │  │ • 确认策略   │  │ • 覆盖率评估  │
    │ • 回滚能力   │  │ • 审计日志   │  │ • 性能预估   │
    └──────────────┘  └──────────────┘  └──────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────────┐
                    │   Harness Runtime        │
                    │  (Docker / K8s / Local)   │
                    └─────────────────────────┘
```

**具体实施建议**：
1. **状态机引擎**：定义 Harness Agent 的合法状态（分析中/脚本生成中/执行中/验证中/完成/失败），每个状态对应一组允许的操作
2. **安全管线**：对 Agent 的每个操作（创建测试、修改配置、执行部署等）进行实时风险评估
3. **Critic 自评**：Agent 在提交测试脚本前自审其质量和完整性
4. **审计日志**：记录所有 Agent 决策和操作的完整链条（满足合规要求）

### 5.3 不建议迁移的设计

| 设计 | 原因 | 替代建议 |
|------|------|---------|
| MetaGPT 的固定角色集（PM/Architect/Engineer/QA） | 过于刚性，不适合测试领域的多样化场景 | 采用可配置的角色模板，用户自定义角色能力 |
| OpenHands 的浏览器自动化（Browser Runtime） | 与 Harness 核心定位不符 | 如需 UI 测试，集成现有 E2E 测试框架 |
| MetaGPT 的单次运行模型（run_project 后退出） | Harness 需要长期运行的服务模式 | 采用 OpenHands 的持久化会话模型 |
| OpenHands 的单 Agent 主导模式 | 复杂测试场景需要多 Agent 协作 | 采用 MetaGPT 的多 Role 协作模式 |

### 5.4 综合迁移路线图

```
Phase 1: 基础能力引入（1-2 月）
├── 引入 Role 抽象（借鉴 MetaGPT 四层建模）
├── 引入 Action/Step 原子操作模型
└── 建立基础的消息/事件通信机制

Phase 2: 编排能力升级（2-3 月）
├── 实现 SOP 驱动的测试流水线模板
├── 引入状态机驱动的 Agent 执行引擎
└── 支持多 Role 协作的测试工作流

Phase 3: 智能化增强（3-4 月）
├── 集成 CodeAct 范式（Agent 生成测试脚本）
├── 引入 _ActionBatch 并行执行模式
└── 实现 Critic 自评机制

Phase 4: 企业级加固（2-3 月）
├── 部署安全风险分析管线
├── 实现 Condensation 上下文压缩
├── 建立完整的审计日志系统
└── 权限模型与确认策略集成

Phase 5: 生态融合（持续）
├── MCP Server 集成（工具扩展协议）
├── 与现有 Harness 模块的无缝对接
└── 社区角色/动作模板市场
```

---

## 六、总结与关键洞察

### 6.1 两者的本质差异

| 维度 | MetaGPT | OpenHands |
|------|---------|-----------|
| **世界观** | **结构主义** —— 世界可以被分解为有序的角色和流程 | **自由主义** —— Agent 应该拥有最大自由度去探索和创造 |
| **控制策略** | **显式控制** —— SOP + 状态机 + 固定角色 | **隐式引导** —— 系统提示词 + Critic + 安全约束 |
| **适用域** | **有明确流程的任务**（SDLC、数据分析） | **开放域任务**（任意软件工程任务） |
| **可预测性** | **高** —— 相同输入产生相似输出 | **中低** —— Agent 可能采取意外但有创意的路径 |
| **调试难度** | **低** —— 清晰的阶段边界和消息流 | **中高** —— 需要追踪事件流和 LLM 推理链 |

### 6.2 对 Harness Suite 的核心启示

1. **"最好的架构是两者的融合"**：Harness 应该采用 MetaGPT 的结构化编排作为"骨架"（保证可控性和可预测性），同时融入 OpenHands 的自由探索能力作为"肌肉"（处理边缘情况和创造性任务）。

2. **Role > Agent**：MetaGPT 的 Role 抽象比 OpenHands 的单体 Agent 更适合企业级平台。Role 天然对应组织中的岗位，易于理解、权限绑定和审计追踪。

3. **安全必须是第一公民**：OpenHands 的安全内建设计证明，Agent 框架的安全性不能事后补充，必须在架构层面就考虑。对于 Harness 这种接触生产环境的平台尤为重要。

4. **CodeAct 是未来方向**：让 Agent 写代码而非调 API，这个范式转换值得 Harness 提前布局。DSL 设计 + Sandbox 执行 + 安全审核的三位一体是关键。

5. **SWE-Bench 77.36% 的含意**：OpenHands 的成绩表明，开源 Agent 已经达到了可以在真实软件工程任务中辅助（甚至在某些场景下替代）人类的水平。Harness 应该积极考虑将这类 Agent 能力集成到平台中，而非仅仅将其视为外部工具。

---

> **附录：关键文件索引**
>
> **MetaGPT**:
> - 核心文件：`metagpt/roles/role.py`（Role 基类，~500 行）
> - 编排器：`metagpt/team.py`（Team 类，~130 行）
> - 角色：`metagpt/roles/pm.py`, `architect.py`, `engineer.py`, `qa.py`
> - 动作：`metagptpts/actions/` 目录下各动作实现
> - 环境：`metagpt/environment/environment.py`
> - GitHub：https://github.com/geekan/MetaGPT
>
> **OpenHands**:
> - 核心 Agent：`openhands-sdk/openhands/sdk/agent/agent.py`（Agent 类，1053 行）
> - 控制器：`openhands/agent/controller.py`（AgentController）
> - 事件流：`openhands/runtime/event_stream.py`（EventStream）
> - 运行时：`openhands/runtime/base.py` + 4 种实现
> - SDK 仓库：https://github.com/OpenHands/software-agent-sdk
> - 主仓库：https://github.com/OpenHands/OpenHands
