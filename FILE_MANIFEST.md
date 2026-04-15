# OPT Lobster Legion — 完整文件清单 v7.1.0

> 生成时间：2026-04-16
> 仓库：`leixing333/opt-lobster-legion`
> 当前版本：**v7.1.0**（Google Stitch + Nano Banana 集成）

---

## 版本演进总览

| 版本 | 核心主题 | 关键交付物 |
|---|---|---|
| v3.0 | 初始多 Agent 框架 | CoS/CTO/Builder/Researcher/KO/Ops 6 Agent |
| v4.0 | 知识库与协议完善 | A2A 协议、设计原则、用户画像 |
| v5.0 | 三大架构融合 | TAOR 引擎、Auto Dream、Hooks 机制、技能自进化 |
| v6.0 | 8 Agent 专业化拆分 | FE/BE/QA 独立、代码级安全拦截（permission_check/audit_logger） |
| v6.1 | 记忆增强 | `memory_compactor.py`、Memory Drift Caveat 扫描 |
| v6.2 | 决策可追溯 | `kairos_daemon.py` KAIROS 追加式日志守护进程 |
| v7.0 | 多模态 + MCP 深度集成 | `vision_parser.py`、`mcp_router.py` |
| **v7.1** | **Google Stitch + Nano Banana** | **`stitch_client.py`、`nano_banana_client.py`、三方联合流水线** |

---

## 完整文件清单

### 根目录

| 文件 | 行数 | 说明 | 版本 |
|---|---|---|---|
| `README.md` | 223 | 项目总览、快速上手指南 | v5.0+ |
| `CHANGELOG.md` | 129 | 完整版本变更历史（v5.0→v7.1） | v7.1 |
| `FILE_MANIFEST.md` | — | 本文件，完整文件清单 | v7.1 |
| `.env.example` | 46 | 环境变量模板（含所有 API Key 说明） | v6.0+ |
| `.gitignore` | 21 | Git 忽略规则 | v5.0+ |
| `deploy.sh` | 127 | 一键部署脚本 | v5.0+ |
| `openclaw.json` | 265 | 旧版主配置（v5.0，保留历史参考） | v5.0 |

### config/（当前主配置）

| 文件 | 行数 | 说明 | 版本 |
|---|---|---|---|
| `config/openclaw.json` | 210 | **当前主配置文件**（v7.1.0，含全部配置块） | v7.1 |

**配置块说明：**
- `engine`：TAOR 引擎参数（maxRetries/timeout/swarm 模式）
- `agents`：8 个 Agent 的模型、SOUL 文件、频道配置
- `memory`：Session 压缩、全局记忆、Drift Caveat 扫描
- `kairos`：KAIROS 日志守护进程配置
- `skills`：技能自进化路径配置
- `hooks`：Pre/Post 工具调用拦截器
- `permissions`：Fail-closed 权限控制
- `mcp`：MCP 服务器配置（GitHub/Postgres）
- `vision`：多模态视觉解析引擎配置
- `mcpRouter`：MCP 权限路由器配置
- `stitch`：**[v7.1 新增]** Google Stitch 认证、Agent 权限矩阵、流水线配置
- `nanaBanana`：**[v7.1 新增]** Nano Banana 三模型配置、Agent 权限矩阵
- `scheduler`：定时任务（Auto Dream 每周一/KAIROS 每日摘要）

### agents/（8 个专业 Agent）

| 文件 | 行数 | 角色 | 版本 | 核心能力 |
|---|---|---|---|---|
| `agents/cos/SOUL.md` | 157 | 幕僚长（Chief of Staff） | v4.0 | QAPS 框架、KAIROS 日志、MCP 统一授权 |
| `agents/cto/SOUL.md` | 97 | 首席技术官 | v3.0 | 技术决策、架构评审、ADR 记录 |
| `agents/fe/SOUL.md` | 157 | 前端工程师 | v4.0 | 多模态视觉工作流、Stitch 集成、Nano Banana 资产生成 |
| `agents/be/SOUL.md` | 114 | 后端工程师 | v3.0 | API 设计、数据库、业务逻辑 |
| `agents/qa/SOUL.md` | 110 | 质量保证工程师 | v3.0 | 测试策略、质量守门、回归测试 |
| `agents/researcher/SOUL.md` | 107 | 市场与数据研究员 | v3.0 | 竞品分析、数据洞察、技术调研 |
| `agents/ko/SOUL.md` | 137 | 知识与进化官 | v3.0 | 技能自进化、记忆管理、知识沉淀 |
| `agents/ops/SOUL.md` | 133 | DevOps 与安全审计员 | v3.0 | 部署自动化、安全审计、合规检查 |
| `agents/builder/SOUL.md` | 55 | 全栈构建者（已拆分） | v3.0 | 保留历史参考，已被 FE/BE/QA 替代 |

