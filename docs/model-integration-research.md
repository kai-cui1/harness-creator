# 调研课题：传统软件系统 + LLM/Agent 混合架构的 Model 集成工作

> **调研日期**：2026-04-27
> **调研问题**：如果开发一个保留传统软件能力的系统，同时集成大模型（本质是 Software System + Agent 混合架构，非纯 Agent），在 model 集成部分需要做哪些工作？
> **定位**：Harness Creator 项目「技术学习与调研平台」产出

---

## 一、问题界定：什么是「非纯 Agent 的混合架构」？

### 1.1 与纯 Agent 系统的区别

| 维度 | 纯 Agent 系统 | 混合架构（本课题目标） |
|------|-------------|---------------------|
| **控制流** | LLM 驱动一切决策（ReAct 循环） | 传统代码控制主流程，LLM 作为能力增强层 |
| **状态管理** | 对话上下文 / Memory 对象 | 传统数据库 + 业务状态机 + LLM Context |
| **确定性** | 低 — 同一输入可能产生不同输出 | 高 — 核心业务逻辑确定，LLM 调用是可选/增强路径 |
| **失败模式** | 幻觉、循环、偏离任务 | LLM 调用失败时降级到传统逻辑 |
| **典型例子** | ChatGPT、Devin、AutoGPT | GitHub Copilot、Notion AI、Cursor、Figma AI |

### 1.2 Harness Creator 自身的定位

Harness Creator 正好属于这类混合架构：
- **传统软件部分**：MDL 解析/渲染/校验、文件管理、版本控制、Pipeline 编排、CLI
- **LLM 增强部分**：文档分析（Analyze）、行业知识补充（Search）、隐式知识推断、交互式确认建议生成
- **关键特征**：去掉 LLM 调用，系统仍然能跑（只是 Analyze 步骤需要人工完成）；加上 LLM，效率大幅提升

---

## 二、Model Integration Layer（MIL）整体架构

### 2.1 分层视图

```
┌─────────────────────────────────────────────────────────┐
│                    应用层 (Application)                   │
│   MDL Pipeline / CLI / Web UI / 编译器 / 版本管理         │
├─────────────────────────────────────────────────────────┤
│                 Model Integration Layer (MIL)             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ 调用网关  │  │ Prompt 管理│  │ 上下文组装│  │响应处理  │ │
│  │ Gateway  │  │  Mgmt     │  │ Assembler │  │Handler  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │              │              │     │
│  ┌────▼──────────────▼──────────────▼──────────────▼───┐ │
│  │                  统一运行时 (Runtime)                  │ │
│  │  重试 / 超时 / 限流 / 缓存 / 流式 / 批量 / 回退       │ │
│  └────────────────────┬────────────────────────────────┘ │
│                        │                                  │
│  ┌────────────────────▼────────────────────────────────┐ │
│  │                Provider 适配层                       │ │
│  │  OpenAI / Claude / DeepSeek / Qwen / 本地模型 ...    │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                   基础设施层 (Infrastructure)             │
│   向量数据库 / 对象存储 / 消息队列 / 监控 / 密钥管理      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 MIL 的核心职责

MIL 是应用代码与 LLM 之间的**唯一桥梁**。它不是简单封装 API 调用，而是承担以下职责：

1. **统一调用接口**：屏蔽不同 Provider 的 API 差异
2. **Prompt 生命周期管理**：模板化、版本化、A/B 测试
3. **上下文工程**：将业务数据高效地组装为 LLM 可理解的输入
4. **响应可靠性保障**：重试、降级、缓存、成本控制
5. **可观测性**：日志、追踪、指标、质量评估

---

## 三、六大子系统详细分析

### 子系统 1：调用网关（LLM Gateway）

#### 1.1 核心功能

```
应用代码 → [Gateway] → Provider A / Provider B / 本地模型
                    ↕
              [路由策略] / [负载均衡] / [故障转移]
