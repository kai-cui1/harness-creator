# Harness 工程套件 — 架构设计文档

| 属性 | 值 |
|------|-----|
| **文档版本** | v0.1.0 |
| **文档状态** | Draft（初稿） |
| **创建日期** | 2026-04-22 |
| **最后更新** | 2026-04-22 |
| **作者** | Harness Creator 项目组 |
| **关联文档** | [API 格式对比报告](./api-format-comparison-report.md) |

---

## 文档修订历史（Changelog）

| 版本 | 日期 | 变更类型 | 变更摘要 | 作者/贡献者 |
|------|------|---------|---------|------------|
| **v0.1.0** | 2026-04-22 | Initial | 初稿：完整架构设计，含五层模型、核心接口定义、框架适配策略、与 CCR 的对应关系、实施路线图 | Harness Creator |

> **变更类型说明**: `Initial` = 初始版本 | `Major` = 架构重大变更 | `Minor` = 功能新增/接口扩展 | `Patch` = 错误修正/描述优化 | `Deprecated` = 标记废弃

---

## 一、设计背景与动机

### 1.1 问题陈述

当前 AI 编程 Agent 生态呈现 **「碎片化」** 特征：

```
碎片化现状：

┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Claude Code│  │Codex CLI │  │  Cursor  │  │  Cline   │
│           │  │          │  │          │  │          │
│ Anthropic │  │ OpenAI   │  │ IDE Fork │  │ Open Src │
│ 原生协议   │  │ 原生协议  │  │ 多模型    │  │ 模型无关  │
└─────┬─────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                    LLM Provider 层                       │
│  Claude │ GPT-5.x │ DeepSeek │ Qwen │ Kimi │ Gemini ... │
└─────────────────────────────────────────────────────────┘
         ↑ 各自独立的 API 格式（报告 v1 已详细分析）
```

这导致两个层面的问题：

| 层面 | 问题 | 影响 |
|------|------|------|
| **LLM API 层** | 各家 API 格式不兼容（认证、消息结构、工具调用、流式输出） | 切换模型 = 重写调用代码 |
| **Agent 框架层** | 各框架的工具系统、Skill 形式、交互模式不同 | 同一个任务在不同框架中无法复用 |

### 1.2 设计目标

Harness 工程套件的核心目标是：**让一套任务定义（Harness/Skill）能够在不同的 Agent 框架和 LLM 提供商上运行。**

具体目标：

1. **任务可移植**：同一个 Code Review Harness 在 Claude Code 和 Codex 中行为一致
2. **模型可切换**：同一套 Harness 可以用 DeepSeek 跑（省钱）或 Claude Opus 跑（质量）
3. **能力可组合**：Skill 可以独立使用，也可以串联形成端到端工作流
4. **渐进式采用**：不需要一次性适配所有框架，可以逐个添加

### 1.3 设计原则

| 原则 | 说明 |
|------|------|
| **接口优于实现** | 定义清晰的抽象接口，各框架只需实现接口即可接入 |
| **分层解耦** | 任务定义 → 能力抽象 → 框架适配 → LLM 调用，每层独立演进 |
| **约定优于配置** | 提供合理默认值，减少用户配置负担 |
| **渐进增强** | 核心功能优先，高级特性（流式、子Agent等）标记为 optional |
| **实战验证优先** | 参考 CCR 等已生产验证的方案，避免过度设计 |

---

## 二、整体架构 — 五层模型

### 2.1 架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户 / 开发者                                  │
│                                                                     │
│  "我需要一个 Code Review 的 Skill"                                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   Layer 5: Presentation & Interaction（表现与交互层）                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│   │ CLI Output  │  │ IDE Panel   │  │ Web Dashboard│                │
│   │ (终端输出)   │  │ (IDE面板)   │  │ (Web仪表盘)  │                │
│   └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Layer 4: Task Definition（任务定义层）★ 核心                      │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  Harness Definition                                      │     │
│   │  ├── 元数据: name, version, author, tags                  │     │
│   │  ├── 触发条件: trigger (manual/event/schedule)             │     │
│   │  ├── 输入规范: inputs[] (schema + validation)              │     │
│   │  ├── 执行步骤: steps[] (有序的能力调用序列)                  │     │
│   │  ├── 输出规范: outputs[] (格式 + 目标)                     │     │
│   │  ├── 验收标准: acceptance[] (质量门禁)                     │     │
│   │  └── 配置项: config[] (可调参数 + 默认值)                   │     │
│   │                                                           │     │
│   │  Skill Definition (可复用的能力单元)                        │     │
│   │  ├── 单一职责: 一个 Skill 对应一个明确的能力                 │     │
│   │  ├── 可组合: 多个 Skill 可串联成 Harness                    │     │
│   │  └── 独立可用: Skill 可以单独被 Agent 调用                  │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Layer 3: Capability Abstraction（能力抽象层）★ 关键               │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  IAgentCapabilities — 统一能力接口                          │     │
│   │  ├── 文件操作: readFile / writeFile / editFile / glob       │     │
│   │  ├── Shell 执行: execCommand / execInteractive              │     │
│   │  ├── 代码搜索: searchCode / grep / findReferences           │     │
│   │  ├── 网络: fetchUrl / webSearch                             │     │
│   │  ├── 工具调用: useTool / useMCP                             │     │
│   │  ├── 上下文: getContext / updateContext                     │     │
│   │  ├── 子代理: spawnSubAgent / awaitSubAgent                  │     │
│   │  └── 多模态: readImage / readPDF                            │     │
│   │                                                           │     │
│   │  Capability Registry — 能力注册与发现                        │     │
│   │  ├── 声明式注册: 框架适配器声明自己支持哪些能力               │     │
│   │  ├── 能力查询: 运行时检查某能力是否可用                       │     │
│   │  └── 降级策略: 不可用时提供 fallback 方案                    │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Layer 2: Framework Adapter（框架适配层）                           │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│   │  Claude  │ │  Codex   │ │  Cursor  │ │  Cline   │            │
│   │  Code    │ │   CLI    │ │          │ │          │            │
│   │ Adapter  │ │ Adapter  │ │ Adapter  │ │ Adapter  │            │
│   └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
│        │            │            │            │                   │
│        ▼            ▼            ▼            ▼                   │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  Framework-Specific Implementations                       │     │
│   │  • Claude Code: Tool Call (Read/Bash/Grep/WebFetch/...)   │     │
│   │  • Codex CLI: Extension API (fs/shell/search/...)         │     │
│   │  • Cursor: Rules + Commands + MCP                         │     │
│   │  • Cline: Slash Commands + MCP + Custom Tools             │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   Layer 1: LLM Provider（LLM 提供商层）                             │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  Unified LLM Adapter (参考 API 对比报告 + CCR 实现)        │     │
│   │                                                           │     │
│   │  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌──────┐   │     │
│   │  │ OpenAI  │ │ Claude  │ │DeepSeek│ │ Qwen │ │ Kimi │   │     │
│   │  │Adapter  │ │Adapter  │ │Adapter │ │Adptr │ │Adptr │   │     │
│   │  └─────────┘ └─────────┘ └────────┘ └──────┘ └──────┘   │     │
│   │                                                           │     │
│   │  核心转换管道:                                             │     │
│   │  UnifiedRequest → ProviderFormat → API Call →             │     │
│   │  ProviderResponse → UnifiedResponse → Framework Format     │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流向

