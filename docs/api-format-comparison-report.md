# 主流大模型 API 格式规范与差异分析报告

> 调研时间：2026-04-22
> 涵盖范围：OpenAI、Claude (Anthropic) Opus、DeepSeek、Qwen (通义千问)、Kimi (Moonshot)

---

## 一、总览对比表

| 维度 | OpenAI | Claude (Anthropic) | DeepSeek | Qwen (阿里云百炼) | Kimi (Moonshot) |
|------|--------|-------------------|----------|-------------------|-----------------|
| **API 协议族** | Chat Completions / Responses | Messages (原生) | OpenAI 兼容 | OpenAI 兼容 + DashScope 原生 | OpenAI 兼容 |
| **Base URL** | `https://api.openai.com/v1` | `https://api.anthropic.com/v1` | `https://api.deepseek.com` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `https://api.moonshot.cn/v1` |
| **认证方式** | `Authorization: Bearer <key>` | `x-api-key: <key>` + `anthropic-version` header | `Authorization: Bearer <key>` | `Authorization: Bearer <key>` | `Authorization: Bearer <key>` |
| **端点路径** | `/chat/completions` | `/messages` | `/chat/completions` | `/chat/completions` | `/chat/completions` |
| **系统提示位置** | messages 中 role=system 或 role=developer | 顶层 `system` 参数（不在 messages 中） | messages 中 role=system | messages 中 role=system | messages 中 role=system |
| **最大输出 Token** | 模型相关 (最高 ~100K+) | 最高 300K (beta header) | 8K (V3.2) | 模型相关 | 模型相关 |
| **流式输出** | SSE (`stream: true`) | SSE (`stream: true`) | SSE (`stream: true`) | SSE (`stream: true`) | SSE (`stream: true`) |
| **SDK 兼容性** | 官方 SDK | 官方 SDK + OpenAI SDK 兼容层 | 可直接用 OpenAI SDK | 可用 OpenAI SDK 或 DashScope SDK | 可直接用 OpenAI SDK |
| **多模态支持** | 文本+图像+音频 | 文本+图像+PDF | 文本+图像 | 文本+图像+音频 | 文本+图像+视频 |
| **工具调用 (Tool Use)** | tools/function_calling | tools (tool_use blocks) | tool_calls | tools | tool_use |
| **思考模式 (Reasoning)** | reasoning_effort 参数 | thinking 对象 (budget_tokens) | deepseek-reasoner 模型 | 支持 (enable_thinking) | thinking 参数 (k2.5) |

---

## 二、逐家详细分析

### 2.1 OpenAI — Chat Completions API

**当前状态：正在向 Responses API 迁移，Chat Completions 仍广泛使用**

#### 请求格式

```json
POST https://api.openai.com/v1/chat/completions
Headers:
  Authorization: Bearer $OPENAI_API_KEY
  Content-Type: application/json

{
  "model": "gpt-4o" | "gpt-5.2" | "o3" | ...,
  "messages": [
    {"role": "developer", "content": "You are a helpful assistant."},  // 新版用 developer 替代 system
    {"role": "user", "content": "Hello!"}
  ],
  // === 核心参数 ===
  "max_completion_tokens": 4096,        // 推荐（替代已废弃的 max_tokens）
  "temperature": 1,                      // 范围 [0, 2]，默认 1
  "top_p": 1,                            // 范围 [0, 1]
  "n": 1,                                // 生成几个候选
  "stream": false,
  "stop": null | string[],               // 最多 4 个停止序列

  // === 推理模型专属 ===
  "reasoning_effort": "medium",          // none|minimal|low|medium|high|xhigh

  // === 工具调用 ===
  "tools": [...],
  "tool_choice": "auto" | "none" | "required" | {...},
  "parallel_tool_calls": true,

  // === 结构化输出 ===
  "response_format": {
    "type": "json_schema",               // 或 "json_object"
    "json_schema": { "name": "...", "strict": true, "schema": {...} }
  },

  // === 高级功能 ===
  "presence_penalty": 0,                 // [-2, 2]
  "frequency_penalty": 0,                // [-2, 2]
  "logit_bias": null,                    // token ID -> bias 值 [-100, 100]
  "logprobs": false,                     // 是否返回 log probabilities
  "top_logprobs": null,                  // 返回 top N 的 logprob
  "seed": null,                          // 用于确定性采样 (Beta)
  "modalities": ["text"],                // ["text"] 或 ["text","audio"]
  "audio": { "voice": "alloy", "format": "pcm16" },
  "prediction": { "content": "..." },    // Predicted Output (加速)
  "service_tier": "auto",                // auto|default|flex|priority
  "store": false,                        // 存储用于 distillation/evals
  "metadata": {},
  "user": null,                          // 已被 prompt_cache_key 替代
  "prompt_cache_key": null,              // 缓存优化
  "prompt_cache_retention": null,        // "24h" 扩展缓存
  "safety_identifier": null,             // 用户标识 (Beta)
  "verbosity": "medium",                 // low|medium|high (控制输出详略)
  "web_search_options": null             // 网络搜索工具
}
```

#### 响应格式

```json
{
  "id": "chatcmpl-B9MBs8CjcvOU2jLn4n570S5qMJKcT",
  "object": "chat.completion",
  "created": 1741570283,
  "model": "gpt-4o-2024-08-06",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I assist you?",
      "refusal": null,
      "annotations": []
    },
    "logprobs": null,
    "finish_reason": "stop"              // stop | length | tool_calls | content_filter
  }],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 10,
    "total_tokens": 29,
    "prompt_tokens_details": { "cached_tokens": 0, "audio_tokens": 0 },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    }
  },
  "service_tier": "default",
  "system_fingerprint": "fp_fc9f1d7035"
}
```

#### 关键特性

- **双协议并存**：Chat Completions（传统）+ Responses API（新版推荐，2026年8月后 Assistants API 迁移截止）
- **role 变更**：新版本使用 `developer` 替代 `system`
- **reasoning_effort**：推理模型专用，6档可调
- **结构化输出**：支持 JSON Schema 强约束 (`json_schema.strict: true`)
- **Predicted Output**：已知大部分输出时可大幅加速
- **音频输入输出**：gpt-4o-audio-preview 支持语音交互
- **Service Tier**：default/flex/priority 三档服务等级

---

### 2.2 Claude (Anthropic) — Messages API

**核心特点：完全独立的 API 格式，与 OpenAI 不兼容（但有兼容层）**

#### 请求格式

