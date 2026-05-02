# Superpowers v5.0.7 深度研究报告

> **日期**: 2026-04-29
> **研究对象**: Superpowers v5.0.7（安装路径 `~/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/`）
> **研究目的**: 系统性分析 Superpowers 的构成原理、定制方法、不足与优化方向，为 Harness Creator 项目提供参考

---

## 一、构成与工作原理

### 1.1 整体架构：三层技能体系

```
┌─────────────────────────────────────────────────────┐
│                  入口层 (Gateway)                     │
│   using-superpowers (SessionStart Hook 自动注入)      │
│   → 建立 "1% 规则" + 技能优先级 + 调度流程图           │
├─────────────────────────────────────────────────────┤
│                 主工作流管道 (Pipeline)                 │
│                                                      │
│  brainstorming → writing-plans → execution → finish  │
│       ↓                ↓          ↓           ↓     │
│   (设计探索)      (实现计划)   (二选一)    (收尾)       │
│                              ├ subagent-driven      │
│                              └ executing-plans      │
├─────────────────────────────────────────────────────┤
│               横切关注点 (Cross-Cutting)              │
│  systematic-debugging │ test-driven-development      │
│  verification-before-completion │ code-review        │
├─────────────────────────────────────────────────────┤
│               基础设施层 (Infrastructure)             │
│  using-git-worktrees │ dispatching-parallel-agents   │
│  writing-skills (元技能: 写技能的技能)                 │
└─────────────────────────────────────────────────────┘
```

### 1.2 全部 14 个技能一览

| # | 技能名称 | 类型 | 定位 | 核心原则 |
|---|---------|------|------|----------|
| 1 | **using-superpowers** | 入口/Gateway | SessionStart 自动注入 | 1% 规则：任何 1% 可能性都须调用技能 |
| 2 | **brainstorming** | 流程/Process | 创意工作的第一步 | HARD-GATE：设计批准前禁止实现 |
| 3 | **writing-plans** | 流程/Process | brainstorming 之后 | Zero Context 假设 + 无占位符 |
| 4 | **subagent-driven-development** | 执行/Execution | 推荐的执行方式 | 每 Task 三阶段：实现→Spec审查→质量审查 |
| 5 | **executing-plans** | 执行/Execution | 备选执行方式（无 subagent） | 同会话顺序执行 + review checkpoint |
| 6 | **systematic-debugging** | 横切/Cross-cutting | 遇到 bug 时强制使用 | 四阶段：根因→模式→假设→修复 |
| 7 | **test-driven-development** | 横切/Cross-cutting | 实现前强制使用 | Iron Law：无测试不写代码 |
| 8 | **verification-before-completion** | 横切/Cross-cutting | 声称完成前必须验证 | Evidence before claims |
| 9 | **requesting-code-review** | 横切/Cross-cutting | 任务完成后请求审查 | Review early, review often |
| 10 | **receiving-code-review** | 横切/Cross-cutting | 收到审查反馈时 | Verify before implementing |
| 11 | **finishing-a-development-branch** | 收尾/Finish | 实现完成后 | 测试→4选项→清理 |
| 12 | **using-git-worktrees** | 基础设施/Infra | 实现前必须隔离 | 目录优先级 + 安全验证 |
| 13 | **dispatching-parallel-agents** | 基础设施/Infra | 多独立任务并行 | 一 agent 一问题域 |
| 14 | **writing-skills** | 元技能/Meta-Skill | 创建新技能时使用 | TDD for documentation |

### 1.3 核心工作机制详解

#### 1.3.1 SessionStart Hook 注入

每次 Claude Code 会话启动时，hook 脚本自动将 `using-superpowers` 的完整内容注入系统提示。这是整个体系的"总开关"。

关键配置：
- `async: false` — 同步执行，确保首次消息前已加载
- `<SUBAGENT-STOP>` 块 — 子代理跳过此技能，避免递归

#### 1.3.2 Skill Tool 调用机制

通过 Claude Code 的 `Skill` 工具按需加载技能内容。**不是 Read 工具**。这是 v3.2.0 后的修正——之前用 Read 工具有循环加载问题。

#### 1.3.3 DOT 流程图作为权威规范

核心技能使用 GraphViz DOT 语法定义流程。流程图是权威定义，散文只是辅助说明。

示例（brainstorming 的流程图定义了 9 步必经路径，终端状态只能是 writing-plans）：

```dot
digraph brainstorming {
    "Explore project context" → "Visual questions ahead?" → ...
    "User reviews spec?" → "Invoke writing-plans skill" [label="approved"]
}
```