```
用户触发 Harness
     │
     ▼
Layer 5: 解析交互模式（CLI/IDE/Web）→ 确定 interactionLevel
     │
     ▼
Layer 4: 加载 Harness 定义 → 解析 steps[] → 验证 inputs[]
     │
     ▼
Layer 3: 将步骤映射为能力调用 → 查询 CapabilityRegistry → 检查降级策略
     │
     ▼
Layer 2: 框架适配器将能力调用翻译为框架原生操作
     │
     ▼
Layer 1: LLM 适配器处理实际的模型调用（含协议转换）
     │
     ▼
收集结果 → 通过 Layer 3→4→5 返回给用户
```

---

## 三、各层详细设计

### 3.1 Layer 1: LLM Provider 层

本层的设计已在 [API 格式对比报告](./api-format-comparison-report.md) 第四章和第六章中有详细说明。此处仅列出关键接口。

#### 3.1.1 统一请求/响应模型

```typescript
// ==================== LLM Provider Layer ====================

/** 统一的 LLM 调用请求 */
interface UnifiedLLMRequest {
  // === 必填 ===
  model: string;                           // 模型标识符
  messages: UnifiedMessage[];              // 消息列表

  // === 可选：生成控制 ===
  maxTokens?: number;
  temperature?: number;                    // 归一化到 [0, 2]
  topP?: number;
  stopSequences?: string[];
  seed?: number;

  // === 流式 ===
  stream?: boolean;

  // === 工具调用 ===
  tools?: UnifiedToolDefinition[];
  toolChoice?: UnifiedToolChoice;

  // === 思考/推理 ===
  thinking?: UnifiedThinkingConfig;

  // === 结构化输出 ===
  responseFormat?: UnifiedResponseFormat;

  // === Provider 特有参数透传 ===
  providerExtras?: Record<string, any>;
}

/** 统一消息 */
interface UnifiedMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string | MessageContentBlock[];

  // 工具调用相关 (OpenAI 格式)
  toolCalls?: ToolCallItem[];
  toolCallId?: string;

  // 思考内容
  thinkingContent?: string;
}

interface MessageContentBlock {
  type: 'text' | 'image_url' | 'video_url' | 'thinking';
  text?: string;
  imageUrl?: { url: string };
  videoUrl?: { url: string };
  thinking?: string;
}

/** 统一工具定义 */
interface UnifiedToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;          // JSON Schema
}

/** 统一响应 */
interface UnifiedLLMResponse {
  id: string;
  model: string;
  content: string;
  finishReason: UnifiedFinishReason;
  usage: UnifiedUsage;
  toolCalls?: ToolCallResult[];
  thinkingContent?: string;
}

enum UnifiedFinishReason {
  STOP = 'stop',
  LENGTH = 'length',
  TOOL_USE = 'tool_use',
  CONTENT_FILTER = 'content_filter',
  END_TURN = 'end_turn',                   // Claude
  MAX_TOKENS = 'max_tokens',               // Claude
  STOP_SEQUENCE = 'stop_sequence',         // Claude
}

interface UnifiedUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  cachedTokens?: number;
  reasoningTokens?: number;
}

interface UnifiedThinkingConfig {
  enabled: boolean;
  budgetTokens?: number;                    // Claude 用
  effort?: 'none' | 'low' | 'medium' | 'high';  // OpenAI 用
}
```

#### 3.1.2 LLM Provider 适配器接口

```typescript
/** LLM Provider 适配器 — 每个 LLM 厂商一个实现 */
interface ILLMProviderAdapter {
  /** 适配器名称 */
  readonly name: string;

  /** 支持的模型列表 */
  readonly supportedModels: string[];

  /**
   * 将统一请求转换为目标 Provider 格式并发送
   * 内部处理: 认证、格式转换、错误重试
   */
  chat(request: UnifiedLLMRequest): Promise<UnifiedLLMResponse>;

  /**
   * 流式调用 — 返回异步迭代器
   */
  chatStream(
    request: UnifiedLLMRequest
  ): AsyncIterable<UnifiedStreamChunk>;

  /**
   * 检查该 Provider 是否支持某个能力
   */
  supports(capability: LLMCapability): boolean;

  /**
   * 获取该 Provider 的默认配置建议
   */
  getDefaultConfig(): ProviderConfig;
}

type LLMCapability =
  | 'function_calling'
  | 'streaming'
  | 'thinking'
  | 'json_mode'
  | 'image_input'
  | 'video_input'
  | 'web_search'
  | 'prompt_caching';

interface ProviderConfig {
  baseUrl: string;
  authType: 'bearer' | 'api_key' | 'oauth';
  defaultHeaders: Record<string, string>;
  defaultModel: string;
  maxTokens: { min: number; max: number; default: number };
  rateLimits: { rpm: number; tpm: number };
}
```

#### 3.1.3 与 CCR 的对应关系

| 本设计概念 | CCR 实现对应 | 说明 |
|-----------|-------------|------|
| `UnifiedLLMRequest` | `UnifiedChatRequest` | 几乎一致，CCR 已验证可行 |
| `ILLMProviderAdapter` | `Transformer` 接口 | CCR 的 Transformer 就是 Provider 适配器 |
| `chat()` 方法 | `transformRequestIn → API → transformResponseOut` | 四阶段管道 |
| `chatStream()` | `transformResponseOut` 中的 ReadableStream 处理 | 流式是最大难点 |
| `supports()` | 各 Transformer 自身声明 | CCR 未显式建模，我们补充 |
| `ProviderConfig` | `config.json` 中的 Providers 数组 | 配置来源相同 |

---

### 3.2 Layer 2: Framework Adapter 层

这是连接「通用能力」和「具体框架」的关键桥梁。

#### 3.2.1 框架差异分析矩阵