```json
POST https://api.anthropic.com/v1/messages
Headers:
  x-api-key: $ANTHROPIC_API_KEY
  anthropic-version: 2023-06-01           // 必需！
  content-type: application/json
  anthropic-beta: interleaved-thinking-2025-05-14  // Beta 功能需要此 header

{
  "model": "claude-opus-4-20250514" | "claude-sonnet-4-20250514",
  "max_tokens": 1024,                     // 必填！无默认值

  // === 系统提示（顶层参数，不在 messages 中）===
  "system": "You are a helpful assistant."
  // 或结构化形式：
  // "system": [{ "type": "text", "text": "..." }],

  // === 消息（只有 user 和 assistant 两种角色）===
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What is LLM?"}
  ],

  // === 核心采样参数 ===
  "temperature": 1,                       // [0, 1] 默认 1
  "top_p": 0.7,                           // [0, 1]
  "top_k": 40,                            // Anthropic 独有参数
  "stop_sequences": ["\n\nHuman:"],       // 注意名称不同！

  // === 流式输出 ===
  "stream": true,

  // === 思考模式 (Extended Thinking) ===
  "thinking": {
    "type": "enabled",
    "budget_tokens": 1024                 // 必须 >= 1024
  },

  // === 工具调用 ===
  "tools": [
    {
      "name": "get_weather",
      "description": "Get weather for a location",
      "input_schema": {                   // 用 input_schema 而非 parameters
        "type": "object",
        "properties": { "location": { "type": "string" } },
        "required": ["location"]
      }
    }
  ],
  "tool_choice": { "type": "auto" },     // auto|any|tool|none
  // "tool_choice": { "type": "tool", "name": "get_weather" },

  // === 其他 ===
  "metadata": { "user_id": "uuid-..." },
  "service_tier": "auto",                 // auto|standard_only
  "container": "container_id",            // 容器复用
  "mcp_servers": [...]                    // MCP 服务器集成
}
```

#### 响应格式

```json
{
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message",
  "role": "assistant",
  "content": [
    { "type": "text", "text": "Hi! My name is Claude." }
  ],
  "model": "claude-sonnet-4-20250514",
  "stop_reason": "end_turn",              // end_turn|max_tokens|stop_sequence|tool_use|pause_turn|refusal
  "stop_sequence": null,
  "usage": {
    "input_tokens": 2095,
    "output_tokens": 503,
    "cache_creation_input_tokens": 2051,   // 缓存创建消耗
    "cache_read_input_tokens": 2051       // 缓存读取节省
  }
}
```

#### 与 OpenAI 的核心差异

| 维度 | OpenAI | Claude |
|------|--------|--------|
| 认证 header | `Authorization: Bearer` | `x-api-key:` + `anthropic-version:` |
| 系统提示 | messages 中 `{role: "system"}` | 顶层 `"system"` 参数 |
| max_tokens | 可选，有默认值 | **必填**，无默认值 |
| 停止序列 | `stop` (string[]) | `stop_sequences` (string[]) |
| 工具定义 | `parameters` (JSON Schema) | `input_schema` (JSON Schema) |
| 工具调用返回 | `choices[].message.tool_calls` | `content[]` 中 `{type: "tool_use"}` block |
| 工具结果回传 | messages 中 role=tool | messages 中 `{type: "tool_result"}` block |
| finish_reason | `stop\|length\|tool_calls` | `end_turn\|max_tokens\|stop_sequence\|tool_use` |
| usage 字段 | prompt/completion/total tokens | input/output tokens + cache 细分 |
| 思考模式 | `reasoning_effort` (字符串枚举) | `thinking.budget_tokens` (整数) |
| 额外采样参数 | 无 | `top_k` (独有) |
| 内容块类型 | 纯文本 string | 数组 `[{type: "text"}]` |
| 输出上限 | 模型限制 | 最高 **300k** (beta header) |
| 多模态 | image_url 格式 | base64 inline 或 URL |

---

### 2.3 DeepSeek — OpenAI 兼容格式

**核心特点：完全兼容 OpenAI Chat Completions 格式，可直接使用 OpenAI SDK**

#### 请求格式

```json
POST https://api.deepseek.com/chat/completions
// 也支持: POST https://api.deepseek.com/v1/chat/completions
Headers:
  Authorization: Bearer $DEEPSEEK_API_KEY
  Content-Type: application/json

{
  "model": "deepseek-chat" | "deepseek-reasoner",
  // deepseek-chat = DeepSeek-V3.2 (非思考模式)
  // deepseek-reasoner = DeepSeek-V3.2 (思考模式/R1风格)

  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],

  // === 标准参数 (与 OpenAI 一致) ===
  "temperature": 1.0,
  "top_p": 1.0,
  "max_tokens": 4096,
  "stream": false,
  "stop": null,

  // === DeepSeek 特有/差异 ===
  // 思考模式通过 model 切换，而非参数
  // deepseek-reasoner 自动启用链式思考 (Chain-of-Thought)

  // === 工具调用 (OpenAI 兼容) ===
  "tools": [...],
  "tool_choice": "auto",

  // === 其他 OpenAI 兼容参数 ===
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "response_format": { "type": "json_object" },
  "n": 1
}
```

#### 响应格式

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "deepseek-chat",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Response text here"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

#### 关键特性

- **纯 OpenAI 兼容**：改 `base_url` 即可用 OpenAI SDK 直接调用
- **思考模式切换**：通过 `model` 字段选择 `deepseek-chat`(非思考) 或 `deepseek-reasoner`(思考)，而非额外参数
- **Context Caching**：支持 Prompt Caching（2024年8月起）
- **FIM Completion (Beta)**：填充中间补全
- **Chat Prefix Completion (Beta)**：聊天前缀补全
- **Anthropic API 兼容**：同时提供 Anthropic Messages API 兼容接口
- **模型版本**：
  - `deepseek-chat` → DeepSeek-V3.2 (128K context)
  - `deepseek-reasoner` → DeepSeek-V3.2 思考模式

---

### 2.4 Qwen (通义千问 / 阿里云百炼)

**核心特点：双协议支持 — OpenAI 兼容 + DashScope 原生**

#### 方式一：OpenAI 兼容接口（推荐迁移使用）

```json
POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
Headers:
  Authorization: Bearer $DASHSCOPE_API_KEY
  Content-Type: application/json

{
  "model": "qwen-plus" | "qwen-max" | "qwen-turbo" | "qwen-long" | "qwen-vl-max" | ...,
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "你好"}
  ],

  // === 核心参数 ===
  "max_tokens": 1500,
  "temperature": 0.85,                   // 默认值因模型而异
  "top_p": 0.8,
  "repetition_penalty": 1.0,             // Qwen 独有：重复惩罚
  "stream": false,
  "stop": null,

  // === 启用联网搜索 ===
  "enable_search": false,                // Qwen 独有功能

  // === 工具调用 ===
  "tools": [...],
  "tool_choice": "auto",

  // === 结构化输出 ===
  "response_format": { "type": "json_object" },

  // === 思考模式 ===
  "enable_thinking": false,              // 启用深度思考
  "thinking_budget": null                // 思考 token 预算
}
```

#### 方式二：DashScope 原生接口

```json
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
Headers:
  Authorization: Bearer $DASHSCOPE_API_KEY
  Content-Type: application/json

{
  "model": "qwen-plus",
  "input": {
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "你好"}
    ]
  },
  "parameters": {
    "result_format": "message",           // message | text
    "max_tokens": 1500,
    "temperature": 0.85,
    "top_p": 0.8,
    "repetition_penalty": 1.0,
    "enable_search": false,
    "enable_thinking": false,
    "seed": 123456                       // 随机种子
  }
}

// 原生响应格式（注意结构不同）:
{
  "output": {
    "choices": [{
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "我是来自阿里云的大规模语言模型..."
      }
    }]
  },
  "usage": {
    "total_tokens": 38,
    "output_tokens": 16,
    "input_tokens": 22
  },
  "request_id": "87f776d7-3c82-9d39-b238-d1ad38c6b9a6"
}
```

