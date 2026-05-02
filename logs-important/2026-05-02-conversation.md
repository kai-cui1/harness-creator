# 2026-05-02 重要对话记录

## 主题概要

1. **write-prd skill 增强** — 增加逐节确认约束（写前确认思路 + 写后确认完成）
2. **lesson-learned skill 从零设计并实现** — 完整的 brainstorm → design → plan → implement → commit → push 流程
3. **项目 Git 仓库初始化** — 首次提交 + push 到 GitHub
4. **README.md 创建**

---

## 对话 1：write-prd skill 增加逐节确认约束

### 用户需求
> 我希望在 write-prd 的 skill 里增加一个约束，让 AI 每写一节之前和我确认写作思路，每完成一章节后和我确认后再继续下一章节

### 执行内容
在 `.claude/skills/write-prd/SKILL.md` 中新增了 **「交互约束：逐节确认（强制）」** 章节，包含：
- 确认流程图（写前确认 → 编写 → 写后确认）
- 5 条规则：每章必确认、写前输出写作思路、写后展示完成摘要、用户可随时调整、不堆积多章
- 写前/写后确认的标准模板格式

---

## 对话 2：lesson-learned skill 全流程

### 用户触发
> 请帮我找这样一种技能，能够帮助 agent 从日常使用中总结经验和 lesson learn，但是不会直接修改我本地的任何文件、技能。而是总结之后，和我确认、得到我允许的情况下去修改

### 调研结果

搜索了 skills.sh 生态，找到 4 个相关技能：

| 技能 | 安装量 | 是否符合要求 |
|------|--------|:---:|
| softaworks/agent-toolkit@lesson-learned | 2.6K | 部分符合（只分析展示，不自动写文件） |
| win4r/memory-lancedb-pro@lesson | 310 | 不符合（会直接更新文件） |
| pedronauck/skills@lesson-learned | 78 | 同上 |
| johnlindquist/claude@lessons | 31 | 不符合（直接 cat >> 写文件） |

### 用户决策：从零自建

### Brainstorming 阶段收集的需求

**触发方式**（多选）：会话结束时自动触发 + 用户手动触发

**经验类型**（全选 + 补充）：
1. Bug/问题类
2. 模式/最佳实践
3. 工具/工作流
4. AI 协作经验
5. **技术陷阱类**（用户新增，举例：Mermaid 中文引号导致渲染失败）
6. **主人偏好类**（用户新增，记录使用者习惯和偏好）

**存储方案**：MVP 先做简单方案（项目 lessons/ + 全局索引），身份隔离等后续迭代写入 roadmap

**确认粒度**：逐条确认（每条经验独立 AskUserQuestion）

### 设计方案：B+C 融合版

- 用 B（指令+模板）的简洁文件结构
- 承载 C（完整管道）的 5 步处理流程
- 6 类模板 + LESSONS.md 索引

### 设计文档
保存至：`docs/superpowers/specs/2026-05-02-lesson-learned-skill-design.md`

### 实现计划
保存至：`docs/superpowers/plans/2026-05-02-lesson-learned-skill.md`
8 个 Task：SKILL.md + 6 个模板 + LESSONS.md 初始化 + 集成验证

### 执行方式：Subagent-Driven Development

并行分发 Tasks 2-7（6 个独立模板文件），全部成功。

### 最终产出文件

```
.claude/skills/lesson-learned/
├── SKILL.md                    # 268 行，5 步管道 + 核心约束 + Red Flags
├── templates/
│   ├── bug.md                  # Bug/问题类（Symptom/Cause/Fix/Prevention/Cost）
│   ├── pattern.md              # 模式/最佳实践（Scenario/Decision/Rationale/Apply）
│   ├── tool.md                 # 工具/工作流（Tool/Feature/Commands/Gotchas）
│   ├── ai-collab.md            # AI 协作（Situation/Wrong/Better/PromptTip）
│   ├── tech-gotcha.md          # 技术陷阱（Tech/Trap/Reason/SafePattern）
│   └── user-preference.md      # 主人偏好（Domain/Pref/Reason/Trigger）

.claude/lessons/
└── LESSONS.md                  # 索引文件（表格形式）
```

---

## 对话 3：Git 仓库初始化与首次提交

### 背景
项目之前没有 git 仓库。用户已创建 GitHub 仓库：https://github.com/kai-cui1/harness-creator

### 执行过程
1. `git init` + `git remote add origin`
2. 创建 `.gitignore`（忽略 .DS_Store, .codex/, .cursor/, node_modules/, __pycache__/, .env*）
3. **Commit 1** (`cd9046d`): feat: lesson-learned skill (11 files, 2469 行)
4. **Commit 2** (`8f80bb3`): init: project base (2862 files, 含全部项目文件)
5. Push 到 origin/main

### 关于 gitignore 的讨论
- IDE/工具配置（.DS_Store, .codex/, .cursor/）→ 忽略 ✅
- 通用开发缓存（node_modules, __pycache__, .env）→ 忽略 ✅
- logs-important/ → **保留入库**（用户选择不忽略）

---

## 对话 4：README.md

创建项目 README，涵盖：
- 项目定位（一句话 + 核心概念表）
- 目录结构说明
- 已有 Skills 介绍（lesson-learned + write-prd）
- 已完成研究成果汇总表
- 技术栈和 Roadmap 链接

Commit: `97b5169` 并 push

---

## 最终 Git 状态

```
97b5169 docs: add README.md with project overview, skills, and research summary
8f80bb3 init: add project base with docs, skills, harnesses, and MDL engine
cd9046d feat: add lesson-learned skill with 6-type templates and per-item confirmation
```

远程仓库：https://github.com/kai-cui1/harness-creator

---

## 关键决策记录

| 决策 | 选择 | 原因 |
|------|------|------|
| lesson-learned 来源 | 从零自建 | 现有 skill 要么会自动写文件，要么功能不匹配 |
| 设计方案 | B+C 融合 | 要 B 的简洁文件结构 + C 的 5 步管道流程 |
| 存储方案 | MVP 简单方案 | 项目 lessons/ + 全局索引，身份隔离后续迭代 |
| 确认粒度 | 逐条确认 | 最精细的控制，用户明确要求 |
| 执行方式 | Subagent-Driven | 6 个模板可并行，review checkpoint 保证质量 |
| logs-important | 保留入库 | 用户选择不入 gitignore |