| 能力维度 | Claude Code | Codex CLI | Cursor | Cline | 抽象策略 |
|---------|------------|-----------|--------|-------|---------|
| **读文件** | `Read` tool | `fs.read()` | IDE API | MCP filesystem | 统一为 `readFile(path)` |
| **写文件** | `Write` tool | `fs.write()` | IDE API | MCP filesystem | 统一为 `writeFile(path, content)` |
| **编辑文件** | `Edit` tool | `fs.edit()` | IDE Apply | MCP edit | 统一为 `editFile(path, old, new)` |
| **执行命令** | `Bash` tool | `shell.exec()` | Terminal | MCP shell | 统一为 `execCommand(cmd)` |
| **代码搜索** | `Grep` tool | `search.code()` | IDE Search | Custom | 统一为 `searchCode(pattern)` |
| **网络请求** | `WebFetch` tool | `fetch()` | 内置 | MCP fetch | 统一为 `fetchUrl(url)` |
| **工具/MCP** | 内置 + MCP Server | Extensions | MCP Client | MCP Client | 统一为 `useTool(name, params)` |
| **子 Agent** | `Agent` tool (内置) | 支持 | Background Agent | 不支持 | 标记 optional + 降级 |
| **多模态输入** | Read tool (图片/PDF) | 支持 | IDE 原生 | 通过 MCP | 统一为 `readImage/readPDF` |
| **项目上下文** | CLAUDE.md + memory | config.toml | .cursorrules | CLAUDE.md 兼容 | 统一为 `getContext()` |
| **确认交互** | 工具调用需确认 | 可配置自主度 | 可配置 | 可配置 | `interactionLevel` 参数 |
| **Skill 加载** | `.md` + Slash Command | JS/TS Extension | `.cursorrules` | Slash Command | **编译器模式**（见下文） |

#### 3.2.2 核心接口：IAgentCapabilities

```typescript
// ==================== Framework Adapter Layer ====================

/**
 * 统一 Agent 能力接口
 * 每个 Framework Adapter 必须实现此接口
 *
 * 设计原则:
 * - 所有方法返回 Promise（支持异步操作）
 * - 每个方法有明确的输入输出契约
 * - 不可用能力通过 throws 或返回特殊值表示
 */
interface IAgentCapabilities {

  // ========== 文件系统操作 ==========

  /** 读取文件内容 */
  readFile(path: string): Promise<string>;

  /** 写入文件（覆盖或新建） */
  writeFile(path: string, content: string): Promise<void>;

  /** 编辑文件（精确替换，非覆盖） */
  editFile(
    path: string,
    oldText: string,
    newText: string,
    options?: EditOptions
  ): Promise<EditResult>;

  /** 文件/目录是否存在 */
  exists(path: string): Promise<boolean>;

  /** Glob 模式匹配文件列表 */
  glob(pattern: string, basePath?: string): Promise<string[]>;

  /** 读取目录结构 */
  listDirectory(path: string): Promise<DirectoryEntry[]>;


  // ========== Shell / 命令执行 ==========

  /** 执行 shell 命令（非交互式） */
  execCommand(
    command: string,
    options?: ExecOptions
  ): Promise<ExecResult>;

  /** 交互式命令执行（需要用户输入的场景） */
  execInteractive?(
    command: string,
    input?: string
  ): Promise<ExecResult>;


  // ========== 代码搜索与分析 ==========

  /** 正则/Grep 搜索代码内容 */
  searchCode(
    pattern: string,
    options?: SearchOptions
  ): Promise<SearchResult[]>;

  /** 查找符号引用（如函数调用点） */
  findReferences(symbol: string, filePath?: string): Promise<ReferenceLocation[]>;


  // ========== 网络操作 ==========

  /** HTTP GET 请求获取内容 */
  fetchUrl(url: string, options?: FetchOptions): Promise<string>;

  /** 网络搜索（依赖 LLM 或外部搜索 API） */
  webSearch?(query: string): Promise<SearchResultItem[]>;


  // ========== 工具 / MCP 调用 ==========

  /** 调用已注册的自定义工具或 MCP 工具 */
  useTool<T = any>(
    toolName: string,
    params: Record<string, any>
  ): Promise<T>;

  /** 列出所有可用工具 */
  listTools(): Promise<ToolInfo[]>;


  // ========== 上下文管理 ==========

  /** 获取当前项目上下文信息 */
  getContext(): Promise<ProjectContext>;

  /** 更新上下文（如添加记忆、更新状态） */
  updateContext(updates: Partial<ProjectContext>): Promise<void>;


  // ========== 子 Agent（Optional）==========

  /** 生成子 Agent 并执行任务 */
  spawnSubAgent?(
    prompt: string,
    options?: SubAgentOptions
  ): Promise<SubAgentResult>;


  // ========== 多模态（Optional）==========

  /** 读取图像文件并返回描述 */
  readImage?(path: string): Promise<ImageDescription>;

  /** 读取 PDF 文件内容 */
  readPDF?(path: string): Promise<PDFContent>;


  // ========== 框架元信息 ==========

  /** 获取此适配器的元信息 */
  getMetadata(): FrameworkAdapterMetadata;
}


// ====== 辅助类型定义 ======

interface EditOptions {
  /** 是否创建文件（不存在时） */
  createIfNotExist?: boolean;
  /** 替换次数限制（oldText 可能出现多次） */
  replaceAll?: boolean;
}

interface EditResult {
  success: boolean;
  changesApplied: number;
  errorMessage?: string;
}

interface DirectoryEntry {
  name: string;
  path: string;
  type: 'file' | 'directory';
}

interface ExecOptions {
  cwd?: string;
  timeout?: number;
  env?: Record<string, string>;
}

interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

interface SearchOptions {
  basePath?: string;
  filePattern?: string;           // 如 "*.ts"
  caseSensitive?: boolean;
  maxResults?: number;
}

interface SearchResult {
  file: string;
  line: number;
  column: number;
  match: string;
  contextBefore?: string;
  contextAfter?: string;
}

interface ReferenceLocation {
  file: string;
  line: number;
  context: string;
}

interface FetchOptions {
  method?: 'GET' | 'POST';
  headers?: Record<string, string>;
  timeout?: number;
}

interface SearchResultItem {
  title: string;
  url: string;
  snippet: string;
}

interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

interface ProjectContext {
  projectName: string;
  rootPath: string;
  language: string[];
  framework: string[];
  description?: string;
  conventions?: string;            // 编码规范
  memory?: Record<string, any>;    // 持久记忆
}

interface SubAgentOptions {
  model?: string;                  // 子 Agent 使用的模型
  maxTurns?: number;               // 最大轮次
  tools?: string[];                // 允许使用的工具子集
}

interface SubAgentResult {
  success: boolean;
  output: string;
  turnsUsed: number;
  toolCallsMade: number;
}

interface ImageDescription {
  description: string;
  format: string;
  dimensions?: { width: number; height: number };
}

interface PDFContent {
  pages: number;
  text: string;
  metadata?: Record<string, any>;
}

interface FrameworkAdapterMetadata {
  frameworkName: string;            // "claude-code" | "codex" | "cursor" | "cline"
  version: string;
  supportedCapabilities: CapabilitySupportMap;
  nativeInteractionMode: 'confirm' | 'auto' | 'configurable';
}

type CapabilitySupportMap = {
  [K in keyof IAgentCapabilities]: 'full' | 'partial' | 'none' | 'unknown';
};
```

#### 3.2.3 框架适配器注册机制

