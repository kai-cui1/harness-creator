# GSD-2 (gsd-build/gsd-2) 深度调研报告

> 调研日期：2026年4月22日
> 项目地址：https://github.com/gsd-build/gsd-2
> 报告类型：全维度技术 + 产品 + 用户评价深度拆解

---

## 一、项目概览

| 属性 | 详情 |
|------|------|
| **全名** | GSD 2 (Get Shit Done 2) |
| **GitHub** | https://github.com/gsd-build/gsd-2 |
| **Stars** | ~4,700+ |
| **Forks** | ~480+ |
| **许可证** | MIT |
| **主语言** | TypeScript (~89.5%) |
| **运行时** | Node.js >= 22.0.0 |
| **当前版本** | v2.77.0 |
| **创建时间** | 2025年1月17日 |
| **最近提交** | 2026年4月21日（活跃） |
| **贡献者** | 100+ |
| **Open Issues** | 180 |
| **Open PRs** | 218 |
| **Merged PRs** | 1,932+ |
| **Discussions** | 1,650+ 帖子 |
| **npm 包名** | `gsd-pi` |
| **社区** | Discord: https://discord.gg/gsd |

### 版本迭代速度

从 v1.0 到 v2.77.0，约 **15 个月内发布了 77 个主版本**，平均每 **3-5 天**一个新版本。迭代节奏极快。

---

## 二、解决什么问题

### 2.1 背景：从 GSD v1 到 GSD v2

GSD 的前身是 **GSD v1 (Get Shit Done)** — 一个在 Claude Code 社区爆火的 prompt 框架。v1 本质上是一组安装到 `~/.claude/commands/` 的 Markdown 提示词模板，它"意外地"效果很好。

但 v1 存在**四大根本性硬伤**：

| # | 硬伤 | 具体表现 |
|---|------|---------|
| 1 | **无上下文控制** | LLM 在长会话中累积垃圾信息（Context Rot），质量持续下降 |
| 2 | **无真正自动化** | "Auto mode" 实际上是 LLM 调用自身的循环，在编排开销上燃烧上下文 |
| 3 | **无崩溃恢复** | 会话中途死亡就得从头开始，所有进度丢失 |
| 4 | **无可观测性** | 无成本追踪、无进度仪表板、无卡死检测 |

### 2.2 GSD v2 的定位

> **"The evolution of Get Shit Done -- now a real coding agent."**
>
> **"One command. Walk away. Come back to a built project with clean git history."**

GSD v2 不再是一个 prompt 框架，而是一个基于 **Pi SDK** 构建的**独立 TypeScript CLI 应用程序**。它直接控制 Agent Session，能够：

- 在任务之间**清除上下文**（每个 Task 使用全新的 200k token 窗口）
- 在调度时**精确注入正确的文件**
- 管理 **Git Worktree/Branch 隔离**
- 追踪**成本和 Token 用量**
- 检测**卡死循环**（滑动窗口检测）
- 从**崩溃中恢复**（锁文件 + JSONL 取证）
- 自动推进整个**里程碑**而无需人工干预

### 2.3 核心问题定义

GSD v2 要解决的根本问题是：

> **如何让 AI 编程 Agent 能够长时间自主工作而不丢失大局观？**

具体拆解为 5 个子问题：

1. **上下文污染问题** — LLM 长会话中的注意力稀释（Context Rot）
2. **编排开销问题** — Agent 自我调度的元对话消耗大量 Token
3. **可靠性问题** — 长时间运行的进程崩溃、API 超时、模型幻觉
4. **可观测性问题** — 不知道 Agent 在做什么、花了多少钱、进度如何
5. **工程化问题** — Git 历史、代码质量、测试覆盖等工程实践缺失

### 2.4 目标用户

| 用户类型 | 核心诉求 | 使用方式 |
|---------|---------|---------|
| 独立开发者 / Solo Founder | 快速构建 MVP，一个人当整个团队用 | `/gsd auto` 全自动 |
| 自由职业者 / Freelancer | 提高交付效率，降低成本 | Step Mode + Auto Mode 结合 |
| 初创公司 CTO / 技术负责人 | 规范化团队 AI 辅助开发流程 | 团队共享配置 + Worktree 协作 |
| AI Coding 早期采用者 | 寻找最佳 AI 工作流 | 探索全部功能 |

---

## 三、产品设计分析

### 3.1 产品功能全景图

