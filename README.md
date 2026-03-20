# 🦞 OPT 龙虾军团 — OpenClaw 一人设计公司系统

> **OpenClaw 养虾宝典 · 完整实施方案**
> 版本：v1.0 | 2026.03 | 作者：Manus AI

一套基于 [OpenClaw](https://github.com/openclaw/openclaw) 的多 Agent 协同系统，帮助超级个体构建具备**持续生产力**的 AI 数字团队。拷贝此目录即可在任意设备上部署完整的龙虾军团。

---

## 快速开始（15 分钟上手）

```bash
# 1. 克隆此仓库
git clone https://github.com/{你的用户名}/opt-lobster-legion.git
cd opt-lobster-legion

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API Keys 和 Slack 频道 ID

# 3. 一键部署
chmod +x deploy.sh && ./deploy.sh

# 4. 在 Slack #hq 频道发送第一条消息，唤醒 CoS 幕僚长
```

---

## 系统架构

```
OPT 龙虾军团 — 三层架构

┌─────────────────────────────────────────────┐
│  意图对齐层                                   │
│  👤 人类老板 ←→ 🤖 CoS 幕僚长 (#hq)          │
└─────────────────────────────────────────────┘
                    ↓ 任务分发
┌─────────────────────────────────────────────┐
│  执行层                                       │
│  🔧 CTO (#cto) → 💻 Builder (#build)         │
│  🔍 Researcher (#research)                   │
└─────────────────────────────────────────────┘
                    ↓ 知识沉淀
┌─────────────────────────────────────────────┐
│  系统维护层                                   │
│  📚 KO 知识管理员 (#know)                     │
│  🛡️ Ops 运维审计员 (#ops)                    │
└─────────────────────────────────────────────┘
```

---

## 目录结构

```
opt-lobster-legion/
├── README.md                    # 本文件，系统总入口
├── deploy.sh                    # 一键部署脚本
├── openclaw.json                # 主配置文件模板
├── .env.example                 # 环境变量模板
│
├── agents/                      # AI 角色定义
│   ├── cos/                     # 幕僚长
│   │   ├── SOUL.md              # 角色性格与职责
│   │   ├── AGENTS.md            # 工作规范
│   │   └── MEMORY.md            # 长期记忆
│   ├── cto/                     # 技术合伙人
│   ├── builder/                 # 全栈执行者
│   ├── researcher/              # 市场情报官
│   ├── ko/                      # 知识管理员
│   └── ops/                     # 运维审计员
│
├── skills/                      # 自定义技能库
│   ├── opt-design-system/       # 品牌设计系统
│   ├── opt-knowledge-base/      # 知识库管理
│   ├── opt-auto-backup/         # 自动备份
│   ├── opt-web-publisher/       # 网站发布
│   ├── opt-brand-guardian/      # 品牌守护
│   └── opt-daily-report/        # 每日报告
│
├── shared/
│   └── PROTOCOLS.md             # 全局协议手册（所有 Agent 必读）
│
├── knowledge-base/              # 企业知识库（RAG 数据源）
│   ├── design/                  # 设计知识
│   ├── tech/                    # 技术知识
│   ├── business/                # 商业知识
│   ├── skills/                  # 技能文档
│   └── lessons-learned/         # 踩坑记录
│
├── workspace/                   # 工作区（项目文件）
│   ├── projects/                # 进行中的项目
│   ├── assets/                  # 设计资产
│   ├── deliverables/            # 交付物
│   └── research/                # 调研报告
│
└── docs/
    └── OpenClaw_Lobster_Legion_Guide.md  # 养虾宝典完整手册
```

---

## 核心功能矩阵

| 功能模块 | 实现方式 | 负责 Agent | 状态 |
|---|---|---|---|
| **长期记忆** | 三层记忆架构（对话→Closeout→RAG）| KO | ✅ |
| **多 Agent 协同** | OpenCrew A2A 两步触发协议 | CoS/CTO | ✅ |
| **知识库 (RAG)** | `opt-knowledge-base` 技能 | KO | ✅ |
| **技能构建** | SKILL.md 标准格式 | KO | ✅ |
| **安全备份** | `opt-auto-backup` 技能 + GitHub | Ops | ✅ |
| **工作区管理** | 沙箱隔离 + 标准目录结构 | Ops | ✅ |
| **操作电脑/应用** | `agent-browser` 社区技能 | Builder | ✅ |
| **CLI 调用** | OpenClaw 内置 Bash 工具 | Builder | ✅ |
| **编程开发** | Builder Agent + CTO 架构指导 | Builder/CTO | ✅ |
| **网站发布** | `opt-web-publisher` 技能 | Builder | ✅ |
| **AI 角色体系** | 6 Agent × SOUL.md 定义 | 全员 | ✅ |
| **每日简报** | `opt-daily-report` 技能 | CoS | ✅ |
| **品牌守护** | `opt-design-system` 技能 | Builder | ✅ |
| **拷贝即升级** | `deploy.sh` + 备份恢复 | Ops | ✅ |

---

## 推荐社区技能（从 ClawHub 安装）

在部署完成后，建议通过 `clawhub install` 安装以下社区技能：

| 技能名 | 功能 | 适用 Agent |
|---|---|---|
| `agent-browser` | 控制浏览器，抓取网页数据 | Researcher, Builder |
| `knowledge-base` | RAG 知识库搜索与更新 | KO, CoS |
| `serper` | Google 搜索 API | Researcher |
| `youtube-transcript` | 提取 YouTube 字幕 | Researcher |
| `github-skill` | GitHub 仓库操作 | Builder |
| `smart-auto-updater` | 自动更新技能 | Ops |
| `skill-creator` | 创建新技能的指南 | KO |
| `daily-digest` | 每日信息摘要 | CoS |

---

## 相关开源项目

本系统参考并集成了以下优秀开源项目：

| 项目 | 功能 | 链接 |
|---|---|---|
| **OpenClaw** | 核心 AI Agent 网关 | [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) |
| **OpenCrew** | 多 Agent 协同架构参考 | [github.com/AlexAnys/opencrew](https://github.com/AlexAnys/opencrew) |
| **awesome-openclaw-skills** | 5400+ 社区技能库 | [github.com/VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) |
| **openclaw-backup** | 备份工具参考 | [github.com/LeoYeAI/openclaw-backup](https://github.com/LeoYeAI/openclaw-backup) |
| **awesome-openclaw-usecases-zh** | 中文用例集合 | [github.com/AlexAnys/awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) |

---

## 文档导航

| 文档 | 内容 | 适合谁读 |
|---|---|---|
| `README.md`（本文件）| 系统总览和快速开始 | 所有人 |
| `docs/OpenClaw_Lobster_Legion_Guide.md` | 养虾宝典完整手册 | 深入理解系统 |
| `shared/PROTOCOLS.md` | 全局协议手册 | 所有 Agent |
| `agents/{角色}/SOUL.md` | 角色性格定义 | 对应 Agent |
| `agents/{角色}/AGENTS.md` | 工作规范 | 对应 Agent |
| `skills/{技能}/SKILL.md` | 技能使用说明 | 对应 Agent |

---

*🦞 愿你的龙虾军团所向披靡，超级个体时代的杠杆属于你。*