```

**需要做的工作**：

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **统一请求/响应模型** | 定义与 Provider 无关的 Request/Response 数据结构 | P0 |
| **多 Provider 适配器** | 为每个 LLM 厂商写 Adapter（OpenAI/Claude/DeepSeek/Qwen/Ollama...） | P0 |
| **路由策略** | 按任务类型路由到不同模型（简单分类→小模型，复杂推理→大模型） | P1 |
| **故障转移** | 主 Provider 失败时自动切换到备用 Provider | P1 |
| **负载均衡** | 多个 API Key 轮询 / 权重分配 | P1 |
| **协议转换** | OpenAI 格式 ↔ Anthropic 格式 ↔ 自定义格式的转换 | P0 |

#### 1.2 关键设计决策

```python
# 统一请求模型示例
class LLMRequest(BaseModel):
    messages: list[ChatMessage]          # 统一消息格式
    model: str                           # 模型标识（可含 provider 前缀）
    temperature: float = 0.7
    max_tokens: int | None = None
    tools: list[ToolDefinition] | None = None  # 函数调用定义
    response_format: ResponseFormat | None = None
    metadata: dict = {}                  # 用于路由/计费/追踪的元数据

# 统一响应模型
class LLMResponse(BaseModel):
    content: str                          # 文本内容
    tool_calls: list[ToolCall] | None     # 函数调用结果
    usage: TokenUsage                     # Token 用量
    model: str                            # 实际使用的模型
    latency_ms: int                       # 响应延迟
    raw_response: dict | None = None      # 原始响应（调试用）
```

#### 1.3 参考实现

- **LiteLLM**（Python）：开源的统一 LLM API 代理，支持 100+ Provider
- **OpenRouter**：云端多模型路由服务
- **Portkey AI Gateway**：企业级 LLM Gateway（限流、缓存、日志、回退）
- **Claude Code Router（CCR）**：Anthropic 官方的协议转换参考实现

---

### 子系统 2：Prompt 管理系统

#### 2.1 核心挑战

Prompt 不是静态字符串，它是一个**需要持续迭代的工程制品**：

- 同一个任务可能有多版 Prompt（v1/v2/v3），需要 A/B 对比
- 不同模型对同一 Prompt 的响应差异很大
- Prompt 中嵌入的业务数据格式需要严格管控
- Prompt 变更需要可追溯、可回滚

#### 2.2 需要做的工作

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **模板引擎** | 支持 Jinja2/Mustache 风格的变量替换、条件逻辑、循环 | P0 |
| **版本管理** | 每个 Prompt 有版本号，支持历史查看和回滚 | P1 |
| **变量 Schema 定义** | 声明模板需要的变量及其类型/约束 | P0 |
| **Prompt 链编排** | 将复杂任务拆分为多个 Prompt 步骤（Chain-of-Thought） | P1 |
| **A/B 测试框架** | 同一任务使用不同 Prompt 版本，对比输出质量 | P2 |
| **效果评估** | 自动/半自动评估 Prompt 输出质量 | P2 |

#### 2.3 Prompt 模板结构示例

```yaml
# prompts/analyze-spec.yaml
name: analyze_specification
version: "1.2.0"
description: 从原始规范文档中提取方法论要素

input_schema:
  raw_content: string        # 原始文档文本
  doc_type: enum[product_doc, design_spec, code_standard, interaction_proto]
  extraction_focus: list[string]  # 提取重点方向

system_prompt: |
  你是一个专业的{doc_type}分析师。你的任务是...
  请重点关注以下方面：{extraction_focus}

user_prompt_template: |
  ## 待分析的文档

  {raw_content}

  ## 分析要求

  请按以下结构输出...

output_schema:
  methodology_elements: list[MethodologyElement]
  implicit_knowledge: list[ImplicitKnowledge]
  confidence_scores: dict