```
GSD 2 功能全景
│
├── 核心执行模式
│   ├── Step Mode (/gsd)        — 单步交互执行 ★ 入门推荐
│   ├── Auto Mode (/gsd auto)    — 全自动状态机驱动 ★ 核心卖点
│   └── Quick Mode (/gsd quick)  — 快速任务跳过规划
│
├── 工作层级体系 (Work Hierarchy)
│   ├── Milestone (里程碑)       — 可交付版本，包含 4-10 个 Slices
│   ├── Slice (切片)             — 可演示垂直功能，包含 1-7 个 Tasks
│   └── Task (任务)              — 单个上下文窗口的工作单元 (~200k tokens)
│
├── 流水线阶段 (The Loop)
│   Research → Plan → Execute → Complete → Reassess → Next Slice
│   └── Validate Milestone → Complete Milestone
│
├── Auto Mode 子系统 (12 项核心能力)
│   ├── Fresh session per unit     — 每任务全新上下文窗口
│   ├── Context pre-loading        — 上下文预注入
│   ├── Git isolation              — Git Worktree/Branch 隔离
│   ├── Crash recovery             — 崩溃恢复 (锁文件 + 取证)
│   ├── Stuck detection            — 卡死检测 (滑动窗口)
│   ├── Timeout supervision        — 超时监督 (软/空闲/硬三级)
│   ├── Cost tracking              — 成本追踪 (按阶段/切片/模型细分)
│   ├── Adaptive replanning        — 自适应重新规划
│   ├── Verification enforcement   — 验证强制执行
│   ├── Provider error recovery    — Provider 错误恢复
│   ├── Milestone validation       — 里程碑验证门控
│   └── Escape hatch               — Esc 键暂停逃生舱
│
├── 上下文工程 (Context Engineering) ★ 核心差异化
│   ├── PROJECT.md      — 项目活文档
│   ├── DECISIONS.md    — 架构决策注册表 (ADR)
│   ├── KNOWLEDGE.md    — 跨会话规则和经验教训
│   ├── STATE.md        — 状态仪表板
│   ├── ROADMAP.md      — 里程碑计划
│   ├── CONTEXT.md      — 用户决策记录
│   ├── RESEARCH.md     — 代码库研究结果
│   ├── PLAN.md         — Slice/Task 计划分解
│   ├── SUMMARY.md      — 执行摘要
│   └── UAT.md          — 用户验收测试脚本
│
├── Token 优化系统
│   ├── Budget Profile   — 40-60% Token 节省
│   ├── Balanced Profile — 10-20% 节省
│   ├── Quality Profile  — 全功率输出
│   ├── Complexity-based Routing — 复杂度路由 (简单任务→便宜模型)
│   └── Budget Pressure Graduation — 预算压力降级
│
├── Git 策略
│   ├── Worktree Isolation — 每个 Slice 在独立 worktree 中执行
│   ├── Branch Isolation   — 独立分支隔离
│   ├── Sequential Commits — 顺序提交
│   └── Squash Merge       — Squash 合并到 main 保持历史干净
│
├── 扩展生态 (24 个内置扩展)
│   ├── GSD Core           — 核心引擎
│   ├── Browser Tools      — Playwright 浏览器自动化
│   ├── Search (Brave/Tavily/Jina) — 网络搜索
│   ├── Google Search      — Gemini 搜索
│   ├── Context7           — 库/框架文档查询
│   ├── Background Shell   — 后台进程管理
│   ├── Async Jobs         — 异步任务
│   ├── Subagent           — 子代理委派
│   ├── GitHub             — Issues/PR 管理
│   ├── Mac Tools          — macOS 自动化
│   ├── MCP Client         — MCP 服务器集成
│   ├── Voice              — 语音转文字
│   ├── Slash Commands     — 自定义命令
│   ├── Secure Env Collect — 安全凭证收集
│   ├── Remote Questions   — 远程决策路由 (Slack/Discord)
│   ├── Universal Config   — 配置导入
│   ├── AWS Auth           — AWS 凭证刷新
│   ├── Ollama             — 本地 LLM 支持
│   ├── Claude Code CLI    — 外部 Provider
│   ├── cmux               — Claude 多路复用
│   ├── GitHub Sync        — GitHub 同步
│   ├── LSP                — 语言服务器协议
│   └── TTSR               — 工具触发规则
│
├── 子代理系统 (5 个专用子代理)
│   ├── Scout            — 代码库侦察
│   ├── Researcher       — 网络研究
│   ├── Worker           — 通用执行
│   ├── JavaScript Pro   — JS 专用
│   └── TypeScript Pro   — TS 专用
│
├── 可观测性
│   ├── Dashboard Overlay (Ctrl+Alt+G) — 终端内仪表板覆盖层
│   ├── HTML Reports                  — HTML 格式报告
│   ├── Cost Projections              — 成本预测
│   ├── Debug Mode (--debug)          — 调试模式
│   ├── Forensics (/gsd forensics)    — 取证分析
│   └── Doctor (/gsd doctor)          — 健康检查
│
├── Headless / CI 模式
│   ├── gsd headless            — 无 TUI 执行
│   ├── gsd headless query      — 即时 JSON 状态查询
│   ├── gsd headless next       — 单步执行 (cron 友好)
│   ├── 结构化退出码 (0/1/2)    — 成功/失败/阻塞
│   ├── 崩溃自动重启 + 指数退避
│   └── Remote Questions         — 决策路由到 Slack/Discord
│
└── VS Code 扩展
    ├── Chat Participant  — 聊天参与者集成
    ├── Sidebar Dashboard — 侧边栏仪表板
    └── RPC Integration   — RPC 通信
```

### 3.2 用户交互流程

#### 基础使用流程

```
1. 安装
   npm install -g gsd-pi@latest

2. 登录 Provider
   gsd → /login → 选择 20+ Provider 之一 (OAuth 或 API Key)

3. 启动
   gsd → 打开交互式 Agent Session

4a. Step Mode (推荐入门)
    /gsd → 逐步执行，每个单元暂停确认

4b. Auto Mode (核心体验)
    /gsd auto → 全自动执行，可以离开电脑

5. 监控/干预 (另一个终端)
    /gsd status    → 进度仪表板
    /gsd discuss   → 讨论架构决策
    Ctrl+Alt+G     → 切换 Dashboard 覆盖层
```

#### 双终端工作流（推荐生产用法）

```
Terminal 1 — 让它构建:
  gsd
  /gsd auto          ← 启动全自动模式

Terminal 2 — 同时操控:
  gsd
  /gsd discuss       ← 讨论架构决策（写入 CONTEXT.md）
  /gsd status        ← 查看进度
  /gsd queue         ← 排队下一个里程碑

  ← 两个终端读写同一个 .gsd/ 目录
  ← Terminal 2 的决策在下一阶段边界被自动采纳
```

#### 新项目启动的智能流程

```
无 .gsd/ 目录
    ↓
启动讨论流 → 捕获愿景、约束、偏好
    ↓
生成 PROJECT.md + M001-ROADMAP.md
    ↓
Milestone 存在但无 Roadmap
    ↓
讨论/研究 Milestone → 生成 ROADMAP.md
    ↓
Roadmap 存在且有待处理 Slices
    ↓
规划下一 Slice 或执行一个 Task
    ↓
任务中途崩溃 → 从中断处恢复（锁文件 + JSONL 取证）
```