#### 关键特性

- **双协议**：OpenAI 兼容（迁移成本低）+ DashScope 原生（功能最完整）
- **联网搜索**：`enable_search: true` 即可开启网络检索增强生成
- **重复惩罚**：`repetition_penalty` 参数（部分国产模型特有）
- **长文档**：`qwen-long` 支持超长上下文（10M+ tokens）
- **多模态**：`qwen-vl-max` 等视觉语言模型
- **Responses API**：也支持 OpenAI 新版 Responses API 格式
- **丰富的模型矩阵**：qwen-turbo(速度)/qwen-plus(均衡)/qwen-max(质量)/qwen-coder(代码)

---

### 2.5 Kimi (Moonshot AI) — OpenAI 兼容格式

**核心特点：OpenAI 兼容格式，但有多项独有扩展**

#### 请求格式

```json
POST https://api.moonshot.cn/v1/chat/completions
Headers:
  Authorization: Bearer $MOONSHOT_API_KEY
  Content-Type: application/json

{
  "model": "kimi-k2.5" | "kimi-k2-0711-preview" | "moonshot-v1-128k" | ...,
  "messages": [
    {"role": "system", "content": "你是 Kimi..."},
    {"role": "user", "content": "你好"}
  ],

  // === 标准参数 ===
  "max_completion_tokens": 1024,         // 注意：max_tokens 已废弃
  "temperature": 0.6,                    // k2系列默认 0.6, k2.5不可修改
  "top_p": 0.95,                         // k2.5 默认 0.95 且不可修改
  "presence_penalty": 0,
  "frequency_penalty": 0,
  "stream": false,
  "stop": null,
  "n": 1,                               // 最大 5

  // === Kimi 独有参数 ===
  "thinking": { "type": "enabled" },     // 仅 k2.5 有效，控制是否启用思考
                                        //   enabled | disabled
  "prompt_cache_key": "session-abc123",  // 缓存优化（Agent 场景建议必填）
  "safety_identifier": "user-hash-xxx",  // 安全标识符

  // === 标准扩展 ===
  "response_format": { "type": "json_object" },
  "tools": [...],
  "tool_choice": "auto",

  // === 流式选项 ===
  "stream_options": {
    "include_usage": true                // 流式中包含 usage 统计
  }
}
```

#### 响应格式

```json
{
  "id": "cmpl-04ea926191a14749b7f2c7a48a68abc6",
  "object": "chat.completion",
  "created": 1698999496,
  "model": "kimi-k2.5",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": " 你好，李雷！1+1等于2。"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 19,
    "completion_tokens": 21,
    "total_tokens": 40,
    "cached_tokens": 10                  // 缓存命中 token 数
  }
}
```

#### 关键特性

- **OpenAI 兼容**：可直接用 OpenAI SDK，只需改 `base_url`
- **最新模型 k2.5**：多模态理解与处理，部分参数锁定不可修改（temperature/top_p/n 等）
- **视频理解**：支持 `video_url` 类型的 content（目前唯一一家在标准 API 中支持视频的）
- **思考控制**：`thinking` 参数控制 k2.5 的思考开关
- **缓存优化**：`prompt_cache_key` 建议 Agent 场景使用 session/task id
- **文件问答**：独立文件上传 API + 文件引用能力
- **Partial Mode**：支持增量更新模式
- **联网搜索**：内置 web_search 工具
- **模型列表丰富**：moonshot-v1 系列 (8k/32k/128k) + kimi-k2 系列 + k2-thinking 系列

---

## 三、关键维度横向对比

### 3.1 认证与连接

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| Auth Header | `Authorization: Bearer` | `x-api-key:` | `Authorization: Bearer` | `Authorization: Bearer` | `Authorization: Bearer` |
| 版本 Header | 无 | `anthropic-version: 2023-06-01` (必需) | 无 | 无 | 无 |
| Beta Header | 无 | `anthropic-beta:` (按需) | 无 | 无 | 无 |
| Base URL | `api.openai.com/v1` | `api.anthropic.com/v1` | `api.deepseek.com` | `dashscope.aliyuncs.com/compatible-mode/v1` | `api.moonshot.cn/v1` |
| SDK | openai Python/Node SDK | @anthropic-ai/sdk | openai SDK (直用) | openai SDK / dashscope SDK | openai SDK (直用) |

### 3.2 消息结构与角色

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| system 角色 | `role: "system"` 或 `"developer"` | **顶层 `system` 参数** | `role: "system"` | `role: "system"` | `role: "system"` |
| user 角色 | `role: "user"` | `role: "user"` | `role: "user"` | `role: "user"` | `role: "user"` |
| assistant 角色 | `role: "assistant"` | `role: "assistant"` | `role: "assistant"` | `role: "assistant"` | `role: "assistant"` |
| tool 角色 | `role: "tool"` | `{type: "tool_result"}` block | `role: "tool"` | `role: "tool"` | `role: "tool"` |
| developer 角色 | `role: "developer"` (新版) | N/A | N/A | N/A | N/A |
| content 类型 | string 或 array | **必须为数组** `[{type:"text"}]` | string 或 array | string 或 array | string 或 array |
| 多模态 content | `image_url` | base64 inline | `image_url` | `image_url` | `image_url` + `video_url` |

### 3.3 采样与生成控制

| 参数 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| temperature | [0, 2], 默认 1 | [0, 1], 默认 1 | [0, 2], 默认 1 | [0, 2], 因模型而异 | [0, 1], k2.5 锁定不可改 |
| top_p | [0, 1], 默认 1 | [0, 1] | [0, 1], 默认 1 | [0, 1] | [0, 1], k2.5 锁定 0.95 |
| top_k | 无 | **有** (整数) | 无 | 无 | 无 |
| max_tokens | `max_completion_tokens` (推荐) | **必填** `max_tokens` | `max_tokens` | `max_tokens` | `max_completion_tokens` |
| stop | `stop` (str[], 最多4个) | `stop_sequences` (str[]) | `stop` | `stop` | `stop` (str[], 最多5个, 每个≤32字节) |
| seed | 有 (Beta) | 无 | 无 | DashScope 原生有 | 无 |
| presence_penalty | [-2, 2] | 无 | [-2, 2] | 无 | [-2, 2], k2.5 不可改 |
| frequency_penalty | [-2, 2] | 无 | [-2, 2] | 无 | [-2, 2], k2.5 不可改 |
| repetition_penalty | 无 | 无 | 无 | **有** (Qwen 特有) | 无 |
| logit_bias | 有 (token ID → bias) | 无 | 无 | 无 | 无 |
| logprobs | 有 | 无 | 无 | 无 | 无 |
| verbosity | 有 (low/med/high) | 无 | 无 | 无 | 无 |