```

---

### 子系统 3：上下文组装器（Context Assembler）

#### 3.1 为什么需要独立的上下文组装？

LLM 的 Context Window 是有限且昂贵的资源。如何把业务数据**高效、精准**地塞进 Context，是一个独立的工程问题：

- **Token 预算管理**：总 Token 数不能超限，需要在 System/User/Tool 之间分配
- **信息优先级排序**：最重要的信息放前面（LLM 对开头和结尾更敏感）
- **动态裁剪**：当内容超限时，智能丢弃低优先级内容
- **RAG 集成**：从向量库检索相关片段作为上下文补充

#### 3.2 需要做的工作

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **Token 计数与预算分配** | 精确计算每个部分的 Token 数，支持动态调整 | P0 |
| **优先级队列** | 按重要性对上下文片段排序 | P0 |
| **摘要压缩** | 对长文本先做摘要再塞入 Context | P1 |
| **RAG 检索集成** | 向量相似度检索 + 重排序（Rerank） | P1 |
| **Few-shot 示例选择** | 动态选择最相关的 few-shot 示例 | P1 |
| **对话历史管理** | 滑动窗口 / 摘要压缩 / 关键信息保留 | P1 |

#### 3.3 上下文窗口分配策略

```
Context Window (e.g., 128K tokens)
├── System Prompt:      ~2K (固定)
├── Task Instructions:  ~3K (固定)
├── Few-shot Examples:  ~5K (动态选择)
├── Retrieved Context:  ~40K (RAG 检索结果)
├── Business Data:      ~50K (核心业务数据)
├── Conversation Hist:  ~20K (最近 N 轮)
├── Output Reserve:     ~8K (预留输出空间)
└──────────────────────────────
Total Budget:          ~128K
```

---

### 子系统 4：响应处理器（Response Handler）

#### 4.1 核心功能

LLM 返回的不是最终可用数据，需要经过处理后才能被应用层消费：

```
LLM Raw Response → [结构化解析] → [验证] → [后处理] → 应用层数据
```

#### 4.2 需要做的工作

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **结构化输出解析** | JSON Mode / Function Calling / 正则提取 → 结构化对象 | P0 |
| **输出校验** | 用 Pydantic/JSON Schema 校验返回数据的完整性 | P0 |
| **幻觉检测** | 基于规则/模型的轻量级事实核查 | P2 |
| **重试策略** | 校验失败时自动重试（带错误反馈） | P1 |
| **流式处理** | SSE/WebSocket 流式输出，支持打字机效果 | P1 |
| **Tool Call 解析** | 解析函数调用请求，分发到对应执行器 | P0（如果用 Tool Use） |

#### 4.3 结构化输出模式对比

| 模式 | 适用场景 | 可靠性 | 实现复杂度 |
|------|---------|--------|-----------|
| **JSON Mode** | 简单结构化输出 | 中 | 低 |
| **Function Calling** | 需要精确 schema 约束 | 高 | 中 |
| **Few-shot + 解析** | 复杂嵌套结构 | 中高 | 中 |
| **Guardrails/AI SDK** | 企业级严格要求 | 最高 | 高 |

---

### 子系统 5：运行时保障（Runtime Guarantees）

#### 5.1 需要做的工作

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **重试机制** | 指数退避重试，区分可重试错误（429/500/503）和不可重试（400/401/403） | P0 |
| **超时控制** | 单次请求超时 + 整体流程超时（避免无限等待） | P0 |
| **限流（Rate Limiting）** | 令牌桶/滑动窗口，防止触发 Provider 限制 | P0 |
| **语义缓存** | 相似查询命中缓存直接返回（节省成本和延迟） | P1 |
| **降级策略** | LLM 不可用时降级到规则引擎/模板/人工 | P1 |
| **异步执行** | 长时间任务异步化，支持轮询/Webhook 回调 | P1 |
| **批量处理** | 多个独立请求合并批处理（降低 API 调用次数） | P2 |

#### 5.2 降级策略矩阵

```
LLM 服务状态        应对策略
───────────────────────────────────────────
正常               → 使用 LLM（全功能）
延迟偏高(>10s)     → 使用缓存 / 简化 Prompt / 切换更快模型
间歇性失败         → 重试 + 故障转移
持续不可用(>5min)  → 降级到规则引擎 / 返回提示信息 / 排队等待
配额耗尽           → 切换 Provider / 降级 / 通知管理员
```

---

### 子系统 6：可观测性与治理（Observability & Governance）

#### 6.1 需要做的工作

| 工作 | 说明 | 优先级 |
|------|------|--------|
| **请求日志** | 记录每次调用的完整信息（request/response/metadata） | P0 |
| **链路追踪** | Trace ID 贯穿整个调用链，关联应用层和 MIL 层 | P1 |
| **指标采集** | 延迟 P50/P99、成功率、Token 用量、成本、错误率 | P0 |
| **成本追踪** | 按 User/Project/Feature 维度统计 LLM 成本 | P1 |
| **质量评估** | 输出质量的自动化/半自动化评估指标 | P2 |
| **安全审计** | Prompt 注入检测、PII 识别、敏感操作日志 | P1 |
| **密钥管理** | API Key 安全存储、轮换、权限隔离 | P0 |

#### 6.2 关键监控指标

```
┌─ 可靠性指标 ─┐   ┌─ 性能指标 ─┐   ┌─ 成本指标 ─┐   ┌─ 质量指标 ─┐
│ 请求成功率    │   │ P50 延迟    │   │ 日 Token 用量│   │ 输出合规率  │
│ 错误率(by type)│  │ P99 延迟    │   │ 日费用      │   │ 幻觉率估算  │
│ 重试率        │   │ TTFT(首token)│  │ 单次调用均费│   │ 用户满意度  │
│ 降级触发次数  │   │ 吞吐 QPS    │   │ 缓存命中率  │   │ A/B 对比分  │
└──────────────┘   └────────────┘   └────────────┘   └────────────┘
```

---

## 四、针对 Harness Creator 场景的具体分析

### 4.1 Harness Creator 中的 LLM 使用场景映射

| 场景 | 触发方式 | 输入 | 输出 | 可靠性要求 | 降级方案 |
|------|---------|------|------|-----------|---------|
| **规范文档分析** (Analyze) | Pipeline 步骤 | Axure HTML / PDF / Markdown | AnalysisResult（方法论要素） | 中（可重试） | 人工填写分析表单 |
| **行业知识搜索** (Search) | Analyze 后自动 | 提取的关键术语 | 补充上下文 | 低（增强型） | 跳过，使用已有知识 |
| **隐式知识推断** | Analyze 过程中 | 显式规则 + 设计产物 | ImplicitKnowledge | 中 | 标记为「待确认」 |
| **MDL Draft 生成** (Solidify) | Confirm 后 | AnalysisResult + ConfirmDecisions | MDLDraft | 高 | 手动编辑 MDL 模板 |
| **确认建议生成** (Confirm) | Pipeline 步骤 | AnalysisResult + 不确定项 | SuggestedConfirmItems | 低 | 展示全部不确定项供用户选 |
| **编译优化建议** | 编译过程 | MDL + 目标框架 | 编译建议 | 低 | 直接使用默认编译策略 |
| **Skill 效果评估** | 定期任务 | Skill + 测试用例 | EvaluationReport | 低 | 跳过评估 |

### 4.2 Harness Creator 的 MIL 架构建议

```
┌──────────────────────────────────────────────────┐
│              Harness Creator Application          │
│                                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Analyzer │  │Pipeline │  │Compiler │           │
│  └────┬────┘  └────┬────┘  └────┬────┘           │
├───────┼─────────────┼─────────────┼───────────────┤
│       ▼             ▼             ▼               │
│  ┌─────────────────────────────────────────┐     │
│  │        Harness MIL (Model Integration)    │     │
│  │                                          │     │
│  │  ┌──────────┐  ┌──────────────────────┐  │     │
│  │  │Prompt 库  │  │ Context Assembler    │  │     │
│  │  │analyze_  │  │ - Token 预算管理     │  │     │
│  │  │spec.yaml │  │ - RAG 检索(可选)     │  │     │
│  │  │confirm_  │  │ - Few-shot 选择      │  │     │
│  │  │items.yaml│  │                      │  │     │
│  │  └──────────┘  └──────────────────────┘  │     │
│  │                                          │     │
│  │  ┌────────────────────────────────────┐  │     │
│  │  │ Runtime: 重试/超时/缓存/降级/流式   │  │     │
│  │  └────────────────────────────────────┘  │     │
│  │                                          │     │
│  │  ┌────────────────────────────────────┐  │     │
│  │  │ Provider Adapters                  │  │     │
│  │  │ (OpenAI/Claude/DeepSeek/Ollama)    │  │     │
│  │  └────────────────────────────────────┘  │     │
│  └─────────────────────────────────────────┘     │
├──────────────────────────────────────────────────┤
│              Infrastructure                       │
│  文件系统 / 向量DB(未来) / 日志 / 监控            │
└──────────────────────────────────────────────────┘
```

### 4.3 MVP 阶段的 MIL 最小集合

对于 Harness Creator MVP，MIL 不需要一步到位。**最小可行集合**：

| 子系统 | MVP 范围 | 后续扩展 |
|--------|---------|---------|
| **调用网关** | 1 个 Provider 适配器（如 OpenAI 兼容接口）+ 统一 Request/Response 模型 | 多 Provider + 路由 + 故障转移 |
| **Prompt 管理** | YAML 模板文件 + Jinja2 渲染 + 变量 Schema | 版本管理 + A/B 测试 |
| **上下文组装** | 手动 Token 预算分配 + 优先级排序 | RAG + 自动摘要 + 动态裁剪 |
| **响应处理** | JSON Mode / Function Calling + Pydantic 校验 + 重试 | 流式 + 幻觉检测 |
| **运行时保障** | 重试（指数退避）+ 超时 + 简单日志 | 语义缓存 + 降级策略 + 异步 |
| **可观测性** | 结构化日志（request/response）+ Token 用量统计 | 链路追踪 + 成本面板 + 质量评估 |

---

## 五、技术选型参考

### 5.1 开源项目参考

| 项目 | 定位 | 语言 | 成熟度 | 适用场景 |
|------|------|------|--------|---------|
| **LiteLLM** | 统一 LLM API 代理 | Python | 高 | 替代手写 Gateway |
| **LangChain/LangGraph** | LLM 应用框架 | Python/JS | 高 | 复杂 Chain/Agent 编排 |
| **LlamaIndex** | RAG 框架 | Python/JS | 高 | 文档检索 + 上下文组装 |
| **Instructor** | 结构化输出 | Python | 中高 | Pydantic 模型驱动的输出解析 |
| **Promptfoo** | Prompt 评估工具 | JS | 中 | Prompt A/B 测试和质量评估 |
| **Portkey** | LLM Gateway | Node.js | 中高 | 生产级网关（限流/缓存/日志） |
| **Haystack** | RAG 管线 | Python | 中 | 企业级检索管线 |
| **DSPy** | 编程式 Prompt 优化 | Python | 中 | 自动 Prompt 优化 |

### 5.2 是否应该用 LangChain？

这是一个常见问题。结论取决于场景：

| 因素 | 用 LangChain | 不用 LangChain |
|------|------------|---------------|
| **项目阶段** | 快速原型验证 | 产品级系统 |
| **LLM 调用复杂度** | 多步 Chain / Agent 循环 | 少量明确的 LLM 调用点 |
| **团队规模** | 小团队 / 个人 | 有专职工程师 |
| **定制需求** | 标准流程够用 | 需要深度定制 MIL |
| **抽象偏好** | 接受高层抽象 | 想要完全掌控每一层 |

**对 Harness Creator 的建议**：MVP 阶段**不引入 LangChain**，原因：
1. Harness Creator 的 LLM 调用点是**明确且有限的**（Analyze/Search/Confirm/Solidify），不需要复杂的 Chain 编排
2. MIL 是项目的**核心竞争力**之一，需要完全可控
3. LangChain 的抽象层会增加调试难度
4. 可以选择性借鉴其设计思想（如 Output Parser、Retry 机制），但自己实现核心逻辑

---

## 六、实施路线图建议

### Phase 0：基础连通（1-2 天）
- [ ] 选定首个 LLM Provider（推荐 OpenAI 兼容接口，覆盖面最广）
- [ ] 实现 `LLMClient` 基类 + 首个 Adapter
- [ ] 实现最简单的 `chat_completion(request) -> response` 调用
- [ ] 写一个端到端测试：「发送 Hello → 收到回复」

### Phase 1：核心 MIL（3-5 天）
- [ ] 统一 `LLMRequest` / `LLMResponse` 数据模型
- [ ] Prompt 模板系统（YAML + Jinja2）
- [ ] 结构化输出（Function Calling / JSON Mode + Pydantic）
- [ ] 重试 + 超时 + 日志
- [ ] 在 Harness Pipeline 中接入第一个 LLM 调用点（如 Analyze 步骤）

### Phase 2：可靠性与效率（3-5 天）
- [ ] Token 计数与预算管理
- [ ] 上下文组装器（优先级队列 + 裁剪策略）
- [ ] 响应缓存（基于 prompt hash 的精确缓存）
- [ ] 成本追踪（按功能模块统计）
- [ ] 多 Provider 适配（第 2 个 Provider）

### Phase 3：高级能力（后续迭代）
- [ ] RAG 集成（行业知识库检索）
- [ ] Prompt A/B 测试框架
- [ ] 降级策略引擎
- [ ] 流式输出支持
- [ ] 质量评估仪表盘

---

## 七、关键风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| **LLM 输出不稳定** | 同一 Prompt 不同次调用结果差异大 | 结构化输出 + 校验 + 重试；关键路径加人工确认 |
| **API 成本失控** | Token 用量随用户增长爆炸 | Token 预算硬上限；缓存命中率优化；低成本模型兜底 |
| **Provider 服务中断** | 功能不可用 | 多 Provider + 降级策略；确保核心流程可脱离 LLM 运行 |
| **Prompt 注入攻击** | 用户通过输入操纵 LLM 行为 | 输入清洗 + System Prompt 加固 + 输出边界检查 |
| **上下文窗口不足** | 大文档无法一次处理完 | 分块策略 + Map-Reduce 模式 + 摘要压缩 |
| **模型快速迭代** | 今天好用的 Prompt 明天失效 | Prompt 版本管理 + 持续评估 + 自动告警 |

---

## 八、总结：MIL 的本质

Model Integration Layer 不是「调用 LLM API 的封装」，它是**传统软件系统与概率性 AI 能力之间的工程契约层**。

它的核心价值在于：

1. **解耦**：应用层不关心底层用的是哪个模型、哪个 Provider
2. **可靠性**：将不可靠的 LLM 调用包装为可靠的接口（重试、降级、校验）
3. **效率**：Token 预算管理、缓存、批量处理控制成本
4. **可迭代**：Prompt 作为一等公民，可以独立于应用代码进行优化
5. **可观测**：每一次 LLM 调用都是可追踪、可审计、可评估的

对于 Harness Creator 这样的混合架构系统，MIL 是**必须认真设计的核心基础设施**，而不是事后补上的胶水代码。
