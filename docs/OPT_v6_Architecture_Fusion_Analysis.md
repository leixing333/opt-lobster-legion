# OPT 龙虾军团 v6.0：三大顶尖智能体架构融合与演进分析

## 1. 三大顶尖系统架构解构与互补分析

基于用户提供的目录结构，我们对当前开源界最顶尖的三个 Agent 系统（Claude Code、Hermes Agent、OpenHarness）进行了深度解构。这三个系统分别代表了三种不同的工程哲学，它们的融合将产生质的飞跃。

### 1.1 Claude Code：极致的工程化与安全控制 (51万行源码)
**核心哲学**：生产级、强约束、安全第一。
- **架构特征**：庞大的 `utils/` (564文件) 和 `components/` (389文件) 证明了其在终端交互和异常处理上的极致追求。
- **核心优势**：
  - **QueryEngine & Agent Loop**：1700+ 行的循环控制，确保了 TAOR（Think-Act-Observe-Repeat）的稳定性。
  - **IDE 桥接层 (`bridge/`)**：直接与 VS Code/JetBrains 通信，这是真正的生产力工具特征。
  - **多 Agent 协调 (`coordinator/`)**：虽然是实验性，但提供了主从架构的雏形。
- **对 OPT 的启示**：我们需要引入 `coordinator` 概念，强化异常捕获，并建立严格的命令分发机制（`commands/`）。

### 1.2 Hermes Agent：闭环学习与自我进化
**核心哲学**：动态演进、强化学习、模型自适应。
- **架构特征**：`environments/` (RL 训练)、`honcho_integration/` (用户建模)、`batch_runner.py` (轨迹生成)。
- **核心优势**：
  - **自注册工具系统**：工具即插即用，支持动态组合（`toolsets.py`）。
  - **RL 数据飞轮**：不仅解决问题，还收集解决问题的轨迹用于未来模型微调。
  - **辩证式用户建模**：动态捕捉用户意图演变。
- **对 OPT 的启示**：OPT 必须具备"记忆"和"进化"能力，技能（Skills）不应是静态的，而应是可动态生成和组合的。

### 1.3 OpenHarness：基础设施与模块化范式
**核心哲学**：模型即智能体，代码即 Harness（控制带）。
- **架构特征**：清晰的 10 大子系统划分（`engine/`, `plugins/`, `hooks/`, `mcp/` 等）。
- **核心优势**：
  - **Hooks 生命周期**：`PreToolUse`/`PostToolUse` 提供了完美的切面编程能力，用于安全审计和数据清洗。
  - **MCP 生态接入**：原生支持 Model Context Protocol，直接复用上万个现有工具。
  - **多级权限模式**：Default/Auto/Plan Mode，平衡了自主性与安全性。
- **对 OPT 的启示**：OPT 的目录结构应该向 OpenHarness 靠拢，将系统解耦为清晰的子模块（Hooks, MCP, Tasks, Memory）。

---

## 2. OPT 龙虾军团 v6.0 角色体系重构思考

当前的 6 个角色（CoS, CTO, Builder, Researcher, KO, Ops）在软件开发场景下存在一定的局限性。为了实现"一人公司"（OPT）的通用开发与运营能力，我们需要对角色进行扩展和重新定义。

### 2.1 现有角色的局限性
- **开发深度不足**：Builder 承担了所有编码工作，但在大型项目中，前端、后端、测试往往需要不同的上下文和技能集。
- **缺乏产品视角**：没有专门负责需求分析、UI/UX 设计和用户体验的角色。
- **缺乏外部交互**：缺少专门负责部署、监控和外部 API 对接的"DevOps"角色（目前的 Ops 更偏向内部安全审计）。

### 2.2 v6.0 角色体系扩展设计 (8 角色矩阵)

我们将构建一个更具柔性和深度的超级智能体团队：