```typescript
/**
 * 框架适配器注册表
 *
 * 使用方式:
 *   1. 框架适配器通过 register() 注册自身
 *   2. Harness 运行时通过 resolve() 获取适配器实例
 *   3. 支持运行时动态切换适配器
 */
class FrameworkAdapterRegistry {
  private adapters: Map<string, IAgentCapabilities> = new Map();

  /** 注册一个框架适配器 */
  register(adapter: IAgentCapabilities): void {
    const meta = adapter.getMetadata();
    this.adapters.set(meta.frameworkName, adapter);
  }

  /** 按名称获取适配器 */
  resolve(frameworkName: string): IAgentCapabilities | undefined {
    return this.adapters.get(frameworkName);
  }

  /** 获取所有已注册适配器及其元信息 */
  listAll(): Array<{
    meta: FrameworkAdapterMetadata;
    capabilities: CapabilitySupportMap;
  }> {
    return Array.from(this.adapters.values()).map(adapter => ({
      meta: adapter.getMetadata(),
      capabilities: {} as CapabilitySupportMap, // 由 getMetadata() 提供
    }));
  }

  /** 检查某框架是否支持指定能力集 */
  checkSupport(
    frameworkName: string,
    requiredCapabilities: (keyof IAgentCapabilities)[]
  ): SupportCheckResult {
    const adapter = this.resolve(frameworkName);
    if (!adapter) {
      return { supported: false, reason: `Framework "${frameworkName}" not registered` };
    }

    const meta = adapter.getMetadata();
    const unsupported = requiredCapabilities.filter(
      cap => meta.supportedCapabilities[cap] === 'none'
    );

    if (unsupported.length === 0) {
      return { supported: true };
    }
    return {
      supported: false,
      missingCapabilities: unsupported,
      reason: `Missing capabilities: ${unsupported.join(', ')}`,
    };
  }
}

interface SupportCheckResult {
  supported: boolean;
  reason?: string;
  missingCapabilities?: (keyof IAgentCapabilities)[];
}
```

---

### 3.3 Layer 3: Capability Abstraction 层

本层在 Layer 2 的接口之上增加**语义包装**和**降级策略**。

#### 3.3.1 能力语义包装

原始接口只定义了「怎么做」，这里增加「做什么」的语义：

```typescript
// ==================== Capability Abstraction Layer ====================

/**
 * 语义化的能力调用 — 封装 IAgentCapabilities 为更高级的操作
 *
 * 示例:
 *   原始: adapter.execCommand("git diff HEAD~1")
 *   语义: capabilities.getRecentChanges(count: 1)
 */
interface ISemanticCapabilities extends IAgentCapabilities {

  // === 代码理解 ===
  understandCode(file: string): Promise<CodeUnderstanding>;
  understandProject(): Promise<ProjectUnderstanding>;

  // === 变更操作 ===
  makeChange(change: CodeChange): Promise<ChangeResult>;
  makeChanges(changes: CodeChange[]): Promise<ChangeResult[]>;

  // === Git 操作 ===
  getGitStatus(): Promise<GitStatus>;
  getRecentChanges(count?: number): Promise<GitDiff[]>;
  createBranch(name: string): Promise<void>;
  stageFiles(files: string[]): Promise<void>;

  // === 测试 ===
  runTests(pattern?: string): Promise<TestResults>;
  runLint(): Promise<LintResults>;

  // === 依赖管理 ===
  installDependency(pkg: string): Promise<void>;
  listDependencies(): Promise<DependencyInfo[]>;
}
```

#### 3.3.2 降级策略引擎

当目标框架不支持某能力时的处理策略：

```typescript
/**
 * 降级策略定义
 *
 * 当目标框架不支持某能力时，按以下优先级尝试:
 *   1. fallbackFn — 提供的替代实现
 *   2. simulation — 用 LLM 模拟（如无法执行命令就让 LLM 分析）
 *   3. skip — 跳过该步骤，记录警告
 *   4. error — 报错终止
 */
type FallbackStrategy =
  | { type: 'fallback'; fn: (...args: any[]) => Promise<any> }    // 替代实现
  | { type: 'simulate'; hint: string }                              // LLM 模拟
  | { type: 'skip'; warning: string }                               // 跳过
  | { type: 'error'; message: string };                             // 报错

/**
 * 能力降级注册表
 */
class FallbackRegistry {
  private strategies: Map<string, FallbackStrategy> = new Map();

  /** 为某能力注册降级策略 */
  register(
    capabilityName: string,
    frameworkName: string,
    strategy: FallbackStrategy
  ): void {
    this.strategies.set(`${capabilityName}::${frameworkName}`, strategy);
  }

  /** 查询降级策略 */
  resolve(
    capabilityName: string,
    frameworkName: string
  ): FallbackStrategy | undefined {
    return this.strategies.get(`${capabilityName}::${frameworkName}`);
  }
}

// 示例: 子 Agent 能力的降级策略
const exampleFallbacks: FallbackRegistry = new FallbackRegistry();

// Cline 不支持子 Agent → 降级为串行执行
exampleFallbacks.register('spawnSubAgent', 'cline', {
  type: 'simulate',
  hint: '将子任务作为当前对话的一部分串行执行'
});

// 某轻量框架不支持 execCommand → 降级为跳过
exampleFallbacks.register('execCommand', 'lightweight-framework', {
  type: 'skip',
  warning: '该框架不支持命令执行，跳过此步骤'
});
```

---

### 3.4 Layer 4: Task Definition 层

这是用户直接面对的层 — Harness 和 Skill 的定义格式。

#### 3.4.1 Harness 定义 Schema

