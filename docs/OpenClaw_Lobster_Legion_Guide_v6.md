# 🦞 OpenClaw 养虾宝典 v6.0
## OPT 龙虾军团 · 超级智能体基础设施构建指南

> **版本**: v6.0 · **日期**: 2026-04-16 · **架构来源**: Claude Code + Hermes Agent + OpenHarness

---

## 序言：三大顶尖系统的融合哲学

本宝典是对三个全球最顶尖开源 Agent 系统的深度学习与融合实践：

| 系统 | 核心贡献 | 关键机制 |
|---|---|---|
| **Claude Code** (Anthropic, 51万行) | 工业级 Agent 架构范本 | TAOR 引擎、Fail-closed 安全、Context Engineering |
| **Hermes Agent** (Nous Research, 17K Stars) | 自我进化型 Agent | 技能自进化、辩证式用户建模、RL 数据飞轮 |
| **OpenHarness** (HKUDS, v0.1.0) | Agent 基础设施范式 | Hooks 机制、Plan/Auto Mode、MCP 生态 |

这三个系统共同揭示了一个核心洞察：

> **"The model is the agent. The code is the harness."**
> 模型即智能体，代码即 Harness。LLM 提供推理能力，Harness 提供手、眼、记忆和安全边界。

---

## 第一章：系统架构总览

### 1.1 OPT v6.0 架构图

```
┌─────────────────────────────────────────────────────────┐
│                    用户 (You)                            │
└─────────────────────────┬───────────────────────────────┘
                          │ 唯一对话入口
┌─────────────────────────▼───────────────────────────────┐
│              CoS 幕僚长 (意图对齐层)                      │
│  • QAPS 任务拆解  • 辩证式用户建模  • Closeout 流程       │
└──────┬──────────┬──────────┬──────────┬─────────────────┘
       │          │          │          │
┌──────▼──┐ ┌────▼────┐ ┌───▼───┐ ┌───▼──────┐
│ CTO     │ │ FE      │ │ BE    │ │Researcher│
│技术合伙人│ │前端工程师│ │后端工程│ │市场研究员 │
│Plan Mode│ │TAOR引擎 │ │TAOR引擎│ │多源验证  │
└──────┬──┘ └────┬────┘ └───┬───┘ └───┬──────┘
       │         │           │         │
┌──────▼─────────▼───────────▼─────────▼──────────────────┐
│              QA / KO / Ops (系统维护层)                   │
│  QA: 质量守门  KO: 知识进化  Ops: 运维安全                │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Harness 基础设施层                       │
│  Hooks系统  •  记忆系统  •  技能库  •  MCP服务器          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 三层协同机制

**意图对齐层**（CoS）：唯一对话窗口，负责将用户的模糊需求转化为结构化的 QAPS 任务，并在会话结束时执行 Closeout 流程，确保记忆不丢失。

**执行层**（CTO + FE + BE + Researcher）：各司其职，严格遵守 SOUL.md 定义的工具权限边界。FE 和 BE 运行 TAOR 引擎，遇到错误自动重试，而不是直接报错。

**系统维护层**（QA + KO + Ops）：QA 是质量守门员，KO 是大脑进化中枢，Ops 是免疫系统。这三个角色共同确保系统在自主运行时不会越界、不会退化、不会崩溃。

---

## 第二章：核心机制详解

### 2.1 TAOR 引擎（来自 Claude Code）

TAOR（Think-Act-Observe-Repeat）是整个系统的执行引擎，确保 Agent 在遇到错误时不会直接放弃，而是自动分析并重试：

```
Think（思考）：分析任务，检查环境状态
    ↓
Act（执行）：执行具体命令或操作
    ↓
Observe（观察）：捕获完整输出（包括 stderr）
    ↓
成功？→ 结束
失败？→ 分析错误原因 → Repeat（最多 3 次）
    ↓（3次后仍失败）