| 角色 | 代号 | 职责定位 | 对应三大架构的特性 |
|---|---|---|---|
| **幕僚长/产品经理** | CoS | 需求拆解、进度协调、最终验收 | Claude Code 的 `coordinator` |
| **技术合伙人** | CTO | 架构设计、技术选型、代码审查 | OpenHarness 的 `Plan Mode` |
| **前端工程师** | FE | UI/UX 实现、交互逻辑、组件开发 | 专注前端上下文，减少 Token 污染 |
| **后端工程师** | BE | API 设计、数据库建模、核心业务逻辑 | 专注后端上下文，运行 TAOR 引擎 |
| **测试工程师** | QA | 单元测试、集成测试、自动化测试 | 闭环验证，确保 Fail-closed |
| **研究员/数据分析** | Researcher | 竞品分析、API 调研、数据清洗 | Hermes 的多源交叉验证 |
| **知识/进化管理员** | KO | 技能提炼、用户画像、RL 轨迹收集 | Hermes 的自我进化与 Honcho 建模 |
| **运维/安全审计** | Ops | CI/CD 部署、Hooks 拦截、MCP 管理 | OpenHarness 的 Hooks 与 MCP 生态 |

---

## 3. v6.0 目录结构设计 (融合三大架构)

为了支撑上述 8 个角色和复杂的进化机制，我们将重构工作区目录，使其成为一个真正的"Harness 基础设施"：

```text
opt-v6-workspace/
├── agents/                 # 8 个角色的 SOUL.md 与上下文
│   ├── cos/, cto/, fe/, be/, qa/, researcher/, ko/, ops/
├── engine/                 # 核心驱动层 (借鉴 Claude Code)
│   ├── taor_loop.sh        # TAOR 循环执行器
│   └── coordinator.py      # 多 Agent 任务调度器
├── skills/                 # 动态技能库 (借鉴 Hermes)
│   ├── core/               # 内置核心技能
│   └── evolved/            # Agent 自主进化生成的技能
├── hooks/                  # 生命周期拦截器 (借鉴 OpenHarness)
│   ├── pre_tool_use/       # 执行前权限检查
│   └── post_tool_use/      # 执行后结果清洗
├── mcp/                    # MCP 服务器配置与客户端
├── memory/                 # 四层记忆系统
│   ├── session/            # 短期会话
│   ├── workspace/          # 项目级上下文
│   ├── global/             # 全局知识库 (DESIGN_PRINCIPLES 等)
│   └── profiles/           # 辩证式用户画像
├── tasks/                  # 后台异步任务管理
├── commands/               # 斜杠命令注册表 (/plan, /commit 等)
├── config/                 # 多层配置文件 (openclaw.json)
└── deploy.sh               # 一键部署与环境检查
```

## 4. 核心融合机制设计

### 4.1 柔性协作：Coordinator 与 Swarm 的结合
CoS 不再是简单的消息转发器，而是具备 `coordinator` 能力的调度中心。当面临复杂开发任务时，CoS 可以动态组建临时 Swarm（例如：FE + BE + QA 组成一个 Feature Team），共享一个局部的 `workspace` 记忆，任务完成后自动解散，将成果合并到主干。

### 4.2 进化闭环：RL 轨迹与技能生成
每次成功的 TAOR 循环（例如 BE 成功修复了一个复杂的数据库死锁），KO 会在后台（Auto Dream 阶段）提取这次交互的轨迹（Prompt -> Action -> Observation），将其转化为：
1. 一个新的 `SKILL.md`（供下次直接调用）。
2. 一条 RL 训练数据（存储在 `memory/trajectories/`，为未来微调本地模型做准备）。

### 4.3 绝对安全：Hooks 与 MCP 的隔离
所有危险操作（如 `BashTool` 执行 `rm -rf`）都会触发 `hooks/pre_tool_use/` 中的拦截脚本。Ops 角色会根据 `openclaw.json` 中的权限矩阵（Default/Auto/Plan Mode）决定是直接放行、要求 CoS 确认，还是直接拒绝。外部工具全部通过 MCP 协议接入，实现沙箱隔离。