```typescript
// ==================== Task Definition Layer ====================

/**
 * Harness 定义 — 结构化的工程任务封装
 *
 * 一个 Harness 代表一个完整的、可端到端执行的工程任务。
 * 它由多个 Step 组成，每个 Step 调用一个或多个 Capability。
 */
interface HarnessDefinition {
  // ===== 元数据 =====
  metadata: HarnessMetadata;

  // ===== 触发条件 =====
  trigger: HarnessTrigger;

  // ===== 输入定义 =====
  inputs: HarnessInput[];

  // ===== 执行步骤（核心）=====
  steps: HarnessStep[];

  // ===== 输出定义 =====
  outputs: HarnessOutput[];

  // ===== 验收标准（质量门禁）=====
  acceptance: AcceptanceCriteria[];

  // ===== 配置项 =====
  config: HarnessConfig[];

  // ===== 依赖的其他 Skill =====
  dependencies?: string[];           // Skill 名称列表
}

interface HarnessMetadata {
  /** 唯一标识符: "org.scope.harness-name" */
  id: string;

  /** 人类可读名称 */
  name: string;

  /** 版本号 (SemVer) */
  version: string;

  /** 作者/维护者 */
  author: string;

  /** 分类标签（用于检索和推荐）*/
  tags: string[];

  /** 描述 */
  description: string;

  /** 兼容性要求 */
  requires: {
    frameworks?: string[];           // 要求的框架列表（空 = 全部兼容）
    capabilities?: (keyof ISemanticCapabilities)[];  // 要求的能力列表
    llmCapabilities?: LLMCapability[];  // 要求的 LLM 能力
  };

  /** 交互级别 */
  interactionLevel: 'silent' | 'confirm' | 'interactive';

  /** 预估资源消耗 */
  estimatedCost: {
    tokensPerRun?: number;            // 预估 token 消耗
    duration?: string;                // 预估耗时 (如 "2-5min")
    filesTouched?: number;            // 预估涉及的文件数
  };
}

/** 触发条件 */
interface HarnessTrigger {
  type: 'manual' | 'event' | 'schedule' | 'hook';

  // event 类型
  eventType?: 'pull_request' | 'push' | 'issue' | 'commit';

  // schedule 类型
  cronExpression?: string;

  // hook 类型
  hookEvent?: string;
}

/** 输入参数定义 */
interface HarnessInput {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'file' | 'file_list' | 'json';
  required: boolean;
  defaultValue?: any;
  validation?: {
    pattern?: string;                 // 正则校验
    enum?: any[];                     // 枚举值
    minLength?: number;
    maxLength?: number;
  };
  /** 来源: 用户手动传入 / 从上下文自动提取 / 从上一步输出获取 */
  source?: 'user' | 'context' | 'step_output';
  sourceStep?: string;                // source='step_output' 时指定步骤名
}

/** 执行步骤 — Harness 的核心 */
interface HarnessStep {
  /** 步骤唯一标识 */
  id: string;

  /** 人类可读名称 */
  name: string;

  /** 步骤描述（给 LLM 看的指令）*/
  instruction: string;

  /** 要调用的能力 */
  action: HarnessAction;

  /** 此步骤期望使用的 LLM 策略 */
  modelStrategy?: ModelStrategy;

  /** 条件执行 — 仅当 condition 为 true 时执行 */
  condition?: string;                // 表达式，如 "${input.severity} == 'high'"

  /** 重试策略 */
  retry?: RetryPolicy;

  /** 超时 */
  timeout?: number;                  // 毫秒

  /** 此步骤的输出变量名（供后续步骤引用）*/
  outputVar?: string;

  /** 失败时的行为 */
  onFailure: 'abort' | 'continue' | 'fallback';
  fallbackStepId?: string;           // onFailure='fallback' 时指定
}

/** 步骤动作 — 定义做什么 */
type HarnessAction =
  | { type: 'llm_prompt'; prompt: string; systemPrompt?: string }     // 让 LLM 思考/决策
  | { type: 'read_file'; path: string }                               // 读文件
  | { type: 'edit_file'; path: string; oldText: string; newText: string }  // 编辑文件
  | { type: 'exec_command'; command: string }                          // 执行命令
  | { type: 'search_code'; pattern: string; options?: SearchOptions }  // 搜索代码
  | { type: 'fetch_url'; url: string }                                // 网络请求
  | { type: 'use_tool'; toolName: string; params: Record<string, any> } // 调用工具
  | { type: 'sub_agent'; prompt: string; options?: SubAgentOptions }   // 子 Agent
  | { type: 'custom'; handler: string; params?: Record<string, any> }; // 自定义动作

/** 模型选择策略 */
interface ModelStrategy {
  /** 首选模型（留空则用默认）*/
  preferredModel?: string;

  /** 按场景选模型 */
  routing?: 'default' | 'reasoning' | 'fast' | 'long_context';

  /** 推理强度偏好 */
  thinkingPreference?: 'none' | 'light' | 'heavy';
}

/** 重试策略 */
interface RetryPolicy {
  maxRetries: number;
  backoffMs: number;
  retryOnErrors: string[];            // 匹配的错误类型
}

/** 输出定义 */
interface HarnessOutput {
  name: string;
  description: string;
  format: 'text' | 'markdown' | 'json' | 'file' | 'diff';
  target?: string;                    // format='file' 时指定路径
  template?: string;                  // 输出模板
}

/** 验收标准 */
interface AcceptanceCriteria {
  id: string;
  description: string;
  /** 检查类型 */
  check: 'llm_review' | 'automated_test' | 'pattern_match' | 'manual';
  /** 检查参数 */
  params?: Record<string, any>;
  /** 不通过时的行为 */
  onFail: 'warn' | 'retry' | 'abort';
  /** 权重（用于评分）*/
  weight?: number;                    // 0-1
}

/** 配置项 */
interface HarnessConfig {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'enum';
  defaultValue: any;
  options?: any[];                    // type='enum' 时的选项
  advanced?: boolean;                 // 是否为高级选项（UI 中隐藏）
}
```

#### 3.4.2 Skill 定义 Schema

Skill 是 Harness 的可复用子单元：

```typescript
/**
 * Skill 定义 — 可复用的能力单元
 *
 * 与 Harness 的区别:
 * - Skill: 单一职责，粒度细，可独立调用
 * - Harness: 完整任务，由多个 Step 组成，可能包含多个 Skill
 */
interface SkillDefinition {
  metadata: SkillMetadata;
  trigger: SkillTrigger;
  inputs: HarnessInput[];
  execute: SkillExecution;            // Skill 只有一个执行体
  outputs: HarnessOutput[];
  acceptance?: AcceptanceCriteria[];
  config?: HarnessConfig[];
}

interface SkillMetadata {
  id: string;                         // "org.scope.skill-name"
  name: string;
  version: string;
  author: string;
  category: SkillCategory;
  tags: string[];
  description: string;
  /** 此 Skill 依赖的能力 */
  requiredCapabilities: (keyof ISemanticCapabilities)[];
}

type SkillCategory =
  | 'analysis'        // 分析类（代码审查、架构分析）
  | 'generation'      // 生成类（代码生成、文档生成）
  | 'modification'    // 修改类（重构、Bug修复）
  | 'testing'         // 测试类（测试生成、测试执行）
  | 'deployment'      // 部署类（CI/CD、发布）
  | 'utility'         // 工具类（搜索、格式化、转换）
  | 'cross_phase';    // 跨阶段（需求→设计→编码）

interface SkillTrigger {
  type: 'slash_command' | 'auto_detect' | 'api_call';
  command?: string;                   // type='slash_command' 时: "/code-review"
  patterns?: string[];                // type='auto_detect' 时: ["review", "审查"]
}

/** Skill 执行体 — 比 HarnessStep 更灵活 */
interface SkillExecution {
  /** 执行指令（给 LLM 的 Prompt 模板）*/
  promptTemplate: string;

  /** 引用的能力列表 */
  usesCapabilities: (keyof ISemanticCapabilities)[];

  /** 引用的工具列表 */
  usesTools?: string[];

  /** 是否允许调用子 Skill */
  allowSubSkills?: boolean;

  /** 输出约束 */
  outputConstraints?: {
    maxLength?: number;
    format?: string;
    mustInclude?: string[];          // 必须包含的内容关键词
    mustNotInclude?: string[];       // 不能包含的内容
  };
}
```

