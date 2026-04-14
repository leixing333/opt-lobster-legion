# 🦞 OPT 龙虾军团 v4.0

> **一人设计公司 AI 军团系统** | OpenClaw + Claude Code CARROS 架构 + Hermes Agent 闭环学习

[![Version](https://img.shields.io/badge/version-4.0.0-orange.svg?style=flat-square)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Agents](https://img.shields.io/badge/agents-6-green.svg?style=flat-square)](#6-位数字员工)
[![Skills](https://img.shields.io/badge/skills-10-purple.svg?style=flat-square)](#10-个内置技能)

**永久网站**：https://leixing333.github.io/opt-lobster-legion/

---

## 什么是 OPT 龙虾军团？

OPT（One-Person Team）是一套**可移植的 AI 团队配置系统**，让一个人拥有一支 6 人 AI 团队的战斗力。它基于三个顶尖项目的架构精华构建：

| 来源 | 核心贡献 |
|---|---|
| **OpenClaw** | 多 Agent 协同框架、Slack 频道绑定、技能系统 |
| **Claude Code**（51 万行源码） | TAOR 循环引擎、CARROS 四层记忆、Fail-closed 安全哲学、Context Engineering |
| **Hermes Agent**（17K Stars） | 技能自进化闭环、辩证式用户建模（正-反-合）、RL 数据飞轮 |

---

## 快速开始（3 步上手）

```bash
# 步骤 1：克隆系统
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 步骤 2：配置环境变量
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY、SLACK_BOT_TOKEN 等

# 步骤 3：一键部署
chmod +x deploy.sh && ./deploy.sh

# 验证部署
openclaw agents list   # 应显示 6 个 Agent
openclaw skills list   # 应显示 10 个技能
```

---

## 系统架构

### 三层协同体系

```
┌─────────────────────────────────────────────────────────────┐
│                    意图对齐层                                 │
│  CoS 幕僚长（唯一对话入口，任务拆解，辩证式用户建模）           │
└──────────────────────┬──────────────────────────────────────┘
                       │ A2A 两步触发协议（requireVisibleAnchor）
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│ CTO       │  │ Builder   │  │Researcher │
│ 技术架构  │  │ 代码执行  │  │ 市场情报  │
│ 代码审查  │  │ TAOR 循环 │  │ 多源验证  │
└───────────┘  └───────────┘  └───────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼                             ▼
┌───────────┐                  ┌───────────┐
│ KO        │                  │ Ops       │
│ 知识沉淀  │                  │ 安全审计  │
│ Auto Dream│                  │ 自动备份  │
└───────────┘                  └───────────┘
```

### 四层记忆架构（CARROS）

| 层级 | 类型 | 存储位置 | 触发方式 |
|---|---|---|---|
| **L0** | 会话记忆 | 内存（临时） | 自动，超 80% 触发 Closeout 压缩 |
| **L1** | 工作区记忆 | `workspace/{agentId}/memory/` | 每次对话后自动写入 |
| **L2** | 知识库 | `knowledge-base/` | KO 手动沉淀 |
| **L3** | Auto Dream | `knowledge-base/` | 每天凌晨 2 点自动触发 |

### Hermes 技能自进化闭环

```
创建技能 → 使用技能 → 发现改进点 → 更新技能 → 下次使用更好的版本
    ↑                                                      │
    └──────────────────────────────────────────────────────┘
```

---

## 6 位数字员工

| 角色 | 推荐模型 | 核心职责 | 关键技能 |
|---|---|---|---|
| **CoS 幕僚长** | claude-opus-4-5 | 唯一对话入口，任务拆解 | 辩证式用户建模 |
| **CTO 技术合伙人** | claude-sonnet-4-5 | 技术架构，代码审查 | TAOR 监督 |
| **Builder 执行者** | gpt-4.1-mini | 代码实现，网站构建 | TAOR 循环，技能自进化 |
| **Researcher 情报官** | gemini-2.5-flash | 竞品分析，行业调研 | 多源交叉验证 |
| **KO 知识管理员** | gpt-4.1-nano | 知识沉淀，Auto Dream | 辩证式建模 |
| **Ops 运维审计员** | gpt-4.1-mini | 安全审计，自动备份 | Fail-closed |

---

## 10 个内置技能

| 技能 | 来源灵感 | 功能 |
|---|---|---|
| `opt-taor-engine` | Claude Code | Think-Act-Observe-Repeat 执行引擎 |
| `opt-autodream-memory` | Claude Code CARROS | 后台记忆巩固，L1→L2 提炼 |
| `opt-rag-knowledge` | Hermes Agent | RAG 知识库检索 |
| `opt-security-audit` | Claude Code Fail-closed | 安全审计，角色漂移防护 |
| `opt-skill-evolution` | Hermes Agent | 技能自进化，闭环学习 |
| `opt-dialectical-modeling` | Hermes Agent Honcho | 辩证式用户建模（正-反-合） |
| `opt-design-system` | OPT 原创 | 品牌设计系统管理 |
| `opt-web-publisher` | OPT 原创 | 网站发布到 GitHub Pages |
| `opt-auto-backup` | OPT 原创 | 自动备份到 GitHub |
| `opt-daily-report` | OPT 原创 | 每日工作报告生成 |

---

## 目录结构

```
opt-lobster-legion/
├── agents/                    # 6 个 Agent 配置
│   ├── cos/SOUL.md            # CoS 幕僚长灵魂文件（含辩证式建模指令）
│   ├── cto/SOUL.md            # CTO 技术合伙人（含架构审查流程）
│   ├── builder/SOUL.md        # Builder 执行者（含 TAOR 循环指令）
│   ├── researcher/SOUL.md     # Researcher 情报官（含多源验证要求）
│   ├── ko/SOUL.md             # KO 知识管理员（含 Auto Dream 流程）
│   └── ops/SOUL.md            # Ops 运维审计员（含 Fail-closed 规则）
├── skills/                    # 10 个内置技能（全部有完整执行流程）
│   ├── opt-taor-engine/
│   ├── opt-autodream-memory/
│   ├── opt-rag-knowledge/
│   ├── opt-security-audit/
│   ├── opt-skill-evolution/
│   ├── opt-dialectical-modeling/
│   ├── opt-design-system/
│   ├── opt-web-publisher/
│   ├── opt-auto-backup/
│   └── opt-daily-report/
├── knowledge-base/            # L2 知识库
│   ├── principles/DESIGN_PRINCIPLES.md  # 10 条核心设计原则
│   └── profiles/USER_PROFILE.md         # 辩证式用户画像
├── shared/protocols/          # 共享协议
│   └── A2A_PROTOCOL.md        # A2A 通信协议（含 QAPS 结构）
├── docs/                      # 技术文档
│   ├── OpenClaw_Lobster_Legion_Guide_v4.md   # 养虾宝典 v4.0
│   ├── Claude_Code_Architecture_Analysis.md  # Claude Code 深度分析
│   └── Hermes_Agent_Architecture_Analysis.md # Hermes Agent 深度分析
├── openclaw.json              # 主配置文件（v4.0，含所有新特性）
├── .env.example               # 环境变量模板
├── deploy.sh                  # 一键部署脚本
└── README.md                  # 本文件
```

---

## 核心能力矩阵

| 功能 | 实现方案 | 技术来源 | 状态 |
|---|---|---|---|
| TAOR 执行引擎 | `opt-taor-engine` 技能 | Claude Code | ✅ |
| 四层记忆系统 | L0→L1→L2→L3 Auto Dream | Claude Code CARROS | ✅ |
| 技能自进化 | `opt-skill-evolution` 技能 | Hermes Agent | ✅ |
| 辩证式用户建模 | `opt-dialectical-modeling` 技能 | Hermes Agent Honcho | ✅ |
| 多 Agent 协同 | A2A 两步触发协议 | OpenClaw | ✅ |
| 工具权限隔离 | `disallowedTools` 配置 | Claude Code | ✅ |
| Fail-closed 安全 | 默认最保守安全设置 | Claude Code | ✅ |
| Context Engineering | Closeout 压缩机制 | Claude Code | ✅ |
| RAG 知识库 | `opt-rag-knowledge` 技能 | 开源 RAG 生态 | ✅ |
| 拷贝即升级 | Git 仓库 + `deploy.sh` | OPT 原创 | ✅ |

---

## 拷贝即升级

这是 OPT 系统最重要的设计原则：**所有状态都存储在文件中**，`.env` 是唯一需要手动配置的文件。

```bash
# 在新设备上恢复整个系统（约 5 分钟）
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion
cp .env.example .env && nano .env  # 填入 API Keys
./deploy.sh
# 完成！6 个 Agent、10 个技能、所有知识库全部恢复
```

---

## 核心设计哲学

> **"未来最值钱的工程师不是写代码最快的，是能把业务规则、架构约束、安全边界，用 AI 能理解的语言精确定义出来的人。规约写得好，AI 才能跑得准。"**

你的价值在于**定义品味、设定边界、验收结果**，而不是亲自执行每一行代码。

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| **v4.0** | 2026-04-15 | 整合 Hermes Agent 闭环学习系统，全部文件深度重写，10 个技能 |
| v3.0 | 2026-04-10 | 整合 Claude Code 架构，TAOR 引擎，四层记忆，8 个技能 |
| v2.0 | 2026-04-05 | 修复 deploy.sh，推送源代码到 GitHub，网站上线 |
| v1.0 | 2026-04-01 | 初始版本，6 Agent 基础架构 |

---

## 在线资源

- **永久网站**：https://leixing333.github.io/opt-lobster-legion/
- **GitHub 仓库**：https://github.com/leixing333/opt-lobster-legion
- **养虾宝典 v4.0**：[docs/OpenClaw_Lobster_Legion_Guide_v4.md](docs/OpenClaw_Lobster_Legion_Guide_v4.md)
- **Claude Code 分析**：[docs/Claude_Code_Architecture_Analysis.md](docs/Claude_Code_Architecture_Analysis.md)
- **Hermes Agent 分析**：[docs/Hermes_Agent_Architecture_Analysis.md](docs/Hermes_Agent_Architecture_Analysis.md)

---

*本系统由 Manus AI 构建，基于 OpenClaw 社区最佳实践、Claude Code 工业级架构范式和 Hermes Agent 闭环学习系统。*