### 3.3 三大工作流引擎

GSD 支持三种工作流引擎，通过策略模式切换：

| 引擎 | 文件 | 说明 |
|------|------|------|
| **DevWorkflowEngine** | `dev-workflow-engine.ts` | 默认引擎，Milestone → Slice → Task 三层标准分解 |
| **CustomWorkflowEngine** | `custom-workflow-engine.ts` | 基于 GRAPH.yaml 的用户自定义工作流，支持迭代展开 |
| **EngineResolver** | `engine-resolver.ts` | 引擎解析器，根据配置选择使用哪个引擎 |

---

## 四、代码实现深度分析

### 4.1 整体架构：Monorepo + 扩展系统 + 状态机

```
┌─────────────────────────────────────────────────────────────┐
│                     用户层 (User Layer)                       │
│  CLI / Web UI / Headless / RPC / MCP                         │
├─────────────────────────────────────────────────────────────┤
│                    入口层 (Entry Layer)                       │
│  loader.ts (零 SDK 引导) → cli.ts (7 种模式路由)             │
├─────────────────────────────────────────────────────────────┤
│                  会话层 (Session Layer)                       │
│  SessionManager · ModelRegistry · SettingsManager            │
├─────────────────────────────────────────────────────────────┤
│                 扩展层 (Extension Layer)                      │
│  DefaultResourceLoader → Extension Registry                  │
│  ┌─────────────┬─────────────┬──────────────┐               │
│  │ gsd (内置)   │ 第三方扩展   │ MCP 工具服务   │               │
│  │ 24个模块     │ Extension API│ 外部工具集成   │               │
│  └─────────────┴─────────────┴──────────────┘               │
├─────────────────────────────────────────────────────────────┤
│              工作流引擎层 (Workflow Engine)                    │
│  DevWorkflowEngine · CustomWorkflowEngine                    │
│  EngineResolver (策略选择)                                    │
├─────────────────────────────────────────────────────────────┤
│              状态机层 (State Machine Layer)                    │
│  auto-loop.ts (主循环)                                       │
│  auto-dispatch.ts (声明式调度表 - 20+ 规则)                   │
│  auto-supervisor.ts (监督器)                                 │
│  auto-recovery.ts (崩溃恢复)                                 │
├─────────────────────────────────────────────────────────────┤
│              持久化层 (Persistence Layer)                     │
│  SQLite (gsd.db) · 文件系统 (.gsd/) · JSONL (会话日志)       │
│  Git Worktree (隔离执行)                                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 关键源码模块解读

#### 模块 1：双文件加载器 (`src/loader.ts`, 224 行)

这是整个项目最关键的架构决策。设计原则是**"在导入任何 SDK 之前设置所有环境变量"**：

```typescript
// 核心设计：零 SDK 导入的引导阶段
const pkgDir = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'pkg')
process.env.PI_PACKAGE_DIR = pkgDir          // Pi SDK 包目录
process.env.PI_SKIP_VERSION_CHECK = '1'
process.title = 'gsd'

// 设置关键环境变量
process.env.GSD_CODING_AGENT_DIR = agentDir   // ~/.gsd/agent/
process.env.GSD_PKG_ROOT = gsdRoot
process.env.GSD_VERSION = gsdVersion
process.env.GSD_BIN_PATH = process.argv[1]
process.env.GSD_WORKFLOW_PATH = join(resourcesDir, 'GSD-WORKFLOW.md')
process.env.GSD_BUNDLED_EXTENSION_PATHS = serializeBundledExtensionPaths(...)

// Workspace 包链接（Windows 兼容回退）
const wsPackages = ['native', 'pi-agent-core', 'pi-ai', 'pi-coding-agent', 'pi-tui']
try { symlinkSync(source, target, 'junction') }
catch { try { cpSync(source, target, { recursive: true }) } catch {} }

// 延迟动态导入 —— 推迟 ESM 求值
await import('./cli.js')
```

**为什么这样设计？** 解决了 ESM 模块环境下 SDK 依赖的鸡生蛋问题。loader.ts 完全不 import 任何 SDK，只做环境准备，然后动态 import cli.js。

#### 模块 2：主 CLI 入口 (`src/cli.ts`, ~800 行)

```typescript
// 阶段 1: V8 编译缓存（Node 22+ 特性）
if (parseInt(process.versions.node) >= 22) {
  process.env.NODE_COMPILE_CACHE ??= join(agentDir, '.compile-cache')
}

// 阶段 2: 参数解析与快速子命令路由
const cliFlags = parseCliArgs(process.argv)
// 处理: update, graph, config, web, sessions, headless, auto, worktree, list-models

// 阶段 3: 认证与模型初始化
const authStorage = AuthStorage.create(authFilePath)
loadStoredEnvKeys(authStorage)
migratePiCredentials(authStorage)
const modelRegistry = new ModelRegistry(authStorage, modelsJsonPath)

// 阶段 4: 资源加载与扩展初始化
initResources(agentDir)
const resourceLoader = buildResourceLoader(agentDir)
await resourceLoader.reload()

// 阶段 5: 会话创建
const { session, extensionsResult } = await createAgentSession({...})