### 3.4 思考/推理模式 (Reasoning / Thinking)

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| 触发方式 | `reasoning_effort` 参数 | `thinking` 对象 | **切换 model** | `enable_thinking` 参数 | `thinking` 参数 |
| 控制粒度 | 枚举: none/minimal/low/medium/high/xhigh | 整数 budget_tokens | 开/关 (换模型) | 布尔 + 可选 budget | 开/关 (enabled/disabled) |
| 输出可见性 | reasoning_tokens 在 usage 中 | thinking content block | 在 content 中返回 | - | - |
| 支持模型 | o-series, gpt-5.1+ | 全系列 (beta) | deepseek-reasoner | 部分模型 | kimi-k2.5, k2-thinking |

### 3.5 工具调用 (Function Calling / Tool Use)

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| 定义字段 | `tools[].function.parameters` | `tools[].input_schema` | 同 OpenAI | 同 OpenAI | 同 OpenAI |
| 选择控制 | `tool_choice` | `tool_choice` | `tool_choice` | `tool_choice` | `tool_choice` |
| 并行调用 | `parallel_tool_calls` | `disable_parallel_tool_use` | 支持 | 支持 | 支持 |
| 返回位置 | `choices[0].message.tool_calls` | `content[]` 中 `tool_use` block | 同 OpenAI | 同 OpenAI | 同 OpenAI |
| 返回格式 | `[{id, type, function: {name, args}}]` | `[{type, id, name, input}]` | 同 OpenAI | 同 OpenAI | 同 OpenAI |
| 结果回传 | `{role: "tool", tool_call_id, content}` | `{type: "tool_result", tool_use_id, content}` | 同 OpenAI | 同 OpenAI | 同 OpenAI |
| 结构化输出 | `response_format.json_schema` | 可通过 tool use 模拟 | `response_format` | `response_format` | `response_format` |

### 3.6 流式输出 (Streaming)

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| 协议 | SSE | SSE | SSE | SSE | SSE |
| 触发 | `stream: true` | `stream: true` | `stream: true` | `stream: true` | `stream: true` |
| 数据格式 | `data: {...}\n\n` | `event: ...\ndata: ...\n\n` | 同 OpenAI | 同 OpenAI | 同 OpenAI |
| 事件类型 | 无事件名 (纯 data) | **有事件名** (message_start, content_block_start, etc.) | 无 | 无 | 无 |
| 结束标记 | `data: [DONE]` | `message_stop` event | `data: [DONE]` | `data: [DONE]` | `data: [DONE]` |
| usage 获取 | 最后 chunk / stream_options | message_start + message_delta | 最后 chunk | 最后 chunk | stream_options.include_usage |
| delta 格式 | `{delta: {role, content}}` | `{delta: {type, text}}` (content_block_delta) | 同 OpenAI | 同 OpenAI | 同 OpenAI |

### 3.7 Usage / Token 计费

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| prompt tokens | `usage.prompt_tokens` | `usage.input_tokens` | `usage.prompt_tokens` | `usage.input_tokens` | `usage.prompt_tokens` |
| completion tokens | `usage.completion_tokens` | `usage.output_tokens` | `usage.completion_tokens` | `usage.output_tokens` | `usage.completion_tokens` |
| total tokens | `usage.total_tokens` | 手动计算 | `usage.total_tokens` | `usage.total_tokens` | `usage.total_tokens` |
| 缓存统计 | `prompt_tokens_details.cached_tokens` | `cache_creation_*` + `cache_read_*` | 有 | DashScope 原生有 | `cached_tokens` |
| 推理 token | `completion_tokens_details.reasoning_tokens` | 含在 output_tokens 中 | 有 (reasoning_content) | - | - |
| 音频 token | `*_details.audio_tokens` | 无 | 无 | 无 | 无 |

### 3.8 错误处理

| 项目 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|------|--------|--------|----------|------|------|
| 错误格式 | `{error: {message, type, code, param}}` | `{error: {type, message}}` | 类 OpenAI | `{code, message, request_id}` | `{error: {type, message}}` |
| 401 | invalid_api_key | authentication_error | - | InvalidApiKey | incorrect_api_key_error |
| 400 | invalid_request_error | invalid_request_error | - | InvalidParameter | invalid_request_error |
| 429 | rate_limit_exceeded | rate_limit_error | - | RateLimitReached | rate_limit_reached_error |
| 500 | server_error | overloaded_error | - | InternalServer | engine_overloaded_error |
| 内容过滤 | content_filter | - | - | - | content_filter |

---

## 四、统一抽象层设计要点（对 Harness 工程套件的启示）

基于以上差异分析，如果需要构建一个统一的 LLM 调用抽象层（这正是 Harness Creator 的目标），需要处理以下关键适配点：

### 4.1 必须适配的核心差异

```
┌─────────────────────────────────────────────────────────────┐
│                    统一抽象层 (Unified Layer)                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 连接适配 (Connection Adapter)                           │
│     ├── Auth: Bearer Token vs x-api-key + version header    │
│     ├── Base URL 映射                                       │
│     └── Header 差异处理                                     │
│                                                             │
│  2. 消息适配 (Message Adapter)                              │
│     ├── system 提示: messages内 vs 顶层参数 (Claude)        │
│     ├── role 映射: system/developer → 各家对应关系          │
│     ├── content 格式: string vs content block array         │
│     └── 多模态: image_url/video_url 格式统一                │
│                                                             │
│  3. 参数适配 (Parameter Adapter)                            │
│     ├── max_tokens / max_completion_tokens 统一             │
│     ├── stop / stop_sequences 名称映射                      │
│     ├── temperature 范围归一化: [0,2] →各家实际范围         │
│     └── 独有参数透传: top_k, repetition_penalty 等          │
│                                                             │
│  4. 工具适配 (Tool Adapter)                                 │
│     ├── 定义格式: parameters vs input_schema                │
│     ├── 返回解析: tool_calls vs tool_use content blocks     │
│     ├── 结果回传: role:tool vs type:tool_result            │
│     └── 并行调用控制差异                                    │
│                                                             │
│  5. 流式适配 (Streaming Adapter)                            │
│     ├── SSE 事件格式: 有事件名 vs 无事件名                   │
│     ├── delta 解析: 格式差异                                │
│     └── usage 获取时机差异                                  │
│                                                             │
│  6. 响应适配 (Response Adapter)                             │
│     ├── finish_reason 映射                                  │
│     ├── usage 字段名映射                                    │
│     ├── 缓存/推理 token 统计差异                            │
│     └── 错误格式统一化                                      │
│                                                             │
│  7. 思维适配 (Thinking Adapter)                             │
│     ├── reasoning_effort (枚举) ↔ budget_tokens (整数)      │
│     ├── 模型切换方式 (DeepSeek) ↔ 参数控制 (其他)           │
│     └── 思考内容提取和展示                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 推荐的统一数据模型

```typescript
// 统一请求模型
interface UnifiedChatRequest {
  model: string;
  messages: UnifiedMessage[];
  systemPrompt?: string;                    // 统一的系统提示
  maxTokens?: number;
  temperature?: number;                     // 归一化到 [0, 2]
  topP?: number;
  stopSequences?: string[];
  stream?: boolean;
  tools?: UnifiedToolDefinition[];
  toolChoice?: UnifiedToolChoice;
  thinking?: UnifiedThinkingConfig;        // 统一思维配置
  responseFormat?: UnifiedResponseFormat;