Escalation → 通知上级 Agent
```

**关键实现**：`engine/taor_loop.sh` 是 TAOR 引擎的 Bash 实现，支持指数退避重试和自动 Escalation 报告生成。

### 2.2 四层记忆系统（来自 Claude Code + Hermes Agent）

| 层级 | 名称 | 存储位置 | 保留时间 | 用途 |
|---|---|---|---|---|
| **L0** | 会话记忆 | `memory/session/` | 30 天 | 当前对话上下文 |
| **L1** | 工作区记忆 | `memory/workspace/` | 项目生命周期 | 任务、结果、Escalation |
| **L2** | 全局记忆 | `memory/global/` | 永久 | 设计原则、ADR、技术债 |
| **L3** | RL 轨迹 | `memory/trajectories/` | 永久 | 未来模型微调的训练数据 |

**Auto Dream 机制**（来自 Claude Code）：每周一凌晨 2:00，`engine/auto_dream.py` 自动执行，将 L0 中的高价值轨迹提炼到 L2，并生成新的技能文件。

### 2.3 Hooks 机制（来自 OpenHarness）

Hooks 是整个系统的安全边界，分为两类：

**PreToolUse**（执行前拦截）：
- `permission_check.py`：验证操作权限，拦截黑名单命令
- `path_guard.py`：确保文件操作不超出允许路径
- `command_blocklist.py`：拦截危险命令

**PostToolUse**（执行后处理）：
- `result_sanitizer.py`：清洗输出中的 API Keys 和密码
- `audit_logger.py`：将所有操作记录到审计日志

**Fail-closed 原则**（来自 Claude Code）：当 Hooks 无法判断操作是否安全时，默认拒绝，并要求 CoS 提供明确授权。

### 2.4 技能自进化（来自 Hermes Agent）

技能自进化是 OPT v6.0 最重要的长期价值机制：

```
Agent 解决复杂问题（TAOR 2+ 次重试后成功）
    ↓
提炼成功路径为 SKILL.md（存入 skills/evolved/）
    ↓
KO 在 Auto Dream 中索引并评分
    ↓
其他 Agent 在遇到类似问题时，RAG 检索到该技能
    ↓
技能被使用 → 记录使用结果 → KO 更新技能版本
    ↓（正反馈循环）
系统越用越强
```

### 2.5 辩证式用户建模（来自 Hermes Agent）

传统的用户画像是累积式的（不断追加），容易产生矛盾和冗余。OPT v6.0 使用辩证式建模：

**正题**（旧画像）+ **反题**（新观察）= **合题**（新画像）

例如：
- 正题："用户偏好 Python，喜欢快速原型"
- 反题："最近在研究 Rust 的内存安全机制"
- 合题："有 Python 背景的系统程序员，正在向 Rust 转型，关注性能与内存安全，同时保持快速迭代的工作风格"

---

## 第三章：8 个 Agent 角色体系

### 3.1 角色总览

| 角色 | 层级 | 核心职责 | 推荐模型 |
|---|---|---|---|
| **CoS** 幕僚长 | 意图对齐 | 唯一对话窗口，任务拆解，结果验收 | claude-3-7-sonnet |
| **CTO** 技术合伙人 | 执行 | 架构设计，技术选型，代码审查 | claude-3-7-sonnet |
| **FE** 前端工程师 | 执行 | UI 组件，交互逻辑，性能优化 | claude-3-5-haiku |
| **BE** 后端工程师 | 执行 | API 设计，数据库，业务逻辑 | claude-3-5-haiku |
| **Researcher** 研究员 | 执行 | 竞品分析，API 调研，市场情报 | claude-3-5-haiku |
| **QA** 测试工程师 | 维护 | 单元测试，集成测试，质量守门 | claude-3-5-haiku |
| **KO** 知识进化管理员 | 维护 | 技能提炼，用户建模，RL 轨迹 | claude-3-7-sonnet |
| **Ops** 运维审计员 | 维护 | CI/CD，Hooks 管理，安全审计 | claude-3-5-haiku |

### 3.2 A2A 协作协议

所有 Agent 间的协作必须遵循 QAPS 结构，并通过写入共享文件（可见锚点）来完成任务交接，确保全链路可审计。详见 `memory/global/A2A_PROTOCOL.md`。

---

## 第四章：技能库体系

### 4.1 技能分类

```
skills/
├── core/                    # 系统核心技能（不可删除）
│   ├── opt-taor-engine/     # TAOR 循环执行引擎
│   ├── opt-autodream-memory/ # Auto Dream 记忆巩固
│   ├── opt-rag-knowledge/   # RAG 知识库检索
│   ├── opt-security-audit/  # 安全审计与 Hooks 管理
│   ├── opt-skill-evolution/ # 技能自进化引擎
│   ├── opt-web-publisher/   # 网站发布
│   ├── opt-auto-backup/     # 自动备份
│   └── opt-daily-report/    # 每日报告
├── evolved/                 # Auto Dream 自动生成的技能
│   └── (动态增长)
└── community/               # 社区贡献的技能
    └── (按需安装)
