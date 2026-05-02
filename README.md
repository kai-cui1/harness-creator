# Harness Creator

> 将**工程方法论**转化为 **Agent 可用工具**的方法论整合与抽象平台。

## 一句话

Harness Creator 的输入是工程规范和产出物（PRD、原型等），核心是对软件工程各环节**方法论的高度整合与抽象**，输出是面向不同 Agent（编程 / UX / 测试等）的、可持续迭代的落地工具（Skills、Plugins 等）。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Harness** | 对某个工程环节方法论的完整封装，含规范、规则、工作流和质量标准 |
| **Skill** | Harness 中的可复用能力单元，Agent 直接消费的最小粒度交付物 |
| **方法论抽象** | 从工程规范中提炼的结构化知识表示，是 Harness 的输入源 |

## 项目结构

```
harness-creator/
├── .claude/skills/              # Claude Code Skills
│   ├── lesson-learned/          # 经验提取 Skill（逐条确认写入）
│   ├── write-prd/               # PRD 编写 Skill（逐节确认流程）
│   └── find-skills/             # 技能发现工具
├── src/harness_creator/         # MDL 引擎实现
├── harnesses/                   # 已产出的 Harness 实例
├── docs/                        # 调研文档 & 设计规格
│   ├── superpowers/specs/       # 设计文档
│   ├── superpowers/plans/       # 实现计划
│   └── ...                      # 各领域调研报告
├── tests/                       # MDL 引擎测试（30/30 通过）
├── CLAUDE.md                    # 项目指令（AI 协作规范）
└── README.md                    # 本文件
```

## 已有 Skills

### lesson-learned — 经验提取

从日常使用中提取经验教训，**逐条确认后写入存储**，绝不自动修改文件。

- 6 类经验模板：Bug / Pattern / Tool / AI-Collab / Tech-Gotcha / User-Preference
- 5 步管道：扫描 → 分类 → 去重 → **逐条确认** → 写入+索引
- 触发方式：会话结束自动触发 / 手动 `/lesson-learned`

### write-prd — PRD 编写

结构化产品需求文档编写，**先骨架后血肉**，每节写作前后均需用户确认。

- 6 章完整流程：概述 → 业务流程 → 功能清单 → 详细设计 → 跨功能规则 → 验收标准
- 含 Mermaid 流程图节点约定、编号体系、检查清单

## 已完成的研究

| 领域 | 成果 |
|------|------|
| LLM API 层 | 5 家主流厂商 API 格式对比 + 统一适配器架构 |
| Agent 框架层 | 12 个平台调研 + MetaGPT vs OpenHands 深度拆解 + Superpowers 分析 |
| Model Integration 层 | MIL 完整分析（6 大子系统 + MVP 路线） |
| 方法论抽象层 | MDL v0.1 + 行业设计标准拆解 + SDLC 10 阶段确认 |
| 已实现代码 | Phase 1 MDL 引擎（数据模型 / 解析器 / 渲染器 / 校验器，30/30 测试通过） |

## 技术栈

- **Skill 系统**: Claude Code Skills (Markdown)
- **MDL 引擎**: Python 3
- **文档**: Markdown + Mermaid

## Roadmap

详见 [docs/roadmap.md](docs/roadmap.md)

## License

Private