### engine/（核心引擎，共 3,392 行）

| 文件 | 行数 | 功能 | 版本 |
|---|---|---|---|
| `engine/taor_loop.sh` | 113 | TAOR 重试引擎（Think→Act→Observe→Reflect） | v6.0 |
| `engine/auto_dream.py` | 303 | 记忆巩固 + Memory Drift Caveat 扫描（步骤0） | v6.1 |
| `engine/memory_compactor.py` | 251 | Session 增量压缩引擎（< 2KB 状态机） | v6.1 |
| `engine/kairos_daemon.py` | 305 | KAIROS 追加式决策日志守护进程 | v6.2 |
| `engine/mcp_router.py` | 447 | 统一 MCP 权限路由器（8 Agent × 5 服务器权限矩阵） | v7.0 |
| `engine/vision_parser.py` | 902 | 多模态视觉解析引擎（含 v7.1 三方联合流水线） | v7.1 |
| `engine/stitch_client.py` | 601 | **[v7.1 新增]** Google Stitch UI 生成客户端 | v7.1 |
| `engine/nano_banana_client.py` | 583 | **[v7.1 新增]** Nano Banana 图像生成客户端 | v7.1 |

**引擎调用关系：**
```
CoS → taor_loop.sh（重试协调）
KO  → auto_dream.py（记忆巩固）→ memory_compactor.py（压缩）
Ops → kairos_daemon.py（日志审计）
所有 Agent → mcp_router.py（MCP 权限路由）
FE  → vision_parser.py → stitch_client.py + nano_banana_client.py
```

### hooks/（安全拦截器）

| 文件 | 行数 | 功能 | 版本 |
|---|---|---|---|
| `hooks/pre_tool_use/permission_check.py` | 89 | 工具调用前权限检查（Fail-closed） | v6.0 |
| `hooks/post_tool_use/audit_logger.py` | 74 | 工具调用后审计日志记录 | v6.0 |

### memory/（运行时记忆）

| 文件 | 行数 | 功能 | 版本 |
|---|---|---|---|
| `memory/global/A2A_PROTOCOL.md` | 47 | Agent 间通信协议（A2A）规范 | v6.0 |
| `memory/profiles/USER_PROFILE.md` | 42 | 用户画像（辩证建模） | v6.0 |

*运行时生成目录：`memory/session/`、`memory/archive/`、`memory/trajectories/`、`memory/kairos_logs/`*

### skills/core/（核心技能，v6.0 重组版）

| 文件 | 行数 | 技能名称 | 功能 |
|---|---|---|---|
| `skills/core/opt-taor-engine/SKILL.md` | 63 | TAOR 引擎技能 | 重试循环使用规范 |
| `skills/core/opt-autodream-memory/SKILL.md` | 230 | Auto Dream 记忆技能 | 记忆巩固与 Drift 扫描 |
| `skills/core/opt-skill-evolution/SKILL.md` | 142 | 技能自进化 | SKILL.md 自动更新规范 |
| `skills/core/opt-rag-knowledge/SKILL.md` | 137 | RAG 知识检索 | 向量检索与知识注入 |
| `skills/core/opt-security-audit/SKILL.md` | 140 | 安全审计 | 代码安全扫描规范 |
| `skills/core/opt-daily-report/SKILL.md` | 148 | 每日报告 | 自动日报生成规范 |
| `skills/core/opt-web-publisher/SKILL.md` | 116 | Web 发布 | 多平台发布自动化 |
| `skills/core/opt-auto-backup/SKILL.md` | 76 | 自动备份 | 定时备份策略 |

### skills/（v5.0 原版技能，保留历史参考）

| 文件 | 行数 | 说明 |
|---|---|---|
| `skills/opt-taor-engine/SKILL.md` | 114 | v5.0 原版 TAOR 技能 |
| `skills/opt-autodream-memory/SKILL.md` | 68 | v5.0 原版记忆技能 |
| `skills/opt-skill-evolution/SKILL.md` | 84 | v5.0 原版进化技能 |
| `skills/opt-rag-knowledge/SKILL.md` | 76 | v5.0 原版 RAG 技能 |
| `skills/opt-security-audit/SKILL.md` | 89 | v5.0 原版安全技能 |
| `skills/opt-daily-report/SKILL.md` | 91 | v5.0 原版日报技能 |
| `skills/opt-web-publisher/SKILL.md` | 114 | v5.0 原版发布技能 |
| `skills/opt-auto-backup/SKILL.md` | 100 | v5.0 原版备份技能 |
| `skills/opt-design-system/SKILL.md` | 84 | 设计系统技能 |
| `skills/opt-dialectical-modeling/SKILL.md` | 87 | 辩证建模技能 |