  // 独有参数透传包
  providerExtras?: Record<string, any>;
}

// 统一响应模型
interface UnifiedChatResponse {
  id: string;
  model: string;
  content: string;
  finishReason: UnifiedFinishReason;       // 统一的结束原因枚举
  usage: UnifiedUsage;
  toolCalls?: UnifiedToolCall[];
  thinkingContent?: string;                // 统一的思考内容
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
```

### 4.3 各家兼容性评级

| 评估维度 | OpenAI | Claude | DeepSeek | Qwen | Kimi |
|----------|--------|--------|----------|------|------|
| **OpenAI 兼容程度** | 基准 (100%) | 低 (~30%) | 高 (~95%) | 高 (~90%) | 高 (~92%) |
| **迁移成本（从 OpenAI）** | N/A | 高 | 极低 | 低 | 极低 |
| **独特价值** | Responses API, Audio, Structured Outputs | 300K 输出, Thinking, MCP, Tool生态 | 性价比, R1 推理 | 联网搜索, 长文档, 双协议 | 视频, 缓存优化, k2.5 |
| **SDK 直用** | openai SDK | anthropic SDK | openai SDK | openai/dashscope SDK | openai SDK |
| **适合 Harness 抽象** | 基准 | 需要重点适配 | 简单映射 | 简单映射 + 原生可选 | 简单映射 |

---

## 五、总结与建议

### 5.1 格式阵营划分

```
┌─────────────────────────────────────────────────────────┐
│                   API 格式三大阵营                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔵 OpenAI 格式阵营 (主流，占市场 ~80%)                  │
│  ├── OpenAI (原始定义者)                                │
│  ├── DeepSeek (高度兼容)                                │
│  ├── Qwen / 通义千问 (高度兼容 + 原生扩展)              │
│  ├── Kimi / Moonshot (高度兼容 + 独有扩展)              │
│  └── 其他: 智谱GLM、零一万物、百川、MiniMax 等          │
│                                                         │
│  🟣 Anthropic 原生格式 (独立体系)                        │
│  └── Claude (Messages API)                              │
│      └── 提供了 OpenAI SDK 兼容层 (有限功能)            │
│                                                         │
│  🟢 Google Gemini 格式 (另一独立体系，未在本报告覆盖)    │
│  └── generateContent API                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 对 Harness Creator 项目的建议

1. **以 OpenAI 格式为基准**：因为 DeepSeek/Qwen/Kimi 都高度兼容，覆盖最广
2. **重点适配 Claude**：它是唯一完全不同格式的头部玩家，且能力突出
3. **分层设计**：
   - **L1 兼容层**：处理 OpenAI 阵营内部的微小差异（参数名、默认值等）
   - **L2 适配层**：处理 Claude 的结构性差异（消息格式、工具格式、流式格式）
   - **L3 扩展层**：各家的独有功能（联网搜索、视频、MCP 等）作为可选插件
4. **关注动态变化**：OpenAI 正在向 Responses API 迁移，Claude 持续迭代 beta 功能

---

## 六、Claude Code Router — 协议转换层实战分析

> 本节补充分析 **Claude Code Router (CCR)** 的协议实现架构。CCR 是目前最成熟的 Claude Code 多模型路由方案，其核心价值在于：**让 Claude Code（原生使用 Anthropic Messages API）能够透明地调用任意 OpenAI 兼容的 LLM 提供商**。

### 6.1 项目概览

| 项目 | 说明 |
|------|------|
| **GitHub** | [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router) (主仓库) |
| **Fork 增强** | [Darthwares/ccr-next](https://github.com/Darthwares/ccr-next) (功能增强版) |
| **核心定位** | Claude Code 的请求代理 + 模型路由器 + 协议转换引擎 |
| **运行方式** | 本地 HTTP 代理服务（默认 `127.0.0.1:3456`） |
| **技术栈** | Node.js / Bun，TypeScript |
| **安装方式** | `npm install -g @musistudio/claude-code-router` |

### 6.2 核心原理：为什么需要 CCR？

```
┌─────────────────────────────────────────────────────────────────────┐
│                         问题背景                                     │
│                                                                     │
│   Claude Code 原生只认 Anthropic Messages API 格式：                  │
│   ├── 认证: x-api-key + anthropic-version                           │
│   ├── 端点: POST /v1/messages                                       │
│   ├── 系统: 顶层 system 参数                                         │
│   ├── 工具: input_schema 格式                                        │
│   └── 流式: SSE with event names                                     │
│                                                                     │
│   但市场上 ~80% 的模型提供商使用 OpenAI Chat Completions 格式：        │
│   ├── 认证: Authorization: Bearer                                    │
│   ├── 端点: POST /v1/chat/completions                                │
│   ├── 系统: messages 中 role=system                                  │
│   ├── 工具: parameters 格式                                          │
│   └── 流式: SSE plain data lines                                     │
│                                                                     │
│   → 需要一个中间层做**双向协议转换**                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.3 架构设计：四阶段数据流管道

CCR 的核心是一个 **Transformer（转换器）管道**，数据流经四个阶段：

```
┌──────────────┐     ┌───────────────────────┐     ┌──────────────────┐
│  Claude Code  │     │                       │     │   目标 Provider    │
│  (客户端)      │────▶│  Claude Code Router    │────▶│  (OpenAI/DeepSeek/ │
│              │     │                       │     │   Qwen/Kimi...)    │
└──────────────┘     └───────────────────────┘     └──────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌──────────┐   ┌──────────┐   ┌──────────────┐
     │ 路由决策   │   │ 协议转换  │   │ 响应逆向转换  │
     │ Router   │   │Transform │   │ Transform    │
     └──────────┘   └──────────┘   └──────────────┘
```

#### 四阶段转换流水线详解

```
阶段 1: transformRequestOut（入站解析）
┌─────────────────────┐          ┌────────────────────┐
│ Anthropic Messages   │  解析为   │ UnifiedChatRequest │
│ API 原始请求         │ ──────▶  │ (统一内部格式)       │
│                     │          │                    │
│ {                   │          │ {                  │
│   model,            │          │   model,           │
│   max_tokens,       │          │   messages[],      │
│   system: "...",    │  ───▶    │   max_tokens,      │
│   messages:[...],   │          │   tools[],         │
│   tools:[...],      │          │   reasoning:{},    │
│   stream:true       │          │   stream           │
│ }                   │          │ }                  │
└─────────────────────┘          └────────────────────┘


阶段 2: transformRequestIn（出站适配）
┌────────────────────┐          ┌────────────────────┐
│ UnifiedChatRequest │  转换为   │ Provider 特定格式    │
│ (统一内部格式)       │ ──────▶  │                    │
│                    │          │ OpenAI 格式示例:     │
│ {                  │          │ {                   │
│   model,           │          │   model,            │
│   messages:[...],   │  ───▶    │   messages:[...],   │
│   tools:[...],      │          │   tools:[...],      │
│   reasoning:{}      │          │   max_tokens,       │
│ }                  │          │   temperature,      │
│                    │          │   stream            │
│                    │          │ }                   │
└────────────────────┘          └────────────────────┘
        │                              │
        │    此阶段处理的关键差异:
        │    ├── system 提示: 顶层参数 → messages 中 role=system
        │    ├── 工具定义: input_schema → parameters
        │    ├── stop_sequences → stop
        │    ├── thinking.budget_tokens → reasoning_effort / enable_thinking
        │    └── content blocks: [{type:"text"}] → string
        │
        ▼
┌────────────────────┐
│  Provider API 调用  │
│  (实际 HTTP 请求)   │
└────────────────────┘
        │
        ▼


阶段 3: transformResponseIn（入站归一化）
┌────────────────────┐          ┌────────────────────┐
│ Provider 原始响应    │  归一化为  │ 统一响应格式          │
│                    │ ──────▶  │                    │
│ OpenAI 示例:        │          │ {                  │
│ {                  │          │   id,               │
│   choices:[{        │  ───▶    │   model,            │
│     message:{       │          │   content,          │
│       role,         │          │   finish_reason,    │
│       content,      │          │   usage:{},         │
│       tool_calls    │          │   tool_calls:[],    │
│     }               │          │   thinking:{}       │
│   }],               │          │ }                  │
│   usage:{}          │          │                    │
│ }                  │          └────────────────────┘
└────────────────────┘


阶段 4: transformResponseOut（出站还原）
┌────────────────────┐          ┌─────────────────────┐
│ 统一响应格式         │  还原为   │ Anthropic Messages   │
│                    │ ──────▶  │ API 响应格式          │
│ {                  │          │                      │
│   content,          │          │ {                    │
│   tool_calls:[],    │  ───▶    │   id: "msg_...",      │
│   finish_reason,    │          │   type: "message",    │
│   usage:{},         │          │   content:[{type:"text"}],
│   thinking:{}       │          │   stop_reason,        │
│ }                  │          │   usage:{}            │
│                    │          │ }                    │
└────────────────────┘          └─────────────────────┘
        │
        │    此阶段处理的关键差异:
        │    ├── finish_reason: "stop" → "end_turn"
        │    ├── usage: prompt_tokens → input_tokens
        │    ├── usage: completion_tokens → output_tokens
        │    ├── tool_calls → content 中 tool_use block
        │    ├── reasoning_content → thinking content block
        │    └── 流式: data: lines → event: + data: SSE
        │
        ▼
┌─────────────────────┐
│ 返回给 Claude Code   │
└─────────────────────┘
```

### 6.4 Transformer 接口定义（TypeScript）

CCR 的转换器遵循统一的接口规范：

```typescript
/**
 * CCR Transformer 接口 — 所有协议转换器的契约
 * 来源: https://musistudio.github.io/claude-code-router/zh-CN/docs/server/config/transformers/
 */
interface Transformer {
  // === 请求转换 ===

  /** 将统一请求转换为 Provider 特定格式（出站） */
  transformRequestIn?: (
    request: UnifiedChatRequest,
    provider: LLMProvider,
    context: TransformerContext
  ) => Promise<Record<string, any>>;

  /** 将 Provider 原始请求解析为统一格式（入站） */
  transformRequestOut?: (
    request: any,
    context: TransformerContext
  ) => Promise<UnifiedChatRequest>;

  // === 响应转换 ===

  /** 将 Provider 响应转换为统一格式（入站归一化） */
  transformResponseIn?: (
    response: Response,
    context?: TransformerContext
  ) => Promise<Response>;

  /** 将统一响应还原为 Anthropic Messages 格式（出站） */
  transformResponseOut?: (
    response: Response,
    context: TransformerContext
  ) => Promise<Response>;

  // === 扩展能力 ===

  /** 自定义端点路径（覆盖默认的 /chat/completions 或 /messages） */
  endPoint?: string;

  /** 转换器名称（用于配置引用和日志） */
  name?: string;

  /** 自定义认证处理器（替代默认的 Bearer/x-api-key 方案） */
  auth?: (
    request: any,
    provider: LLMProvider,
    context: TransformerContext
  ) => Promise<any>;

  /** 日志实例（由框架自动注入） */
  logger?: any;
}
```

#### 核心数据模型

```typescript
/** 统一请求模型 — CCR 内部的中间表示 */
interface UnifiedChatRequest {
  messages: UnifiedMessage[];
  model: string;
  max_tokens?: number;
  temperature?: number;
  stream?: boolean;
  tools?: UnifiedTool[];
  tool_choice?: any;
  reasoning?: {
    effort?: ThinkLevel;       // "none" | "low" | "medium" | "high"
    max_tokens?: number;
    enabled?: boolean;
  };
}

/** 统一消息模型 */
interface UnifiedMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string | null | MessageContent[];

  // 工具调用相关（OpenAI 格式）
  tool_calls?: Array<{
    id: string;
    type: "function";
    function: { name: string; arguments: string };
  }>;
  tool_call_id?: string;

  // 思考内容（推理模式）
  thinking?: {
    content: string;
    signature?: string;        // 某些模型的思考签名
  };
}
```

### 6.5 内置转换器清单与职责

| 转换器名称 | 适用目标 | 核心职责 | 关键转换逻辑 |
|-----------|----------|---------|-------------|
| **anthropic** | 通用 Anthropic↔OpenAI 双向转换 | 格式桥接 | system↔messages、input_schema↔parameters、tool_use↔tool_calls、SSE event↔plain data |
| **deepseek** | DeepSeek API | DeepSeek 专属适配 | `reasoning_content` 字段处理、思考预算映射、model 切换（chat/reasoner） |
| **gemini** | Google Gemini API | Gemini 专属适配 | `generateContent` 格式转换、`contents`→`messages` 映射、Vertex Auth 处理 |
| **openrouter** | OpenRouter API | OpenRouter 专属适配 | Provider 路由参数透传、`:online` 后缀处理、HTTP Header 注入 |
| **groq** | Groq API | Groq 高速推理适配 | 低延迟优化参数、速率限制处理 |
| **maxtoken** | 通用 | Token 上限控制 | 强制设置/覆写 `max_tokens` 值 |
| **tooluse** | 工具调用优化 | Tool Choice 优化 | 自动调整 `tool_choice` 为 `"auto"` / `"required"` |
| **enhancetool** | 工具容错增强 | 工具调用错误容忍 | 对 LLM 返回的不规范 tool call 参数做修正（代价：失去流式） |
| **reasoning** | 推理内容处理 | Thinking ↔ Reasoning 转换 | `reasoning_content` → `thinking` block、`enable_thinking` / `thinking.budget_tokens` 映射 |
| **sampling** | 采样参数处理 | 采样字段标准化 | temperature/top_p/top_k/repetition_penalty 跨厂商范围归一化 |
| **cleancache** | 缓存清理 | 移除缓存控制字段 | 清除 `cache_control` 相关字段（某些 Provider 不支持） |
| **vertex-gemini** | Vertex AI Gemini | Google Cloud 认证 | OAuth2 / Service Account 认证处理 |
| **customparams** | 通用参数注入 | 自定义参数注入 | 向请求中添加任意自定义 header/body 字段 |

### 6.6 配置体系：Provider + Router + Transformer 三位一体

```jsonc
// ~/.claude-code-router/config.json — 完整配置示例
{
  // === 全局设置 ===
  "APIKEY": "your-secret-key",           // Router 自身认证密钥
  "PROXY_URL": "http://127.0.0.1:7890", // 出站代理
  "LOG": true,                           // 启用日志
  "API_TIMEOUT_MS": 600000,              // 10 分钟超时（Claude Code 任务可能很长）
  "HOST": "127.0.0.1",                  // 监听地址

  // === Provider 定义（支持多厂商并行）===
  "Providers": [
    {
      "name": "openrouter",
      "api_base_url": "https://openrouter.ai/api/v1/chat/completions",
      "api_key": "sk-or-xxx",
      "models": [
        "google/gemini-2.5-pro-preview",
        "anthropic/claude-sonnet-4",
        "anthropic/claude-3.7-sonnet:thinking"
      ],
      "transformer": {
        "use": ["openrouter"]   // ← 使用 openrouter 转换器
      }
    },
    {
      "name": "deepseek",
      "api_base_url": "https://api.deepseek.com/chat/completions",
      "api_key": "sk-xxx",
      "models": ["deepseek-chat", "deepseek-reasoner"],
      "transformer": {
        "use": ["deepseek"],                          // 全局: deepseek 转换器
        "deepseek-chat": { "use": ["tooluse"] }       // 仅 deepseek-chat: 额外加 tooluse
      }
    },
    {
      "name": "gemini",
      "api_base_url": "https://generativelanguage.googleapis.com/v1beta/models/",
      "api_key": "AIza...",
      "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
      "transformer": { "use": ["gemini"] }
    },
    {
      "name": "ollama",
      "api_base_url": "http://localhost:11434/v1/chat/completions",
      "api_key": "ollama",
      "models": ["qwen2.5-coder:latest"]
      // 无需 transformer — Ollama 原生兼容 OpenAI 格式
    },
    {
      "name": "dashscope",
      "api_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
      "api_key": "sk-xxx",
      "models": ["qwen3-coder-plus"],
      "transformer": {
        "use": [
          ["maxtoken", { "max_tokens": 65536 }],  // 带 options 的转换器
          "enhancetool"
        ]
      }
    },
    {
      "name": "anthropic-direct",
      "api_base_url": "https://api.anthropic.com/v1/messages",
      "api_key": "sk-ant-xxx",
      "models": ["claude-sonnet-4-20250514"],
      "transformer": { "use": ["anthropic"] }  // 直连 Anthropic，保留原生格式
    }
  ],

  // === 路由规则（按场景自动选择模型）===
  "Router": {
    "default": "deepseek,deepseek-chat",           // 默认模型
    "background": "ollama,qwen2.5-coder:latest",   // 后台任务用本地小模型
    "think": "deepseek,deepseek-reasoner",         // Plan Mode 等推理场景
    "longContext": "openrouter,google/gemini-2.5-pro-preview", // 长上下文 (>60K tokens)
    "longContextThreshold": 60000,                 // 长上下文阈值
    "webSearch": "gemini,gemini-2.5-flash",        // 网络搜索任务
    "image": "openrouter,anthropic/claude-sonnet-4" // 图像理解 (beta)
  },

  // === 全局转换器（作用于所有 Provider）===
  "transformers": [
    {
      "name": "my-custom-transformer",
      "path": "$HOME/.claude-code-router/plugins/my-transformer.js",
      "options": { "debug": true }
    }
  ],

  // === 自定义路由脚本（高级用法）===
  "CUSTOM_ROUTER_PATH": "$HOME/.claude-code-router/custom-router.js"
}
```

### 6.7 路由机制详解

#### 6.7.1 内置场景路由

CCR 根据 Claude Code 发出的请求特征自动判断场景并路由到对应模型：

| 路由键 | 触发条件 | 典型用途 | 推荐模型类型 |
|--------|---------|----------|-------------|
| `default` | 所有未匹配的请求 | 日常编码对话 | 性价比高的通用模型 |
| `background` | 子 Agent / 后台任务 | 代码生成、简单查询 | 本地小模型或便宜模型 |
| `think` | Plan Mode / 推理密集 | 架构设计、复杂分析 | 推理专用模型（R1、o-series） |
| `longContext` | 输入 token > threshold | 大文件分析、长文档 | 长上下文模型（Gemini Pro、Qwen Long） |
| `webSearch` | 触发了网络搜索工具 | 实时信息检索 | 内置搜索能力的模型 |
| `image` | 请求包含图像 | UI 审查、截图分析 | 多模态视觉模型 |

#### 6.7.2 动态模型切换（运行时）

在 Claude Code 会话中通过 `/model` 命令实时切换：

```
# 切换到 OpenRouter 上的 Claude Sonnet 4
/model openrouter,anthropic/claude-sonnet-4

# 切换到 DeepSeek 推理模型
/model deepseek,deepseek-reasoner

# 切换到本地 Ollama
/model ollama,qwen2.5-coder:latest
```

#### 6.7.3 子 Agent 路由

在子 Agent 的 prompt 开头嵌入特殊标记来指定路由目标：

```
<CCR-SUBAGENT-MODEL>openrouter,anthropic/claude-sonnet-4</CCR-SUBAGENT-MODEL>
请帮我分析这段代码的性能瓶颈...
```

#### 6.7.4 自定义路由脚本

```javascript
// ~/.claude-code-router/custom-router.js
module.exports = async function router(req, config) {
  const userMessage = req.body.messages.find(m => m.role === "user")?.content;

  // 基于关键词路由
  if (userMessage?.includes("解释代码")) {
    return "openrouter,anthropic/claude-sonnet-4";  // 用强模型解释代码
  }

  if (userMessage?.includes("写单元测试")) {
    return "deepseek,deepseek-chat";  // 用性价比模型写测试
  }

  return null;  // null = 回退到默认路由规则
};
```

### 6.8 协议转换关键差异对照表（CCR 实际处理）

以下表格展示 CCR 在实际运行中需要处理的 **Anthropic ↔ OpenAI 格式映射**，这是本报告第二章对比的具体工程落地：

#### 请求方向：Anthropic → OpenAI（出站）

| Anthropic Messages API 字段 | 转换动作 | OpenAI Chat Completions 字段 |
|---------------------------|---------|----------------------------|
| 顶层 `"system"` | 移入 messages 数组 | `{role: "system", content: "..."}` |
| `messages[]` 中只有 user/assistant | 直接映射（过滤掉非标准角色） | `messages[]` |
| `tools[].input_schema` | 重命名字段 | `tools[].function.parameters` |
| `stop_sequences` | 重命名 | `stop` |
| `max_tokens`（必填） | 直接传递 | `max_tokens` / `max_completion_tokens` |
| `thinking.type: "enabled"` + `budget_tokens` | 转换为枚举或布尔 | `reasoning_effort` / `enable_thinking` |
| `top_k` | 丢弃（OpenAI 不支持） | N/A |
| `stream: true` | 直接传递 | `stream: true` |
| `content: [{type: "text", text: "..."}]` | 展平为字符串 | `content: "..."` |

#### 响应方向：OpenAI → Anthropic（入站）

| OpenAI 响应字段 | 转换动作 | Anthropic 响应字段 |
|---------------|---------|------------------|
| `choices[0].message.content` (string) | 包装为数组 | `content: [{type: "text", text: "..."}]` |
| `choices[0].message.tool_calls` | 转换为 content block | `content: [{type: "tool_use", id, name, input}]` |
| `choices[0].finish_reason: "stop"` | 映射 | `stop_reason: "end_turn"` |
| `choices[0].finish_reason: "length"` | 映射 | `stop_reason: "max_tokens"` |
| `choices[0].finish_reason: "tool_calls"` | 映射 | `stop_reason: "tool_use"` |
| `usage.prompt_tokens` | 重命名 | `usage.input_tokens` |
| `usage.completion_tokens` | 重命名 | `usage.output_tokens` |
| `choices[0].message.reasoning_content` | 转换为 thinking block | `content: [{type: "thinking", thinking: "..."}]` |
| `id: "chatcmpl-..."` | 重新生成 | `id: "msg_..."` |
| `object: "chat.completion"` | 替换 | `type: "message"` |

#### 流式响应转换差异

| 维度 | OpenAI SSE 格式 | Anthropic SSE 格式 | CCR 转换动作 |
|------|----------------|-------------------|------------|
| 事件名 | 无（纯 `data:` 行） | 有 (`event: message_start` 等) | 添加事件名包装 |
| 数据包裹 | `data: {...}` | `data: {...}` (相同) | 透传 |
| Delta 结构 | `{delta: {role, content}}` | `{delta: {type, text}}` (在 content_block_delta 中) | 字段重映射 |
| 结束标记 | `data: [DONE]` | `event: message_stop` | 格式替换 |
| Usage 时机 | 最后 chunk / `stream_options.include_usage` | `message_start` + `message_delta` | 合并/拆分位置调整 |
| 思考内容 | `reasoning_content` in delta | `content_block_start(type: "thinking")` + delta | 类型转换 |

### 6.9 与本报告第四章「统一抽象层」设计的对应关系

CCR 的实现与本报告第四章提出的统一抽象层设计高度吻合，可作为参考实现：

| 设计概念 | 报告第四章（理论设计） | CCR（工程实现） |
|---------|--------------------|----------------|
| **统一请求模型** | `UnifiedChatRequest` interface | `UnifiedChatRequest` interface (完全一致) |
| **统一消息模型** | `UnifiedMessage` interface | `UnifiedMessage` interface (含 tool_calls/thinking) |
| **连接适配** | Connection Adapter | `auth()` 方法 + Header 注入 |
| **消息适配** | Message Adapter | `transformRequestOut/In` 中的消息格式转换 |
| **参数适配** | Parameter Adapter | 各内置转换器的参数映射逻辑 |
| **工具适配** | Tool Adapter | anthropic 转换器的 `input_schema ↔ parameters` 转换 |
| **流式适配** | Streaming Adapter | `transformResponseOut` 中的 ReadableStream 管道 |
| **思维适配** | Thinking Adapter | `reasoning` 转换器的 `reasoning_content ↔ thinking` 转换 |
| **插件扩展** | L3 扩展层 | 自定义 Transformer + Plugin System |
| **路由策略** | （未详细展开） | Router (default/background/think/longContext/webSearch) |

### 6.10 对 Harness Creator 项目的启示

基于对 CCR 的深入分析，对 harness-creator 项目的 Harness/Skill 设计有以下具体建议：

1. **采用 Transformer 管道模式**：CCR 的四阶段转换管道是经过验证的模式，可直接作为 Harness 中「多 Provider 适配 Skill」的架构蓝本
2. **UnifiedChatRequest 作为中间表示**：以统一的内部格式为中轴，各 Provider 的转换器只需关注「统一格式 ↔ 自身格式」的双向映射
3. **内置转换器 + 自定义转换器的组合策略**：常见 Provider 用内置转换器覆盖，特殊需求通过插件机制扩展
4. **场景化路由**：CCR 的 default/background/think/longContext 路由思路可泛化为 Harness 的「任务类型 → 模型选择」策略
5. **流式转换是最大难点**：CCR 的流式响应转换代码量远超非流式，设计 Harness 时应优先确保非流式路径正确，再迭代流式支持
6. **容错降级原则**：CCR 的 `enhancetool` 转换器展示了「宁可损失流式也不能让工具调用失败」的实用主义——Harness 的适配层也应遵循类似原则

### 6.11 参考资料（Claude Code Router 专项）

- [Claude Code Router GitHub 主仓库](https://github.com/musistudio/claude-code-router)
- [Claude Code Router 增强版 Fork (ccr-next)](https://github.com/Darthwares/ccr-next)
- [CCR 转换器官方文档](https://musistudio.github.io/claude-code-router/zh-CN/docs/server/config/transformers/)
- [CCR 项目动机与工作原理](https://github.com/musistudio/claude-code-router/blob/main/docs/motivation.md)
- [vLLM — Claude Code 原生集成文档](https://docs.vllm.ai/en/stable/serving/integrations/claude_code/)（另一种无需转换的方案）
- [LiteLLM 作为 Claude Code 代理的替代方案](https://gameapp.club/post/2025-07-20-claude-code-with-litellm/)
- [DeepSeek Anthropic API 兼容接口文档](https://api-docs.deepseek.com/guides/anthropic_api)

---

## 七、参考资料

- [OpenAI Chat Completions API Reference](https://platform.openai.com/docs/api-reference/chat/create)
- [OpenAI Responses API Migration Guide](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Anthropic Messages API Reference](https://docs.anthropic.com/en/api/messages)
- [DeepSeek API Docs](https://platform.deepseek.com/api-docs)
- [DeepSeek API Guides - Thinking Mode](https://platform.deepseek.com/api-docs/guides/thinking_mode)
- [阿里云百炼 - 千问 API 参考](https://help.aliyun.com/zh/model-studio/qwen-api-reference/)
- [阿里云百炼 - 首次调用千问 API](https://help.aliyun.com/zh/model-studio/getting-started/first-api-call-to-qwen)
- [Kimi/Moonshot API - Chat 接口说明](https://platform.moonshot.cn/docs/api/chat)
- [OpenAI Model Spec](https://model-spec.openai.com/)
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)

---

*报告生成时间：2026-04-22 | 基于各家官方 API 文档及 Claude Code Router 开源实现的最新版本*