#### 3.4.3 完整示例：Code Review Harness

```yaml
# 示例: code-review.harness.yaml
metadata:
  id: "harness.creator.code-review"
  name: "代码审查"
  version: "1.0.0"
  author: "Harness Creator"
  tags: [quality, review, pull-request]
  description: "对代码变更进行系统性审查，发现问题并给出修复建议"
  requires:
    capabilities: [readFile, editFile, searchCode, execCommand, fetchUrl]
    llmCapabilities: [function_calling]
  interactionLevel: "confirm"
  estimatedCost:
    tokensPerRun: 15000
    duration: "3-8min"

trigger:
  type: event
  eventType: pull_request

inputs:
  - name: "target_branch"
    description: "目标分支"
    type: "string"
    required: true
    source: context

  - name: "changed_files"
    description: "变更的文件列表"
    type: "file_list"
    required: true
    source: context

  - name: "review_depth"
    description: "审查深度"
    type: "enum"
    required: false
    defaultValue: "standard"
    validation:
      enum: [quick, standard, thorough]

steps:
  # Step 1: 收集变更上下文
  - id: "collect_changes"
    name: "收集变更"
    instruction: "获取本次 PR 的所有代码变更，包括 diff 内容"
    action:
      type: "exec_command"
      command: "git diff ${target_branch}...HEAD --stat && git diff ${target_branch}...HEAD"
    modelStrategy:
      routing: "fast"
    outputVar: "changes_diff"
    onFailure: "abort"

  # Step 2: 逐文件分析
  - id: "analyze_files"
    name: "分析变更文件"
    instruction: |
      对每个变更文件进行深入分析：
      1. 理解变更意图
      2. 检查潜在 Bug
      3. 评估性能影响
      4. 检查安全性问题
      5. 检查编码规范遵循情况
    action:
      type: "llm_prompt"
      prompt: |
        请审查以下代码变更：
        ${changes_diff}

        审查深度: ${review_depth}
        项目编码规范: ${context.conventions}
    modelStrategy:
      routing: "reasoning"
      thinkingPreference: "heavy"
    outputVar: "analysis_result"
    retry:
      maxRetries: 1
      backoffMs: 2000

  # Step 3: 搜索相关问题
  - id: "search_related"
    name: "搜索相关代码"
    instruction: "搜索变更涉及的相关代码，了解影响范围"
    action:
      type: "search_code"
      pattern: "${extract_symbols(analysis_result)}"
    outputVar: "related_code"
    onFailure: "continue"  # 搜索失败不影响主流程

  # Step 4: 生成审查报告
  - id: "generate_report"
    name: "生成审查报告"
    instruction: |
      基于分析和搜索结果，生成结构化的代码审查报告。
      报告必须包含：问题清单（按严重程度排序）、修复建议、正面评价。
    action:
      type: "llm_prompt"
      prompt: |
        基于以下分析结果生成代码审查报告：

        ## 分析结果
        ${analysis_result}

        ## 相关代码
        ${related_code}

        ## 输出格式要求
        ### 问题清单（按严重程度排序）
        - [严重] 问题描述 | 文件:行号 | 修复建议
        - [中等] ...
        - [建议] ...

        ### 正面评价
        - 做得好的地方...
    outputVar: "review_report"

outputs:
  - name: "report"
    description: "代码审查报告"
    format: "markdown"
    target: "CODE_REVIEW.md"

acceptance:
  - id: "has_findings"
    description: "报告必须包含具体的问题定位（文件+行号）"
    check: "pattern_match"
    params:
      pattern: "\\w+\\.\\w+:\\d+"
    weight: 0.4
    onFail: "retry"

  - id: "has_suggestions"
    description: "每个问题必须有修复建议"
    check: "llm_review"
    weight: 0.3
    onFail: "warn"

  - id: "no_false_positive"
    description: "不应有误报"
    check: "llm_review"
    weight: 0.3
    onFail: "warn"

config:
  - name: "auto_fix"
    description: "是否自动修复低风险问题"
    type: "boolean"
    defaultValue: false
    advanced: true

  - name: "max_issues"
    description: "最大报告问题数"
    type: "number"
    defaultValue: 20
```

---

### 3.5 Layer 5: Presentation & Interaction 层

#### 3.5.1 交互模式定义

```typescript
// ==================== Presentation & Interaction Layer ====================

/** 交互级别 — 控制 Harness 与用户的交互程度 */
type InteractionLevel =
  | 'silent'       // 全自动，无任何交互（适合 CI/CD）
  | 'confirm';     // 关键操作需确认（适合日常使用）

/** 展示格式 */
interface PresentationFormat {
  /** 主输出格式 */
  primary: 'terminal' | 'markdown' | 'json' | 'html' | 'ide_panel';

  /** 详细程度 */
  verbosity: 'minimal' | 'normal' | 'verbose';

  /** 是否展示中间步骤 */
  showProgress: boolean;

  /** 是否展示思考过程 */
  showThinking: boolean;

  /** 进度条样式 */
  progressStyle: 'text' | 'spinner' | 'step_list';
}

/** 交互事件 */
interface InteractionEvent {
  type:
    | 'step_start'      // 步骤开始
    | 'step_complete'   // 步骤完成
    | 'confirmation_required'  // 需要用户确认
    | 'error'           // 出错
    | 'warning'         // 警告
    | 'output_ready'    // 输出就绪
    | 'progress';       // 进度更新
  stepId?: string;
  message: string;
  data?: any;
  /** 需要用户回应的事件 */
  expectResponse?: boolean;
  responseOptions?: string[];    // 可选的回应选项
}

/** 展示层接口 — 不同 UI 后端实现 */
interface IPresentationBackend {
  /** 初始化展示环境 */
  initialize(format: PresentationFormat): Promise<void>;

  /** 渲染交互事件 */
  render(event: InteractionEvent): Promise<void>;

  /** 获取用户回应 */
  waitForResponse(options?: string[]): Promise<string>;

  /** 展示最终输出 */
  presentOutput(output: string, format: string): Promise<void>;

  /** 清理资源 */
  cleanup(): Promise<void>;
}

// ====== 内置后端实现 ======

/** 终端后端（CLI 场景）*/
class TerminalPresentationBackend implements IPresentationBackend { /* ... */ }

/** IDE 面板后端（Cursor/Cline 场景）*/
class IDEPanelPresentationBackend implements IPresentationBackend { /* ... */ }

/** JSON 后端（API/程序化调用场景）*/
class JSONPresentationBackend implements IPresentationBackend { /* ... */ }
```

---

## 四、关键设计决策（ADR 记录）

### ADR-001: 为什么选择接口抽象而非代码生成？

| 选项 | 优点 | 缺点 |
|------|------|------|
| **A: 接口抽象（ chosen ）** | 类型安全、IDE 支持、运行时灵活、易测试 | 每个框架需要写适配器 |
| B: 代码生成 | 一次生成到处用、无运行时开销 | 生成产物难调试、同步成本高 |
| C: 协议缓冲区 | 强类型跨语言 | 过度工程、生态不匹配 |