**终端状态约束**：brainstorming 的唯一合法出口是 `writing-plans`，不能直接跳到实现技能。

#### 1.3.4 Iron Law（铁律）模式

用于纪律型技能的核心模式，用极端语言防止 Agent 找借口绕过规则：

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST     (TDD)
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST     (Debugging)
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION      (Verification)
```

配套措施：
- **Rationalization Table**：预判所有合理化借口并逐一反驳
- **Red Flags List**：Agent 自检清单
- **Spirit vs Letter** 封堵："违反字面规则 = 违反精神"

#### 1.3.5 CSO（Claude Search Optimization）

Superpowers 发现的一个关键 Agent 行为模式：**如果技能描述（description field）中包含了工作流摘要，Agent 会只看描述就以为自己懂了，跳过读取完整技能内容**。

解决方案：
- 描述字段 **只写触发条件**（Use when...），不写工作流摘要
- 触发条件要具体、包含症状和关键词

这是 writing-skills 中最重要的元发现之一。

#### 1.3.6 两阶段代码审查

SDD 的独特设计 —— 每个 task 完成后经过两轮独立审查：

| 阶段 | 审查者 | 关注点 | 失败处理 |
|------|--------|--------|----------|
| Stage 1: Spec Compliance | spec-reviewer | 是否完全符合 plan/spec？不多不少？ | implementer 修复 → re-review 循环 |
| Stage 2: Code Quality | code-reviewer | 代码质量、可维护性、测试覆盖 | implementer 修复 → re-review 循环 |

这解决了常见的失败模式：**代码写得很好但不符合需求**。

#### 1.3.7 TDD-for-Skills 元思想

把 TDD 思想应用到技能开发本身：

| TDD 概念 | 技能开发对应物 |
|---------|---------------|
| 测试用例 | 用 subagent 跑压力场景（pressure scenario） |
| 生产代码 | SKILL.md 文档本身 |
| RED（测试失败） | 无技能时 Agent 的基线行为（记录所有 rationalization） |
| GREEN（通过）| 有技能时 Agent 的合规行为 |
| REFACTOR | 发现新漏洞 → 堵住 → 重测 |

这意味着每个技能都应该有对应的压力测试证明其有效性。

### 1.4 优先级层级（用户覆盖的法律基础）

```
优先级 1: 用户显式指令 (CLAUDE.md, GEMINI.md, AGENTS.md, 直接请求)  ← 最高
优先级 2: Superpowers Skills                                        ← 中间
优先级 3: CC 默认 System Prompt                                       ← 最低
```

原文声明：
> If CLAUDE.md or AGENTS.md says "don't use TDD" and a skill says "always use TDD," follow the user's instructions. The user is in control.

### 1.5 主工作流数据流全景

```
用户输入: "我想做个 X 功能"
         │
         ▼
[using-superpowers] ─── 1% 规则评估 ──→ 匹配 brainstorming
         │
         ▼
[brainstorming] ─── 9 步 Checklist:
  ① 探索项目上下文（文件、文档、最近提交）
  ② 提供可视化伴侣（如涉及视觉内容，单独一条消息询问）
  ③ 逐一提问澄清（一次一问，理解目的/约束/成功标准）
  ④ 提出 2-3 方案 + 权衡分析 + 推荐
  ⑤ 分段呈现设计（按复杂度缩放，每段确认）
  ⑥ 写 design doc → docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
  ⑦ Spec 自审（占位符/矛盾/歧义/范围检查）
  ⑧ 用户审核 written spec 文件
  ⑨ 转交 writing-plans（唯一合法出口）
         │
         ▼
[writing-plans] ─── 输出:
  ├── Scope Check（多子系统则拆分）
  ├── File Structure 映射（文件职责分解）
  ├── Bite-Sized Tasks（每步 2-5 分钟）
  ├── 完整代码示例（严格无占位符/TBD/TODO）
  ├── TDD 步骤内联（Red-Green-Refactor per step）
  └── 保存到 docs/superpowers/plans/YYYY-MM-DD-<feature>.md
         │
         ▼
  用户选择执行方式:
  ┌──────────────────────────────────────────────────┐
  │ A: subagent-driven-development (推荐,同会话)      │
  │   每 Task:                                        │
  │   Implementer → Self-Review                       │
  │            → Spec Reviewer (可能循环)              │
  │            → Quality Reviewer (可能循环)           │
  │   → Mark Complete → Next Task                     │
  │   全部完成 → Final Code Reviewer                  │
  │   → finishing-a-development-branch               │
  ├──────────────────────────────────────────────────┤
  │ B: executing-plans (备选,新会话或无线subagent能力)  │
  │   Load Plan → TodoWrite → Execute Sequentially    │
  │   → Blocker 时 Stop and Ask                      │
  │   → finishing-a-development-branch               │
  └──────────────────────────────────────────────────┘
         │
         ▼