// 阶段 6: 模式分发（7 种运行模式）
//   Interactive TUI / Print / RPC / MCP / Text / Web / Headless-Auto
```

**支持的 7 种运行模式**：
| 模式 | 触发方式 | 用途 |
|------|---------|------|
| Interactive TUI | 默认 | 交互式终端界面 |
| Print | `--print` | 单次提示词执行 |
| RPC | `--mode rpc` | JSON-RPC over stdin/stdout |
| MCP | `--mode mcp` | MCP 协议服务端 |
| Text | `--mode text` | 纯文本输出 |
| Web | `--web` | 浏览器 Web 模式 |
| Headless/Auto | `headless`/`auto` | 无 TUI 全自动 |

#### 模块 3：调度中枢 (`auto-dispatch.ts`, 1083 行) — 项目最复杂的单文件

这是 GSD Auto Mode 的**大脑**。采用**声明式的规则匹配表（Dispatch Table）**替代 if-else 链：

```typescript
/**
 * Auto-mode Dispatch Table — 声明式 phase -> unit 映射。
 * 每条规则将 GSD 状态映射到 unit 类型、unit ID 和 prompt builder。
 * 规则按顺序求值；第一个匹配的胜出。
 */
export interface DispatchRule {
  name: string;
  match: (ctx: DispatchContext) => Promise<DispatchAction | null>;
}

export const DISPATCH_RULES: DispatchRule[] = [
  // 规则 1: 升级暂停（最高优先级）
  { name: "escalating-task → pause-for-escalation", ... },

  // 规则 2: 文档重写覆盖门控
  { name: "rewrite-docs (override gate)", ... },

  // 规则 3-5: 完成后流程
  { name: "summarizing → complete-slice", ... },
  { name: "run-uat (post-completion)", ... },       // UAT 测试调度
  { name: "uat-verdict-gate (non-PASS blocks)", ... }, // UAT 裁决门控

  // 规则 6: 路线图重新评估
  { name: "reassess-roadmap (post-completion)", ... },

  // 规则 7-9: pre-planning 阶段
  { name: "needs-discussion → discuss-milestone", ... },
  { name: "pre-planning (no context) → discuss-milestone", ... },
  { name: "pre-planning (no research) → research-milestone", ... },
  { name: "pre-planning (has research) → plan-milestone", ... },

  // 规则 10-13: planning 阶段
  { name: "planning (multiple slices need research) → parallel-research-slices", ... },
  { name: "planning (no research, not S01) → research-slice", ... },
  { name: "refining → refine-slice", ... },           // 渐进式规划 (ADR-011)
  { name: "planning → plan-slice", ... },

  // 规则 14-16: executing 阶段
  { name: "evaluating-gates → gate-evaluate", ... },
  { name: "executing → reactive-execute (parallel dispatch)", ... }, // 并行执行
  { name: "executing → execute-task", ... },

  // 规则 17-18: 验证与完成
  { name: "validating-milestone → validate-milestone", ... },
  { name: "completing-milestone → complete-milestone", ... },
];
```

**安全防护机制（Safety Guards）**：
| 防护 | 实现 | 作用 |
|------|------|------|
| Rewrite Circuit Breaker | `MAX_REWRITE_ATTEMPTS = 3` | 限制文档最大重写次数 |
| UAT Circuit Breaker | `MAX_UAT_ATTEMPTS = 3` | 每 Slice 的 UAT 尝试上限 |
| SUMMARY 缺失检测 | 验证前检查 | 确保 Slice 有执行摘要 |
| VALIDATION 裁决门控 | `needs-remediation` 裁决 | 验证不通过阻止完成 |
| 实现产物检查 | 非 `.gsd/` 目录变更检测 | 确保产生了实际代码 |
| DB/磁盘不一致调和 | #4658 | SUMMARY 与 DB 状态不一致时自动修复 |

#### 模块 4：自定义工作流引擎 (`custom-workflow-engine.ts`, 245 行)

```typescript
export class CustomWorkflowEngine implements WorkflowEngine {
  readonly engineId = "custom";

  // 从 GRAPH.yaml 派生引擎状态
  async deriveState(_basePath: string): Promise<EngineState> {
    const graph = readGraph(this.runDir);
    const allDone = graph.steps.every(s =>
      s.status === "complete" || s.status === "expanded"
    );
    return { phase: allDone ? "complete" : "running", ... };
  }

  // 解析下一个调度动作（支持迭代展开）
  async resolveDispatch(state, context): Promise<EngineDispatchAction> {
    // 支持迭代(iterate)配置：从源工件正则提取项目并展开为实例步骤
    if (stepDef?.iterate) {
      // ReDoS 防护：5 秒超时
      const items = extractItemsWithTimeout(
        iterate.pattern, sourceContent, 5000
      );
      const expandedGraph = expandIteration(
        graph, next.id, items, next.prompt
      );
    }
    return { action: "dispatch", step: { unitType, unitId, prompt } };
  }

