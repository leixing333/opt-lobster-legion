# 🦞 OPT 龙虾军团 v3.0 — 一人设计公司 AI 系统

> **基于 Claude Code 工业级架构范式 · 拷贝即升级 · 持续生产力**

---

## 什么是 OPT 龙虾军团？

OPT（One-Person Team）是一套基于 OpenClaw 的多 Agent 协同系统，让一个人拥有一支完整的 AI 团队，实现设计、开发、调研、运营的全链路自动化。

v3.0 版本深度整合了 Claude Code 源码泄露事件中揭示的工业级 Agent 架构范式，包括 TAOR 引擎、四层记忆系统（CARROS）、严格工具隔离和 Fail-closed 安全原则。

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
```

---

## 拷贝即升级（新设备恢复）

```bash
# 1. 克隆仓库
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 2. 配置 .env
cp .env.example .env && nano .env

# 3. 部署
./deploy.sh

# 4. 验证
openclaw agents list   # 应显示 6 个 Agent
openclaw skills list   # 应显示 8 个技能
```

---

## 目录结构

```
opt-lobster-legion/
├── agents/                    # 6 个 AI 角色配置
│   ├── cos/                   # CoS 幕僚长
│   │   └── SOUL.md            # 角色灵魂文件
│   ├── cto/                   # CTO 技术合伙人
│   ├── builder/               # Builder 全栈执行者
│   ├── researcher/            # Researcher 市场情报官
│   ├── ko/                    # KO 知识管理员
│   └── ops/                   # Ops 运维审计员
│
├── skills/                    # 8 个自定义技能
│   ├── opt-taor-engine/       # TAOR 引擎（Think-Act-Observe-Repeat）
│   ├── opt-autodream-memory/  # AutoDream 记忆巩固系统
│   ├── opt-rag-knowledge/     # RAG 知识库检索系统
│   ├── opt-security-audit/    # 安全审计系统
│   ├── opt-design-system/     # 设计系统技能
│   ├── opt-web-publisher/     # 网站发布技能
│   ├── opt-auto-backup/       # 自动备份技能
│   └── opt-daily-report/      # 每日报告技能
│
├── shared/                    # 共享资源
│   ├── protocols/             # A2A 协作协议
│   ├── templates/             # 任务模板
│   └── hooks/                 # 生命周期钩子
│
├── knowledge-base/            # L2 知识库
│   ├── projects/              # 历史项目经验
│   ├── principles/            # 设计原则和架构规范
│   ├── patterns/              # 代码模式和配置模板
│   └── errors/                # 错误记录和解决方案
│
├── workspace/                 # 各 Agent 的 L1 记忆工作区
│   ├── cos/
│   ├── cto/
│   ├── builder/
│   ├── researcher/
│   ├── ko/
│   └── ops/
│
├── docs/                      # 系统文档
│   ├── OpenClaw_Lobster_Legion_Guide_v3.md  # 养虾宝典 v3.0
│   └── Claude_Code_Architecture_Analysis.md # Claude Code 架构分析
│
├── openclaw.json              # 主配置文件
├── .env.example               # 环境变量模板
├── deploy.sh                  # 一键部署脚本
└── README.md                  # 本文件
```

---

## 核心能力矩阵

| 功能 | 实现方案 | 技术来源 |
|---|---|---|
| TAOR 执行引擎 | `opt-taor-engine` 技能 | Claude Code 核心架构 |
| 四层记忆系统 | L0→L1→L2 + AutoDream | Claude Code CARROS |
| 多 Agent 协同 | A2A 两步触发协议 | OpenClaw 最佳实践 |
| 工具权限隔离 | `disallowedTools` 配置 | Claude Code 安全范式 |
| Fail-closed 安全 | 默认最保守安全设置 | Claude Code 安全范式 |
| RAG 知识库 | `opt-rag-knowledge` 技能 | 开源 RAG 生态 |
| 安全审计 | `opt-security-audit` 技能 | Claude Code 审计机制 |
| 拷贝即升级 | `opt-auto-backup` 技能 | OpenClaw 备份系统 |

---

## 在线资源

- **永久网站**：https://leixing333.github.io/opt-lobster-legion/
- **GitHub 仓库**：https://github.com/leixing333/opt-lobster-legion
- **养虾宝典 v3.0**：[docs/OpenClaw_Lobster_Legion_Guide_v3.md](docs/OpenClaw_Lobster_Legion_Guide_v3.md)

---

*本系统由 Manus AI 构建，基于 OpenClaw 社区最佳实践、多 Agent 协同理论以及 Claude Code 工业级架构范式。*