**决定**: 选择 A — 接口抽象。理由：
1. Agent 框架迭代快，代码生成难以跟上
2. TypeScript 接口天然有良好的 IDE 支持
3. 运行时可动态切换适配器（CCR 已验证此模式的可行性）
4. 测试时可以 mock 整个适配器层

### ADR-002: Harness 定义为什么用 YAML/JSON 而非纯代码？

| 选项 | 优点 | 缺点 |
|------|------|------|
| **A: 声明式 YAML/JSON（chosen）** | 人机可读、可版本控制、可跨语言消费、LLM 易解析 | 复杂逻辑表达受限 |
| B: 纯 TypeScript/Python | 表达力强、IDE 完善 | 框架耦合、LLM 难以直接编辑 |

**决定**: 选择 A — 声明式格式为主，辅以自定义 Handler 扩展点。

### ADR-003: 子 Agent 能力如何处理？

**决定**: 标记为 optional，提供三级降级策略：

```
Level 1: 原生子 Agent（Claude Code / Codex / Cursor 支持）
    ↓ 不可用
Level 2: 串行模拟（在同一会话中依次执行子任务）
    ↓ 不可接受
Level 3: 跳过并警告（记录到日志，不中断主流程）
```

### ADR-004: Skill 格式如何跨框架分发？

**决定**: 采用**编译器模式** — 定义一份源格式，编译为目标框架格式：

```
源格式 (Harness Creator 原生)
    │
    ├── compiler.toClaudeCode()  → .md skill file + slash command
    ├── compiler.toCodex()       → .ts extension
    ├── compiler.toCursor()      → .cursorrules snippet
    └── compiler.toCline()       → custom slash command
```

这样一套 Harness 定义可以分发到所有支持的框架。

---

## 五、与现有方案的对比

### 5.1 vs Claude Code Router (CCR)

| 维度 | CCR | Harness Creator |
|------|-----|-----------------|
| **定位** | LLM 协议转换代理 | 工程 Task 编排 + 多框架适配 |
| **覆盖范围** | Layer 1 (LLM Provider) | Layer 1-5 (全栈) |
| **转换方向** | Anthropic ↔ OpenAI | 统一接口 ↔ N 个框架 |
| **任务编排** | 无（纯透传） | 有（Harness Step 引擎） |
| **Skill 系统** | 无 | 有（Skill Definition） |
| **关系** | **可作为 Layer 1 的参考实现** | 在 CCR 之上构建更高层抽象 |

### 5.2 vs LangChain / CrewAI 等 Agent 框架

| 维度 | LangChain / CrewAI | Harness Creator |
|------|--------------------|-----------------|
| **定位** | 通用 Agent 开发框架 | 编程领域专用 Task 编排 |
| **抽象层次** | Chain/Tool/Agent | Harness/Skill/Capability |
| **目标用户** | AI 应用开发者 | 软件工程师 |
| **领域知识** | 无（通用） | 内嵌软件工程最佳实践 |
| **框架绑定** | 自成体系 | 适配现有编程 Agent |

### 5.3 vs 直接写 Claude Code Skills

| 维度 | 直接写 .md Skill | Harness Creator |
|------|------------------|-----------------|
| **适用范围** | 仅 Claude Code | 多框架 |
| **模型切换** | 手动改配置 | 声明式路由 |
| **复用性** | 低（格式耦合） | 高（接口解耦） |
| **质量保障** | 无验收标准 | 内置 AcceptanceCriteria |
| **上手难度** | 低（简单即好） | 中等（先复杂后简单） |

---

## 六、实施路线图

### Phase 1: MVP（最小可行产品）— v0.1.x

**目标**: 在 Claude Code 上跑通一个完整的 Harness

| 序号 | 任务 | 产出 | 优先级 |
|------|------|------|--------|
| 1.1 | 定义 `IAgentCapabilities` 接口 | TypeScript interface 文件 | P0 |
| 1.2 | 实现 `ClaudeCodeAdapter` | 适配器实现（基于内置 Tool） | P0 |
| 1.3 | 定义 `HarnessDefinition` Schema | YAML Schema + TypeScript 类型 | P0 |
| 1.4 | 实现 Harness Step 引擎 | 步骤调度器（顺序执行） | P0 |
| 1.5 | 实现 `TerminalPresentationBackend` | 终端输出 | P0 |
| 1.6 | 编写第一个示例 Harness | Code Review Harness | P0 |
| 1.7 | 编写 3-5 个示例 Skill | 常用 Skill 库 | P1 |

**验收标准**: 用户能用 `harness run code-review` 在 Claude Code 中完成一次完整的代码审查。

### Phase 2: 多框架支持 — v0.2.x

**目标**: 支持 Codex CLI + Cline

| 序号 | 任务 | 产出 | 优先级 |
|------|------|------|--------|
| 2.1 | 实现 `CodexAdapter` | Codex CLI 适配器 | P0 |
| 2.2 | 实现 `ClineAdapter` | Cline 适配器 | P1 |
| 2.3 | 实现 `FrameworkAdapterRegistry` | 动态注册与发现 | P0 |
| 2.4 | 实现 `FallbackRegistry` | 降级策略引擎 | P1 |
| 2.5 | 实现 Skill 编译器 (→ Claude Code 格式) | .md 输出 | P1 |
| 2.6 | 实现 Skill 编译器 (→ Codex 格式) | .ts 输出 | P2 |

**验收标准**: 同一个 Code Review Harness 在 Claude Code、Codex、Cline 上都能跑通。

### Phase 3: LLM 统一层 — v0.3.x

**目标**: 集成 LLM Provider 抽象，支持模型路由

| 序号 | 任务 | 产出 | 优先级 |
|------|------|------|--------|
| 3.1 | 实现 `ILLMProviderAdapter` 接口 | 统一 LLM 调用接口 | P0 |
| 3.2 | 实现 OpenAI Adapter | OpenAI/GPT 系列 | P0 |
| 3.3 | 实现 Anthropic Adapter | Claude 系列 | P0 |
| 3.4 | 实现 DeepSeek/Qwen/Kimi Adapter | 国产模型 | P1 |
| 3.5 | 实现模型路由策略 | 按 task 类型选模型 | P1 |
| 3.6 | 集成流式输出支持 | Streaming pipeline | P2 |

**验收标准**: 用户可以在 Harness 定义中指定 `"model": "deepseek-chat"` 来降低成本。

### Phase 4: 生态建设 — v0.4.x+

| 序号 | 任务 | 产出 | 优先级 |
|------|------|------|--------|
| 4.1 | Harness Marketplace | 分发与发现机制 | P1 |
| 4.2 | Skill SDK | 第三方 Skill 开发工具包 | P1 |
| 4.3 | Cursor Adapter | IDE 集成 | P2 |
| 4.4 | CI/CD Integration | GitHub Actions / GitLab CI | P2 |
| 4.5 | Telemetry & Analytics | 使用数据收集（匿名） | P3 |
| 4.6 | Web Dashboard | 可视化管理界面 | P3 |