[finishing-a-development-branch]
  Step 1: 验证测试通过
  Step 2: 确定基础分支
  Step 3: 提供 4 个选项（合并本地/Push PR/保留/丢弃）
  Step 4: 执行选择
  Step 5: 清理 worktree
```

---

## 二、作为 Agent 用户如何覆盖/定制

### 2.1 方法对比总览

| 方法 | 作用范围 | 改动难度 | 适用场景 |
|------|---------|---------|---------|
| CLAUDE.md 声明 | 当前项目 | 低（纯文本） | 项目级偏好设置 |
| Personal Skills 同名替换 | 个人全局 | 中（需写完整 skill） | 深度修改某个 skill |
| Settings.json 配置 | 个人全局 | 低 | 权限/Hook/环境变量 |
| Fork 源码修改 | 个人全局 | 高（需维护 fork） | 大规模定制 |

### 2.2 方法一：CLAUDE.md 项目级覆盖（最推荐）

在项目 `CLAUDE.md` 中添加规则，利用 superpowers 自身的优先级机制：

```markdown
## Superpowers 定制规则

### 工作流适配
- 本项目是研究与方法论抽象平台，**不需要 TDD 流程**
- 对于研究讨论类任务，**简化 brainstorming 流程**，允许直接进入讨论
- 本项目当前**不是 git 仓库**，跳过 git worktree 隔离要求
- 个人研究项目，**跳过 code review 强制要求**

### 输出偏好
- 中文为主要工作语言，输出和文档优先使用中文
- 分析报告使用结构化 markdown 格式
```

**原理**：superpowers 的 using-superpowers 明确声明了 User Instructions > Superpowers。

### 2.3 方法二：Personal Skills 同名遮蔽

在 `~/.claude/skills/` 创建同名技能目录和 SKILL.md 文件：

```
~/.claude/skills/
  brainstorming/SKILL.md           ← 你的自定义版本（优先于 superpowers）
  test-driven-development/SKILL.md ← 你的宽松版本
  systematic-debugging/SKILL.md    ← 你的变体
```

适用场景：
- 保留框架但大幅修改具体流程
- 为特定类型的项目创建变体
- 移除某些强制性约束

### 2.3 方法三：Settings.json 配置

通过 `/config` skill 或直接编辑：
- **权限管理**：允许/禁止特定命令类型
- **Hook 管理**：修改或禁用 SessionStart hook
- **环境变量**：项目特定的环境配置

### 2.4 方法四：Fork & 修改源码

Fork [obra/superpowers](https://github.com/obra/superpowers) 仓库，从自己的 fork 安装。

适用场景：
- 需要修改核心机制（如 1% 规则、优先级逻辑）
- 需要新增技能类型
- 想贡献改进回社区

---

## 三、不足与优化方向

### 3.1 结构性缺陷

#### 缺陷 #1：编程中心主义（Coding-Centric Bias）

**现象**：整个管道为"写代码功能"设计，对非编码任务支持极差。

**对 Harness Creator 的影响矩阵**：

| 你常做的任务 | Superpowers 的响应 | 问题严重度 |
|-------------|-------------------|-----------|
| 研究某个技术领域 | 强制走 brainstorming(9步) → design doc → plan | 高 - 过重且不匹配 |
| 写分析报告 | 没有"写作"技能，只有"写代码"管道 | 高 - 缺失能力 |
| 讨论产品方向 | HARD-GATE 禁止非设计输出 | 中 - 阻塞自然对话 |
| 对比分析多个方案 | 只有 brainstorming 的 2-3 方案对比 | 中 - 太轻量 |
| 方法论抽象/建模 | 无相关技能 | 高 - 核心活动缺失 |
| 整理调研笔记 | 无相关技能 | 中 - 日常需求缺失 |

**优化建议**：新建 **Research Pipeline** 和 **Analysis Pipeline** 技能，类似 brainstorming 但输出是 insight/doc 而非 design spec。

#### 缺陷 #2：全有或全无（All-or-Nothing）

**现象**：无论任务复杂度如何，都走同样的完整管道。

| 任务复杂度 | Superpowers 开销 | 合理开销 |
|-----------|-----------------|---------|
| 改一行配置 | brainstorming(9步) → plan → SDD(3 subagent/task) | 直接改 |
| 加一个函数 | 同上 | 简化 brainstorming → 直接实现 |
| 建一个模块 | 合理 | 合理 |
| 建一个系统 | 合理 | 合理 |

**优化建议**：增加 **complexity-aware routing**（复杂度感知路由），根据任务规模自动选择重量级或轻量级流程。

#### 缺陷 #3：TDD 教条主义

**现象**：TDD skill 使用极端表述，不允许例外（除非用户明确许可）。

不适用的场景：
- 数据分析和探索性编程
- 原型和 MVP 验证
- 配置文件和基础设施代码
- 文档生成和转换脚本
- Harness Creator 本身（方法论抽象产出物）

**优化建议**：创建 **context-aware TDD** 变体 —— 只在有测试框架的项目中强制 TDD，其他场景降级为"建议测试"。

#### 缺陷 #4：Token 成本爆炸

**现象**：SDD 模式下 token 消耗是直接实现的 3-5 倍。

计算模型：
```
每个 Task = Implementer(1次) + Spec Reviewer(1-N次) + Quality Reviewer(1-N次)
假设平均 1.5 次审查循环:
  10 Tasks × (1 + 1.5 + 1.5) = 40 次 subagent 调用