```

### 4.2 技能质量标准

每个 `SKILL.md` 必须满足：
- 至少 50 行内容
- 包含 5 个必填章节（简介、场景、步骤、错误处理、变更日志）
- 包含至少一个代码示例（```bash 或 ```python）

使用 `python3 skills/core/opt-skill-evolution/audit_skills.py` 可以检查所有技能的质量评分。

---

## 第五章：快速开始

### 5.1 三步上手

```bash
# 步骤 1：克隆系统
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 步骤 2：配置环境变量
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY 等

# 步骤 3：一键部署
chmod +x deploy.sh && ./deploy.sh
```

### 5.2 在 openclaw 中使用

将 `opt-v6/` 目录中的文件复制到 openclaw 对应目录：

```bash
# 替换 Agent 配置
cp -r opt-v6/agents/* ~/.openclaw/agents/

# 替换技能库
cp -r opt-v6/skills/* ~/.openclaw/skills/

# 替换 Hooks
cp -r opt-v6/hooks/* ~/.openclaw/hooks/

# 替换主配置
cp opt-v6/config/openclaw.json ~/.openclaw/openclaw.json

# 重启 openclaw
openclaw restart
```

### 5.3 验证部署

```bash
openclaw agents list     # 应显示 8 个 Agent
openclaw skills list     # 应显示 8+ 个技能
openclaw config validate # 验证配置文件
```

---

## 第六章：日常运营 The Loop

每天的工作流程：

```
早上：CoS 读取 USER_PROFILE.md 和 pending_tasks.md
    ↓
与用户对话，理解今日目标
    ↓
QAPS 拆解，派单给对应 Agent
    ↓
Agent 执行（TAOR 引擎，自动重试）
    ↓
CoS 验收结果，汇报给用户
    ↓
晚上：Closeout 流程（记忆压缩，任务归档）
    ↓
每周一凌晨：Auto Dream（技能提炼，画像更新，RL 轨迹收集）
```

---

## 第七章：核心设计哲学

### 7.1 三大架构的统一哲学

> **Claude Code**："规约写得好，AI 才能跑得准。未来最值钱的工程师是能把业务规则、架构约束、安全边界用 AI 能理解的语言精确定义出来的人。"

> **Hermes Agent**："The agent that grows with you. 真正有价值的 Agent 不是功能最多的，而是能随着使用而不断进化的。"

> **OpenHarness**："The model is the agent. The code is the harness. 模型提供推理能力，Harness 提供手、眼、记忆和安全边界。"

### 7.2 OPT 的核心价值主张

你的价值不在于亲自执行每一行代码，而在于：
- **定义品味**：什么是好的设计，什么是好的代码
- **设定边界**：什么可以做，什么绝对不能做
- **验收结果**：判断输出是否符合预期
- **持续进化**：让系统越用越强，而不是越用越乱

---

## 附录 A：相关开源项目

| 项目 | Stars | 与 OPT 的关联 |
|---|---|---|
| Claude Code (Anthropic) | 工业级 | TAOR 引擎、Fail-closed、Context Engineering 来源 |
| Hermes Agent (Nous Research) | 17K | 技能自进化、辩证建模、RL 飞轮来源 |
| OpenHarness (HKUDS) | 2.2K | Hooks 机制、Plan Mode、MCP 生态来源 |
| LightRAG (HKUDS) | 31.9K | 可替换 opt-rag-knowledge 技能的图结构 RAG |
| nanobot (HKUDS) | 37.8K | OPT 的轻量替代方案 |
| openclaw | 活跃 | OPT 系统的运行时环境 |

---

*本宝典由 OPT 龙虾军团自动生成并持续进化。拷贝即升级，进化永不止步。*

🦞 **OpenClaw · OPT · 龙虾军团 v6.0**
