# OPT 龙虾军团 v5.0 架构设计：三大顶尖框架的融合

## 1. 架构愿景：超级智能体基础设施

在 v5.0 版本中，OPT 龙虾军团不再仅仅是一个"多 Agent 团队"，而是一个**具备自主进化能力的超级智能体基础设施**。我们深度融合了目前业界最顶尖的三大开源/泄露架构：

1. **Claude Code (51万行源码)**：提供工业级的执行稳定性（TAOR 引擎）与安全边界（Fail-closed）。
2. **Hermes Agent (17K Stars)**：提供前沿的自我进化能力（技能闭环、辩证建模、RL 飞轮）。
3. **OpenHarness (HKUDS)**：提供基础设施范式（模型即智能体，代码即 Harness，Hooks 机制）。

## 2. 核心融合机制

### 2.1 认知与执行解耦（OpenHarness + Claude Code）
- **模型层（认知）**：负责意图理解、任务拆解、代码生成。
- **Harness 层（执行）**：负责工具调用、权限校验、结果清洗。
- **融合点**：Builder 的 TAOR 循环不再由模型自己盲目重试，而是由底层的 Harness 脚本（`opt-taor-engine`）控制重试逻辑和错误捕获，模型只负责在每次循环中提供新的解决方案。

### 2.2 五层记忆与辩证建模（Claude Code + Hermes Agent）
- **L0 会话记忆**：当前对话上下文（受 Token 限制）。
- **L1 工作区记忆**：短期项目状态（30天保留）。
- **L2 知识库**：长期沉淀的规范与模式。
- **L3 Auto Dream**：夜间后台提炼的精华（Claude Code 机制）。
- **L4 辩证画像**：基于正-反-合逻辑动态演变的用户画像（Hermes Agent 机制）。
- **融合点**：KO（知识管理员）每天凌晨执行 Auto Dream 时，不仅提炼知识，还必须调用 `opt-dialectical-modeling` 更新 L4 画像。

### 2.3 技能自进化与 Hooks 拦截（Hermes Agent + OpenHarness）
- **技能创建**：Builder 解决复杂问题后，调用 `opt-skill-evolution` 沉淀技能。
- **Hooks 拦截**：所有技能在执行前后，必须经过 `PreToolUse` 和 `PostToolUse` 钩子（OpenHarness 机制）。
- **融合点**：Ops（运维审计员）通过配置全局 Hooks，在任何技能执行前进行权限校验（Fail-closed），在执行后进行敏感信息脱敏。

## 3. 目录结构重构 (v5.0)

```text
opt-lobster-legion/
├── agents/                 # 6 个 Agent 的核心定义
│   ├── cos/                # 幕僚长（意图对齐、任务分发）
│   ├── cto/                # 技术合伙人（架构把控、代码 Review）
│   ├── builder/            # 全栈执行者（TAOR 引擎、代码编写）
│   ├── researcher/         # 市场情报官（多源验证、结构化输出）
│   ├── ko/                 # 知识管理员（Auto Dream、辩证建模）
│   └── ops/                # 运维审计员（Hooks 拦截、安全审计）
│       ├── SOUL.md         # 角色灵魂（认知层）
│       └── AGENTS.md       # 工作规范（Harness 层约束）[v5.0 新增]
├── skills/                 # 10 个核心技能（含可执行脚本）
│   ├── opt-taor-engine/    # TAOR 循环执行引擎
│   ├── opt-autodream-memory/ # Auto Dream 记忆巩固
│   ├── opt-rag-knowledge/  # RAG 知识库检索
│   ├── opt-security-audit/ # 安全审计与 Hooks 拦截
│   ├── opt-skill-evolution/# 技能自进化闭环
│   ├── opt-dialectical-modeling/ # 辩证式用户建模
│   ├── opt-design-system/  # 品牌设计系统
│   ├── opt-web-publisher/  # 网站发布流水线
│   ├── opt-auto-backup/    # 自动备份机制
│   └── opt-daily-report/   # 每日工作报告
├── shared/                 # 共享基础设施
│   ├── protocols/          # A2A 通信协议
│   └── hooks/              # 全局生命周期钩子 [v5.0 新增]
├── knowledge-base/         # L2-L4 长期记忆库
│   ├── principles/         # 设计原则与架构规范
│   ├── patterns/           # 代码模式与配置模板 [v5.0 补充]
│   ├── errors/             # 错误记录与解决方案 [v5.0 补充]
│   ├── projects/           # 历史项目经验
│   └── profiles/           # 辩证式用户画像
├── workspace/              # L1 短期工作区记忆
├── openclaw.json           # 主配置文件（新增 MCP 与 Hooks 配置）
├── deploy.sh               # 一键部署脚本（Harness 启动器）
└── README.md               # 系统总入口
```

## 4. 核心工作流：The Super Loop

1. **输入**：老板向 CoS 发送模糊指令。
2. **认知**：CoS 读取 L4 辩证画像，澄清意图，拆解为 QAPS 工单。
3. **分发**：CoS 通过 A2A 协议将工单派发给 Builder。
4. **执行**：Builder 启动 TAOR 引擎（Harness 层接管）。
5. **拦截**：执行任何命令前，触发 Ops 的 `PreToolUse` Hook 进行权限校验。
6. **进化**：Builder 成功后，调用 `opt-skill-evolution` 沉淀新技能。
7. **沉淀**：凌晨 2 点，KO 执行 Auto Dream，提炼 L1 记忆到 L2 知识库，并更新 L4 画像。
8. **审计**：每周一，Ops 执行安全审计，防止角色漂移。