加上 controller 构建上下文的成本...
```

**优化建议**：
- **Risk-based review**：简单 task 跳过 quality review
- **Batch review**：多个简单 task 合并一次审查
- **Cost estimate**：执行前预估 token 消耗，让用户决策

### 3.2 工作流缺陷

#### 缺陷 #5：缺少 Research/Investigation 技能

**现象**：14 个技能中没有专门用于调查研究的。

缺失的能力清单：
- **文献综述**：收集、整理、对比多来源信息
- **竞品分析**：系统性对比多个方案/产品
- **技术决策记录（ADR）**：记录决策理由和替代方案
- **知识提取**：从代码/文档中提炼模式和洞察
- **信息架构整理**：将碎片化信息组织为结构化知识

#### 缺陷 #6：Brainstorming 的 HARD-GATE 对非编码任务过严

**原文**：
> Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it.

**问题**：当用户只想"帮我分析下这个架构"或"帮我整理下这些笔记"时，这个 gate 不必要地阻塞工作流。

**优化建议**：增加 **task-type detection** —— 区分 creative/building vs analytical/discussion，后者走简化流程。

#### 缺陷 #7：Writing-Plans 的 "Zero Context" 假设

**原文**：
> Assume the engineer has zero context for our codebase and questionable taste.

**问题**：SDD 在同一会话中执行时，controller 已经理解了项目。"Zero context" 导致 plan 冗长、token 浪费、implementer 收到过多信息。

**优化建议**：增加 **context-sharing level** 参数 —— 同会话 SDD 使用 shared context 模式，减少重复信息。

#### 缺陷 #8：Git 依赖过深

**受影响的技能**：using-git-worktrees, subagent-driven-development, executing-plans, finishing-a-development-branch, requesting-code-review

几乎每个执行技能都依赖 git 操作。对于：
- 非 git 仓库项目
- 纯文档项目
- 研究笔记项目

整套执行管道无法运行。

**优化建议**：增加 **VCS-agnostic mode** —— 将版本控制操作解耦为可选插件而非硬编码依赖。

### 3.3 心理学与体验缺陷

#### 缺陷 #9：对抗性语气（Adversarial Tone）

**典型用语**：
- "This is not negotiable. This is not optional."
- "You do not have a choice. You cannot rationalize your way out."
- "If you haven't completed Phase 1, you cannot propose fixes."
- "ALL of these mean: STOP. Return to Phase 1."

**正面效果**：有效防止 Agent 绕过规则（从 release notes 可见，v3.2.2 加入 EXTREMELY-IMPORTANT 块后合规率显著提升）

**负面效果**：
- 协作感觉像"管教"而非"合作"
- 可能导致 Agent 过度保守（因害怕违规而不敢行动）
- 对习惯平等协作的用户感到不适
- 在中文语境下更加突兀

**优化建议**：保留防御机制的效果，但调整语气。例如用"护栏"隐喻替代"命令"语气。

#### 缺陷 #10：缺少自适应机制

Superpowers 不会根据以下因素调整行为：

| 因素 | 当前行为 | 理想行为 |
|------|---------|---------|
| 对话历史 | 已讨论过的方案不简化 | 利用历史避免重复提问 |
| 用户熟练度 | 新手=专家=相同引导量 | 专家获得精简模式 |
| 任务类型 | 编码=研究=讨论=相同管道 | 不同类型不同路由 |
| 会话阶段 | 第1次=N次=相同流程 | 后续交互简化 |
| 失败历史 | 某方法失败后不自适应 | 自动回避已失败的路径 |

#### 缺陷 #11：1% 规则的恒定开销

**原文**：
> If you think there is even a 1% chance a skill might apply... you ABSOLUTELY MUST invoke the skill

**影响**：每条用户消息都可能触发 Skill Tool 调用，即使最终不适用。在高频对话中不可忽视。

**优化建议**：增加 **cache-and-invalidate** 机制 —— 同类任务在同一会话中后续出现时复用之前的判断结果。

### 3.4 对 Harness Creator 的匹配度评估

| 维度 | 匹配度 | 说明 |
|------|-------|------|
| 功能开发（如构建 Harness 运行时） | **高** | 完整管道适用 |
| 技术调研 | **低** | 缺少研究管道，brainstorming 不匹配 |
| 方法论抽象/建模 | **很低** | 输出是文档/spec，不是代码 |
| 文档写作 | **无** | 没有写作技能 |
| 架构设计 | **中** | brainstorming 可用但需适配 |
| 竞品/平台分析 | **无** | 没有分析/对比技能 |
| 产品方向讨论 | **低** | HARD-GATE 阻塞讨论式工作 |
| 多项目/跨领域协调 | **无** | 没有跨项目协调机制 |
| 知识管理/沉淀 | **无** | 没有知识提取/整理技能 |

**结论**：Superpowers 解决了"如何让 Agent 规范地写代码"的问题，但 Harness Creator 的核心活动是"如何让 Agent 规范地做研究和抽象"。两者有交集但不重合。

---

## 四、总结

### 4.1 Superpowers 的核心价值（值得保留/借鉴的）

| 价值点 | 说明 | 可借鉴程度 |
|--------|------|-----------|
| **纪律性框架** | 防止 Agent "裸奔"——直接动手不做思考 | 高 - 可适配到研究场景 |
| **DOT 流程图权威定义** | 形式化流程 > 纯文本描述 | 很高 - 可直接采用 |
| **Rationalization 防御** | 预判+堵塞 Agent 借口的模式 | 很高 - 核心方法论创新 |
| **CSO 理论** | Agent 如何"作弊"跳过技能的洞察 | 高 - 设计 Harness Skill 时必须考虑 |
| **TDD-for-Skills 元思想** | 用 TDD 验证技能有效性 | 高 - Harness Skill 质量保障方法 |
| **两阶段审查分离** | Spec 合规 vs 代码质量的解耦 | 中 - 适用于需要质量门控的场景 |
| **优先级层级设计** | User > Skills > Default | 很好 - 应成为 Harness 的设计原则 |
| **HARD-GATE 模式** | 阶段门控防止跳步 | 中 - 需要软化以适应研究场景 |
| **Subagent 隔离** | 每次 dispatch 提供精确上下文 | 高 - 上下文工程的好实践 |

### 4.2 最需要的定制（按优先级排序）

| 优先级 | 定制项 | 推荐方法 | 预期收益 |
|--------|--------|---------|---------|
| **P0** | 添加 Research/Analysis Pipeline 技能 | 新建 personal skill | 补足核心能力缺口 |
| **P0** | CLAUDE.md 声明项目特性（非编码、非git、中文） | 编辑 CLAUDE.md | 立即消除大部分不匹配 |
| **P1** | 轻量模式开关（简单任务跳过重型流程） | personal skill 或 CLAUDE.md 规则 | 减少日常开销 |
| **P1** | 中文输出偏好 + 结构化格式约定 | CLAUDE.md | 提升协作体验 |
| **P2** | 成本感知执行（预估 token 再决定是否 SDD） | 修改 SDD 或新建变体 | 控制使用成本 |
| **P2** | 非编码任务的完整适配方案 | 新建一组 research-oriented skills | 全面支撑 Harness Creator 工作流 |

### 4.3 对 Harness Creator 项目的启示

Superpowers 本身就是一个 **Harness 的实例** —— 它把"规范化软件开发"这套方法论编码成了 Agent 可消费的 Skills。从这个角度看：

1. **Superpowers 是最好的参照物**：它展示了如何将一套工程方法论转化为 Agent 技能体系
2. **它的局限就是 Harness Creator 的机会**：Superpowers 只覆盖了"编码"环节，Harness Creator 可以覆盖 SDLC 全链路的研究/设计/抽象环节
3. **CSO 和 Rationalization 防御是通用技术**：设计 Harness Skill 时必须内置这些防御机制
4. **DOT 流程图 + Iron Law + Red Flags 是可组合的设计模式**：可以用来构建任意领域的 Harness

---

*本报告基于 Superpowers v5.0.7 全部 14 个 SKILL.md 及其 supporting files 的逐行阅读分析。*