  // 步骤完成后调和状态（文件锁保证原子性）
  async reconcile(state, completedStep): Promise<ReconcileResult> {
    return await withFileLock(graphPath, () => { ... });
  }
}
```

**关键特性**：迭代展开（Iterate Expansion）、ReDoS 防护、文件锁并发控制、上下文注入。

#### 模块 5：核心扩展目录结构 (`src/resources/extensions/gsd/`)

这是项目的**心脏**，包含 80+ 个 TypeScript 文件：

| 子目录 | 文件数 | 职责 |
|--------|:-----:|------|
| `auto/*` | ~20 | Auto Mode 状态机核心（主循环/调度/监督/恢复/超时/预算/仪表板...） |
| `commands/*` | ~15 | 命令实现（bootstrap/config/handlers/inspect/logs/mcp-status...） |
| `doctor/*` | 10+ | 诊断与健康检查系统 |
| `bootstrap/*` | — | 项目引导逻辑 |
| `templates/*` | — | 模板引擎 |
| `tools/*` | — | 工具定义 |
| `watch/*` | — | 文件监听 |
| `skills/gsd-headless/*` | — | 无头技能 |
| `workflow-templates/*` | — | 工作流模板 |
| `prompts/*` | — | 提示词模板 |
| `safety/*` | — | 安全策略 |
| `migrate/*` | — | 迁移脚本 |
| `tests/*` | — | 测试用例 |

**扁平核心模块文件**（位于 `gsd/` 根目录）：

| 文件 | 职责 |
|------|------|
| `context-store.ts` | 状态存储管理 |
| `db-writer.ts` | SQLite 持久化写入 |
| `context-injector.ts` | 上下文注入引擎 |
| `context-masker.ts` | 敏感信息遮蔽 |
| `context-budget.ts` | Token 预算管理 |
| `config-overlay.ts` | 配置覆盖层 |
| `preferences.ts` | 用户偏好管理 |
| `execution-policy.ts` | 执行策略定义 |
| `custom-workflow-engine.ts` | 自定义工作流引擎 |
| `dev-workflow-engine.ts` | 默认开发工作流引擎 |
| `crash-recovery.ts` | 崩溃恢复机制 |
| `error-classifier.ts` | 错误分类器 |
| `complexity-classifier.ts` | 任务复杂度分类 |
| `dashboard-overlay.ts` | 终端仪表板覆盖层 |
| `atomic-write.ts` | 原子文件写入 |
| `branch-patterns.ts` | Git 分支命名模式 |
| `file-watcher.ts` | 文件系统监听 |
| `activity-log.ts` | 活动日志 |
| `dispatch-guard.ts` | 调度守卫 |
| `export-html.ts` | HTML 报告导出 |
| `definition-loader.ts` | 定义加载器 |
| `cache.ts` | 缓存管理 |
| `captures.ts` | 截图/捕获 |
| `changelog.ts` | 变更日志 |
| `exit-command.ts` | 退出命令处理 |
| `env-utils.ts` | 环境变量工具 |
| `debug-logger.ts` | 调试日志 |
| `codebase-generator.ts` | 代码库描述生成 |
| `claude-import.ts` | Claude 配置导入 |
| `diff-context.ts` | 差异上下文 |
| `collision-diagnostics.ts` | 冲突诊断 |
| `detection.ts` | 状态检测 |

### 4.3 完整数据流

```
用户输入 (goal/prompt)
    │
    ▼
[loader.ts] 零依赖引导 — 设置 PI_PACKAGE_DIR 等 15+ 环境变量
    │  (--version/--help 快速路径直接返回)
    ▼
[cli.ts] 模式路由 (7 种运行模式) + 初始化
    │  ├─→ Print/RPC/MCP/Text/Web: 各自独立处理
    │  └─→ Interactive/Headless: 进入会话循环
    │
    ▼
[auto-loop.ts] 主状态机循环 (Auto Mode)
    │
    ▼
[auto-dispatch.ts] DISPATCH_RULES 匹配 (20+ 条规则按优先级求值)
    │  第一条匹配的 rule 胜出 (first-match-wins)
    ▼
[auto-prompts.ts] 构建 Prompt
    │  注入: 任务计划 + 摘要 + 路线图 + 上下文预算
    ▼
[context-injector.ts] 上下文注入 (多层装饰器)
    │  基础 prompt → 任务摘要 → 前置步骤产物 → 路线图 → Token 裁剪 → 敏感遮蔽
    ▼
LLM 执行 (Anthropic/OpenAI/Google/Ollama/其他 20+ Provider)
    │
    ▼
[auto-post-unit-closeout.ts] 后置处理
    │  写入 SUMMARY.md / UAT.md / VERDICT 到磁盘
    ▼
[auto-recovery.ts] 崩溃恢复检查
    │  锁文件存在? → JSONL 取证分析 → 断点续跑
    ▼
回到 [auto-loop.ts] 下一次迭代
```

### 4.4 设计模式识别

| # | 模式 | 所在文件 | 说明 |
|---|------|---------|------|
| 1 | **策略模式** | engine-types.ts + 两个 WorkflowEngine | 工作流引擎可切换 |
| 2 | **责任链模式** | auto-dispatch.ts | 20+ 条 Dispatch Rules 构成匹配链 |
| 3 | **状态机模式** | auto-loop.ts + .gsd/ 文件系统 | 磁盘驱动的有限状态机 |
| 4 | **观察者模式** | file-watcher.ts (chokidar) | 文件变化触发状态重派发 |
| 5 | **装饰器模式** | context-injector.ts | Prompt 多层装饰增强 |
| 6 | **工厂模式** | cli.ts createAgentSession() | 多模式 Session 创建 |
| 7 | **断路器模式** | auto-dispatch.ts | Rewrite/UAT 最大尝试次数限制 |
| 8 | **模板方法模式** | engine-types.ts WorkflowEngine 接口 | deriveState→dispatch→reconcile 骨架 |
| 9 | **适配器模式** | cli.ts MCP 模式 | 内部工具适配为 MCP 协议 |
| 10 | **外观模式** | resource-loader.ts | 复杂扩展加载封装为 reload() |

### 4.5 代码质量评估

| 维度 | 评分 | 说明 |
|------|:----:|------|
| 类型安全 | 优秀 | 全面 TypeScript，核心数据结构有明确接口 |
| 模块化 | 优秀 | 80+ 个 .ts 文件，职责单一 |
| 文档完整性 | 优秀 | JSDoc + README + ADR 引用 + 交叉 issue 编号 |
| 测试覆盖 | 较完善 | 单元/集成/覆盖率/冒烟/在线/浏览器/原生 7 类测试 |
| 错误处理健壮性 | 优秀 | 多层防护 + 优雅降级 + 崩溃恢复 + 磁盘持久化计数器 |
| 可扩展性 | 优秀 | 24 内置扩展 + 第三方 API + MCP Server + 自定义工作流 |
| 潜在改进点 | — | auto-dispatch.ts(1083行) 和 cli.ts(800行) 可进一步拆分 |

---

## 五、使用场景详细分析

### 5.1 八大典型场景

#### 场景 1：SaaS 产品从 0 到 1 构建

> *"We've used GSD to build and launch a SaaS product including an agent-first CMS (whiteboar.it)"* — HN 用户

- **工作流**: `/gsd auto` → 输入产品概念 → 自动规划 Milestone/Slice/Task → 全自动执行 → Git worktree 隔离 → squash 合并
- **适用模式**: Auto Mode 全自动驾驶
- **关键价值**: 一个人完成通常需要团队的完整产品

#### 场景 2：macOS/iOS 原生应用开发

> *"Got sick of paying FreshBooks... used GSD to build a macOS Swift app with Codex 5.4 and Opus 4.6"* — HN 用户

- **工作流**: Step Mode 逐步执行 → SwiftUI 界面生成 → 交互式确认每个 Slice
- **关键优势**: 多 LLM 路由（Codex 处理代码生成，Opus 处理架构决策）

#### 场景 3：大规模代码库快速构建

> *"With GSD, I was able to write 250K lines of code in less than a month, without prior knowledge of claude"* — HN 用户

- **工作流**: Spec-Driven Development → Milestone 分解 → 并行 Slice 执行 → Token 优化控制成本
- **关键特性**: Context Engineering 确保每次 Task 在新鲜上下文中执行

#### 场景 4：替代现有 SaaS 工具的自建方案

- **动因**: SaaS 月费累积 > AI API 一次性成本
- **工作流**: 需求分析 → 技术选型 → 分模块实现 → 集成测试
- **案例**: 替代 FreshBook（记账软件）、替代其他订阅制 SaaS

#### 场景 5：Agent-First CMS / 内容管理系统

- **实际案例**: whiteboar.it 产品
- **特色**: 利用 GSD 的 Agent 架构构建以 AI Agent 为核心的内容管理
- **扩展**: 使用 GSD Extension API 自定义 CMS 专用扩展

#### 场景 6：从 Claude Code 裸用到框架化升级

- **目标用户**: 已在使用 Claude Code 但缺乏系统化工作流的开发者
- **升级路径**: 安装 GSD → 导入现有项目 → `/gsd` 命令替代直接对话
- **价值**: 从随意 vibe-coding 升级为 spec-driven 开发

#### 场景 7：多模型协作的复杂项目

- **配置**: Opus 4.6 做架构设计 → Codex 做代码生成 → Sonnet 做测试 → Ollama 本地做文档
- **GSD 能力**: 20+ LLM Provider 支持 + 复杂度路由策略

#### 场景 8：CI/CD 集成的 Headless 自动化

- **用法**: `gsd headless --timeout 600000` 在 CI pipeline 中运行
- **特点**: 结构化退出码 (0=成功/1=失败/2=阻塞) + Remote Questions 路由人工决策 + 崩溃自动重启

### 5.2 与竞品的差异化定位

| 维度 | GSD-2 | Claude Code (原生) | Cursor/Windsurf | Superpowers | Aider |
|------|-------|-------------------|----------------|-------------|-------|
| **本质** | 独立 Agent 编排应用 | IDE/CLI 工具 | IDE | Prompt 框架 | 编码助手 |
| **上下文管理** | 每任务全新 200k 窗口 | 手动管理 | 自动管理 | 依赖宿主 | 对话滚动 |
| **自主程度** | 全自动里程碑推进 | 半自动 | 辅助编码 | 步骤引导 | 交互式 |
| **Git 策略** | Worktree+Squash merge | 用户手动 | 自动 commit | 用户手动 | 自动 commit |
| **崩溃恢复** | 锁文件+Session取证 | 无 | 有限 | 无 | 无 |
| **成本追踪** | 按阶段/切片/模型细分 | 基础 | 有 | 无 | 无 |
| **卡死检测** | 滑动窗口+诊断重试 | 无 | 无 | 无 | 无 |
| **Token 优化** | 40-60% 节省 | 无 | 无 | 无 | 无 |
| **Provider** | 20+ | Anthropic 为主 | 多家 | Claude | 多家 |
| **Headless/CI** | 一等公民 | 有限 | 无 | 无 | 有 |

**一句话总结差异**：GSD 2 不是又一个 AI 编码助手或 IDE 插件，而是一个**编排层（Orchestration Layer）**——站在 AI 编程 Agent 之上，管理整个软件交付生命周期。

---

## 六、用户评价与分析

### 6.1 正面评价（真实用户声音）

来自 Hacker News、GitHub Discussions、专业媒体评测：

#### 高度认可类

> **"GSD consistently gets me 95% of the way there on complex tasks. That's amazing... We've used GSD to build and launch a SaaS product including an agent-first CMS (whiteboar.it)"**
> — HN 用户，成功构建并上线了 SaaS 产品

> **"I've been using GSD for all my dev projects. Honestly a fantastic harness right out of the box"**
> — HN 用户，称其为"开箱即用的绝佳 harness"

> **"With GSD, I was able to write 250K lines of code in less than a month, without prior knowledge of claude"**
> — HN 用户，一个月写出 25 万行代码

> **"GSD pretty much solved these problems for me [compared to Superpowers]"**
> — HN 用户，对比后认为 GSD 更优

#### 专业媒体好评

- **Medium (@joe.njenga)**: 将 GSD 定位为填补 **"vibe-coding 与重型企业框架之间空白"** 的工具，特别适合独立开发者、自由职业者、初创公司创始人
- **The New Stack (David Eastman)**: 实操评测称赞 GSD 的**交互式需求提取能力**——能从模糊描述中通过提问式对话挖掘出具体需求；自动 Git 初始化、进度条显示、Roadmap 自动生成获得好评

### 6.2 负面评价（真实用户声音）

#### Token 消耗问题（最集中的投诉点）

> **"gsd is a highly overengineered piece of software that unfortunately does not get shit done, burns limits and takes ages while doing so"**
> — HN 用户，批评过度工程化、烧额度、速度慢

> **"Burned literally a weeks worth of the $20 claude subscription and then $20 worth of API credits on gsdv2. To get like 500 LOC"**
> — HN 用户，花了约 $40 只得到 500 行代码

> **"Hit the 5-hour limits in ~30 minutes and my weekly limits by Tuesday with GSD"**
> — HN 用户，30 分钟触达 5 小时用量上限

> **"Tried this for a week and gave up. Required far too much back and forth. Ate too many tokens... It should be called planning-shit instead"**
> — HN 用户，讽刺其应改名为"规划 shit"

#### 流程/体验问题

> **"Gave it a shot, but won't be using it going forward. It requires a waterfall process"**
> — HN 用户，不喜欢瀑布式开发流程

> **"Creates a lot of content inside the repository and I don't like that... it just pollutes my space"**
> — HN 用户，抱怨仓库内生成大量文件造成污染

#### GitHub Discussions 回退声音

- **"GSD-2 is becoming nearly unusable on Claude, even with extra usage"** (2026-04-09)
- **"Migrate back to GSD v1??"** (2026-03-25, 7 条回复) — 出现回退到 v1 的声音
- **"Downgrade to GSD v1?"** (2026-04-08, 6 条回复)

### 6.3 评价总结矩阵

| 维度 | 正面占比 | 核心论点 |
|------|:-------:|---------|
| 复杂任务完成度 | 70%+ | 能达到 95% 完成度，适合大型项目 |
| Token 效率 | **30%** | **最大痛点**，大量用户投诉烧钱 |
| 学习曲线 | 50% | 有门槛但 v1 用户迁移较顺畅 |
| 工作流偏好 | 40% | 瀑布式流程不受敏捷爱好者欢迎 |
| 仓库整洁度 | 35% | 生成文件多，部分用户反感 |
| 与竞品对比 | 60% | 相比 Superpowers/Plan Mode 有优势 |

### 6.4 SWOT 分析

| | 正面 | 负面 |
|--|------|------|
| **内部** | **优势(S)**: Context Engineering 创新、Spec-Driven 方法论成熟、MIT 开源、双模式灵活、Token 优化系统、活跃社区、24 个 bundled extensions | **劣势(W)**: Token 消耗过大、v2 稳定性不足、学习曲线陡峭、仓库文件污染、流程偏重、缺少可视化界面 |
| **外部** | **机会(O)**: AI coding 市场爆发增长、企业 AI adoption 加速、开源生态扩展、多 LLM 时代适配 | **威胁(T)**: Cursor/Windsurf IDE 方案崛起、Devin 全自治方案进化、Claude Code 自身能力增强可能使框架层多余、API 成本持续高企 |

### 6.5 最终评分（10 分制）

| 维度 | 分数 | 说明 |
|------|:----:|------|
| 创新性 | **9/10** | Context Engineering 和 SDD 方法论独树一帜 |
| 实用性 | **7/10** | 大型项目出色，简单任务杀鸡用牛刀 |
| 易用性 | **5/10** | 学习门槛不低，v2 稳定性影响体验 |
| 成本效益 | **4/10** | Token 消耗是最大短板 |
| 生态健康度 | **7/10** | 开源活跃，但出现回退 v1 的声音 |
| 商业可行性 | **6/10** | 开源可持续性待观察 |
| **综合推荐指数** | **6.5/10** | **适合中大型项目的结构化 AI 开发** |

---

## 七、局限性与改进方向

### 7.1 最受诟病的问题（按严重程度排序）

| 排名 | 问题 | 严重度 | 影响范围 |
|:----:|------|:------:|---------|
| 1 | **Token 消耗过大** | 致命 | 所有付费用户 |
| 2 | **v2 稳定性/可用性下降** | 严重 | Claude 用户为主 |
| 3 | **流程过重/瀑布式** | 中等 | 敏捷偏好用户 |
| 4 | **仓库文件污染** | 中等 | 洁癖型开发者 |
| 5 | **执行速度慢** | 中等 | 时间敏感用户 |
| 6 | **学习门槛** | 轻微 | 新手用户 |
| 7 | **模型选择困惑** | 轻微 | 成本敏感用户 |

### 7.2 社区最想要的功能（优先级排序）

1. **Token 消耗大幅优化** — 第一优先级，关系到生存
2. **Lite/Quick 模式** — 降低简单任务的使用门槛
3. **执行前成本估算** — 用户掌控感
4. **v2 稳定性修复** — 止住回退 v1 的趋势
5. **清理/归档生成的文件** — 解决仓库污染问题
6. **更多 bundled extensions** — 丰富开箱即用体验
7. **Web Dashboard** — 可视化管理
8. **企业版/团队功能** — 商业化路径

---

## 八、对 Harness 套件项目的启示

### 8.1 最值得借鉴的设计（P0 级别）

| # | 来自 GSD-2 的设计 | 对 Harness 的迁移建议 |
|---|-------------------|---------------------|
| 1 | **三层工作分解 (Milestone→Slice→Task)** | Harness 应建立类似的粒度层次体系：Project → Phase → Stage → Step → Action |
| 2 | **每 Task 新鲜上下文窗口** | Harness 的每个 Skill/Step 执行应确保干净的上下文，通过 Artifact 传递跨步信息 |
| 3 | **磁盘驱动的状态机** | Harness 的 Pipeline 状态应持久化到磁盘而非仅内存，天然支持崩溃恢复 |
| 4 | **声明式调度表 (Dispatch Rules)** | Harness 的 Orchestrator 应采用规则表而非硬编码逻辑，便于调试和扩展 |
| 5 | **Git Worktree 隔离** | Harness 的执行单元应在隔离环境中运行，互不影响 |

### 8.2 值得参考的设计（P1 级别）

| # | 设计 | 参考价值 |
|---|------|---------|
| 1 | Token 优化三档 Profile | Harness 的成本控制策略 |
| 2 | 复杂度路由（不同复杂度用不同模型） | Harness 的 AI Provider 选择策略 |
| 3 | UAT 验收门控 | Harness 的质量门禁机制 |
| 4 | 双终端协作模式 | Harness 的多人协作方案 |
| 5 | 24 个 Extension 的分类组织法 | Harness Skill/Extension 的分类体系 |
| 6 | 上下文工程文档体系 (PROJECT/DECISIONS/STATE/...) | Harness Artifact 的标准化格式 |
| 7 | Headless + CI/CD 一等公民 | Harness 的自动化集成能力 |
| 8 | 断路器模式（Rewrite/UAT 保护） | Harness 的安全防护机制 |

### 8.3 应该避免的问题（教训）

| # | GSD-2 的坑 | Harness 应如何避免 |
|---|-----------|-------------------|
| 1 | Token 消耗失控 | 内置严格的成本预估和上限控制；提供 Lite 模式 |
| 2 | 过度工程化 | 保持简单任务的轻量路径；不要强制完整流程 |
| 3 | 仓库文件污染 | 生成的 Artifact 应可归档/隐藏；提供清理命令 |
| 4 | 瀑布式流程唯一选项 | 同时支持敏捷/迭代模式和瀑布模式 |
| 5 | v2 稳定性倒退 | 保证向后兼容；渐进式升级路径；保留稳定版 |
| 6 | 学习曲线过陡 | 提供渐进式入门路径（Quick → Step → Auto）；好的默认配置 |

### 8.4 GSD-2 与 Harness 套件的概念映射

| GSD-2 概念 | Harness 对应概念 | 映射说明 |
|-----------|-----------------|---------|
| **Milestone** | **Project / Release** | 可交付的大版本 |
| **Slice** | **Phase / Stage** | 可演示的功能单元 |
| **Task** | **Step / Action** | 单次执行的原子操作 |
| **Auto Loop (状态机)** | **Pipeline Orchestrator** | 自动推进的核心引擎 |
| **Dispatch Rules** | **Routing Rules / Decision Table** | 状态→动作的映射规则 |
| **Context Engineering 文档** | **Artifact / Spec** | PROJECT/PLAN/SUMMARY → Harness 的标准化产出物 |
| **Extension** | **Skill / Plugin** | 可插拔的能力单元 |
| **Subagent (Scout/Worker)** | **Specialized Skill** | 专业化能力角色 |
| **Workflow Engine** | **Workflow Definition** | 可自定义的执行流程 |
| **Token Budget** | **Cost Policy / Resource Quota** | 成本和资源管控 |
| **Git Worktree** | **Execution Sandbox** | 隔离执行环境 |
| **Crash Recovery** | **Checkpoint / Resume** | 断点续跑能力 |
| **UAT Gate** | **Quality Gate / Validation** | 质量验证门控 |
| **Dashboard Overlay** | **Observability Dashboard** | 可观测性界面 |
| **Headless Mode** | **CI/CD Integration** | 自动化流水线集成 |

---

## 九、总结

### GSD-2 是什么

GSD-2 是目前 **AI 编码 Agent 领域最具野心的开源项目之一**。它从一个爆火的 Claude Code prompt 框架（v1），进化为一个完整的、独立的 **AI 软件交付编排平台**（v2）。代表了 **AI-native 软件开发方法论**的前沿探索方向。

### 核心竞争力

1. **真正的自主性** — `/gsd auto` 可以在没有人类干预的情况下完成整个里程碑
2. **Context Engineering** — 每任务全新 200k token 窗口，从根本上解决上下文污染问题
3. **工程化深度** — 崩溃恢复、成本追踪、卡死检测、Git 隔离都是工程级解决方案
4. **开放性** — 20+ LLM Provider、MIT 许可证、100+ 贡献者、24 个内置扩展
5. **极速迭代** — 每 3-5 天一个版本，77 个版本的持续演进

### 核心风险

1. **Token 成本过高** — 用户最集中投诉点，关系到产品生存
2. **v2 稳定性不足** — 已出现回退 v1 的社区声音
3. **过度工程化** — 简单任务杀鸡用牛刀
4. **IDE 集成方案的竞争压力** — Cursor/Windsurf 等正在快速进步

### 对 Harness 套件的最终建议

**GSD-2 是 Harness 套件最重要的单一参考对象**。原因：

1. **理念最接近** — 都是面向"AI 驱动的全链路软件开发"
2. **已经验证过的设计** — 三层工作分解、Context Engineering、声明式调度表都经过大规模用户验证
3. **踩过的坑明确** — Token 消耗、过度工程化、稳定性倒退等问题可以作为 Harness 的避坑指南
4. **开源可研究** — MIT 许可证，代码完全可读，可以直接学习实现细节

**建议 Harness 套件在以下方面深入借鉴 GSD-2**：
- 三层工作分解体系（Milestone → Slice → Task）
- 磁盘驱动的状态机 + 声明式调度表
- 上下文工程方法论和 Artifact 标准化
- Git Worktree 隔离 + Crash Recovery
- Token 优化和成本控制策略

同时在以下方面**做得更好**：
- 更低的 Token 开销（轻量模式）
- 更灵活的流程选择（非纯瀑布）
- 更干净的仓库管理（Artifact 归档）
- 更稳定的版本演进（避免 v2 倒退）

---

*报告完成时间：2026年4月22日*
*调研方法：GitHub API + Web Search + HN/Discussions/专业媒体交叉验证 + 源码架构分析*