---

## 七、开放问题与风险

### 7.1 开放问题（待决策）

| ID | 问题 | 影响 | 建议 |
|----|------|------|------|
| O-001 | Harness 定义语言选 YAML 还是 TOML 还是自定义？ | 影响所有后续开发 | 先用 YAML（生态最广），后续可加 DSL |
| O-002 | 是否需要支持 Harness 之间的依赖和组合？ | 架构复杂度 | Phase 1 不支持，Phase 2+ 考虑 |
| O-003 | 验收标准的自动化检查能做到什么程度？ | 质量保障 | 先做 LLM Review（简单），再做规则引擎（复杂） |
| O-004 | 如何处理 Harness 执行过程中的长耗时操作？ | 用户体验 | 支持断点续执行 + 进度持久化 |
| O-005 | 安全边界：Harness 能执行任意命令吗？ | 安全性 | 默认沙箱模式，显式授权才允许危险操作 |

### 7.2 风险识别

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 框架 API 变更导致适配器失效 | 高 | 中 | 版本锁定 + 抽象隔离 + 自动化测试 |
| 抽象层过度设计导致性能损失 | 中 | 中 | 基准测试 + 按需优化热点路径 |
| 用户学习曲线陡峭 | 中 | 高 | 丰富示例 + 交互式引导 + 从简单开始 |
| 无法覆盖所有框架的特殊能力 | 高 | 低 | 明确标注 optional + 优雅降级 |
| MCP 成为事实标准使本架构部分冗余 | 低 | 低 | MCP 可作为底层传输层，不冲突 |

---

## 八、术语表

| 术语 | 定义 |
|------|------|
| **Harness** | 工程套件 — 封装一个完整工程任务的、可端到端执行的结构化定义 |
| **Skill** | 技能 — Harness 中的可复用能力单元，对应软件开发生命周期中的具体环节 |
| **Adapter** | 适配器 — 将统一接口转换为特定框架/厂商原生实现的组件 |
| **Capability** | 能力 — Agent 可执行的操作抽象（如读文件、执行命令） |
| **Step** | 步骤 — Harness 中的最小执行单元，包含一个 Action 和相关策略 |
| **LLM Provider** | LLM 提供商 — 提供大语言模型 API 服务的厂商（OpenAI、Anthropic 等） |
| **Framework** | 框架 — 编程 Agent 运行环境（Claude Code、Codex CLI、Cursor、Cline） |
| **MCP** | Model Context Protocol — Anthropic 提出的模型上下文协议，用于标准化工具调用 |
| **CCR** | Claude Code Router — 开源的 Claude Code 多模型路由代理 |
| **Acceptance Criteria** | 验收标准 — Harness 执行完成后必须满足的质量条件 |
| **Fallback Strategy** | 降级策略 — 目标能力不可用时的备选方案 |

---

## 九、附录

### 附录 A: 目录结构建议

```
harness-creator/
├── docs/
│   ├── harness-architecture-v0.1.0.md    ← 本文档
│   └── api-format-comparison-report.md   ← API 对比报告
├── packages/
│   ├── core/                             # 核心包
│   │   ├── src/
│   │   │   ├── types/                    # 所有 TypeScript 接口定义
│   │   │   │   ├── harness.ts            # HarnessDefinition 等
│   │   │   │   ├── skill.ts              # SkillDefinition 等
│   │   │   │   ├── capabilities.ts       # IAgentCapabilities 等
│   │   │   │   ├── llm.ts                # ILLMProviderAdapter 等
│   │   │   │   └── presentation.ts       # IPresentationBackend 等
│   │   │   ├── engine/                   # Harness 执行引擎
│   │   │   │   ├── step-executor.ts      # 步骤执行器
│   │   │   │   ├── harness-runner.ts     # Harness 运行器
│   │   │   │   └── acceptance-checker.ts # 验收检查器
│   │   │   ├── registry/                 # 注册表
│   │   │   │   ├── framework-registry.ts
│   │   │   │   ├── fallback-registry.ts
│   │   │   │   └── harness-registry.ts
│   │   │   └── compiler/                 # Skill 编译器
│   │   │       ├── to-claude-code.ts
│   │   │       ├── to-codex.ts
│   │   │       └── to-cursor.ts
│   │   └── package.json
│   │
│   ├── adapters/                         # 框架适配器包
│   │   ├── claude-code/
│   │   │   └── src/adapter.ts
│   │   ├── codex/
│   │   │   └── src/adapter.ts
│   │   ├── cline/
│   │   │   └── src/adapter.ts
│   │   └── cursor/
│   │       └── src/adapter.ts
│   │
│   ├── llm-providers/                   # LLM 提供商适配器包
│   │   ├── openai/src/adapter.ts
│   │   ├── anthropic/src/adapter.ts
│   │   ├── deepseek/src/adapter.ts
│   │   ├── qwen/src/adapter.ts
│   │   └── kimi/src/adapter.ts
│   │
│   └── presentation/                    # 展示层包
│       ├── terminal/src/backend.ts
│       ├── ide-panel/src/backend.ts
│       └── json/src/backend.ts
│
├── harnesses/                           # 内置 Harness 示例
│   ├── code-review/
│   │   └── harness.yaml
│   ├── test-generation/
│   │   └── harness.yaml
│   ├── refactoring/
│   │   └── harness.yaml
│   └── doc-generation/
│       └── harness.yaml
│
├── skills/                              # 内置 Skill 库
│   ├── analysis/
│   │   ├── code-understanding.skill.yaml
│   │   └── security-audit.skill.yaml
│   ├── generation/
│   │   ├── api-client.skill.yaml
│   │   └── unit-test.skill.yaml
│   └── utility/
│       ├── git-operation.skill.yaml
│       └── format-code.skill.yaml
│
└── examples/                            # 使用示例
    ├── getting-started/
    └── advanced/
```

### 附录 B: 参考资源

- [API 格式对比报告](./api-format-comparison-report.md) — 5 大 LLM 厂商 API 格式详细对比
- [Claude Code Router](https://github.com/musistudio/claude-code-router) — 协议转换层参考实现
- [CCR 转换器文档](https://musistudio.github.io/claude-code-router/zh-CN/docs/server/config/transformers/) — Transformer 接口设计参考
- [Anthropic Messages API](https://docs.anthropic.com/en/api/messages) — Claude 原生 API 规范
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat/create) — OpenAI API 规范
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — 工具调用标准协议
- [Cline](https://cline.bot/) — 开源 VS Code AI 编程助手
- [Cursor](https://cursor.com/) — AI-first IDE

---

*文档结束 — Harness Architecture v0.1.0 | 2026-04-22 | Draft*