### docs/（文档库，完整历史）

| 文件 | 行数 | 说明 | 版本 |
|---|---|---|---|
| `docs/OpenClaw_Lobster_Legion_Guide_v3.md` | 149 | v3.0 使用手册 | v3.0 |
| `docs/OpenClaw_Lobster_Legion_Guide_v4.md` | 414 | v4.0 使用手册 | v4.0 |
| `docs/OpenClaw_Lobster_Legion_Guide_v5.md` | 91 | v5.0 使用手册 | v5.0 |
| `docs/OpenClaw_Lobster_Legion_Guide_v6.md` | 302 | v6.0 使用手册（当前主手册） | v6.0 |
| `docs/OPT_v5_Architecture_Design.md` | 79 | v5.0 架构设计文档 | v5.0 |
| `docs/OPT_v6_Architecture_Fusion_Analysis.md` | 102 | v6.0 架构融合分析 | v6.0 |
| `docs/OPT_v5_vs_v6_Analysis_Report.md` | 112 | v5.0 vs v6.0 深度对比报告 | v6.0 |
| `docs/OPT_v6.1_v6.2_Architecture_Plan.md` | 86 | v6.1/v6.2 开发规划 | v6.2 |
| `docs/Hermes_Agent_Architecture_Analysis.md` | 55 | Hermes 架构分析（参考） | v5.0 |
| `docs/OpenHarness_Architecture_Analysis.md` | 78 | OpenHarness 架构分析（参考） | v5.0 |
| `docs/stitch_research.md` | 37 | Google Stitch API 研究笔记 | v7.1 |

### knowledge-base/（知识库，v4.0 原版）

| 文件 | 行数 | 说明 |
|---|---|---|
| `knowledge-base/principles/DESIGN_PRINCIPLES.md` | 105 | 设计原则文档 |
| `knowledge-base/profiles/USER_PROFILE.md` | 53 | 用户画像（v4.0 原版） |

### shared/（共享协议，v4.0 原版）

| 文件 | 行数 | 说明 |
|---|---|---|
| `shared/protocols/A2A_PROTOCOL.md` | 52 | A2A 通信协议（v4.0 原版） |

---

## 统计汇总

| 类别 | 文件数 | 总行数 |
|---|---|---|
| 引擎代码（engine/） | 8 | 3,392 |
| Agent SOUL（agents/） | 9 | 1,027 |
| 安全拦截（hooks/） | 2 | 163 |
| 核心技能（skills/core/） | 8 | 1,052 |
| 历史技能（skills/） | 10 | 907 |
| 文档（docs/） | 11 | 1,505 |
| 配置（config/） | 1 | 210 |
| 记忆（memory/） | 2 | 89 |
| 其他根文件 | 7 | 815 |
| **合计** | **58** | **约 9,160** |

---

## 快速上手（v7.1）

```bash
# 1. 克隆仓库
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入以下 API Key：
#   ANTHROPIC_API_KEY=   Claude API Key（必须）
#   OPENAI_API_KEY=      GPT-4o API Key（视觉解析用）
#   GOOGLE_API_KEY=      Nano Banana API Key
#   STITCH_API_KEY=      Google Stitch API Key
#   STITCH_PROJECT_ID=   Stitch 项目 ID

# 3. 安装依赖
pip install google-genai pillow openai anthropic
npm install -g @google/stitch-sdk  # Stitch SDK（可选）

# 4. 启动 CoS（幕僚长）
claude --model claude-3-7-sonnet-20250219 \
       --system-prompt agents/cos/SOUL.md \
       --config config/openclaw.json

# 5. 使用 FE Agent 的 Stitch + Nano Banana 流水线
python3 engine/vision_parser.py pipeline <设计图路径> <输出目录>
# 或从 Prompt 开始（需要 STITCH_API_KEY）：
python3 -c "
from engine.vision_parser import VisionParser
p = VisionParser()
result = p.full_pipeline_v71(
    'A dark SaaS dashboard with sidebar navigation',
    'workspace/output',
    use_stitch=True
)
print(result)
"
```

---

*本文件由 OPT 系统自动生成，最后更新：2026-04-16*
