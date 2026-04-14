# 🦞 OpenClaw 养虾宝典：OPT 龙虾军团构建指南 v4.0

> **版本说明 (v4.0)**：本版本深度整合了 **Claude Code**（51 万行源码）的工业级安全与执行架构（TAOR 引擎、CARROS 四层记忆、Fail-closed 安全、Context Engineering），以及 **Hermes Agent**（17K Stars）的前沿自我进化机制（闭环学习、辩证式用户建模、技能自进化、RL 训练管道）。这是目前最强大的"一人公司" AI 团队构建指南。

---

## 一、系统愿景：从"工具"到"自我进化的协作体"

OPT（One-Person Team）龙虾军团不再仅仅是一个被动响应指令的工具集合。基于 Hermes Agent 的设计哲学，它是一个**持续自我改进的训练数据工厂与协作伙伴**。

**你的价值在于**：定义品味、设定边界、验收结果。

**Agent 的价值在于**：执行任务、沉淀技能、理解你的演变、并随着你的使用而变得更强。

这是一种全新的人机协作范式：**你不是在使用工具，你是在培养一支懂你的团队。**

---

## 二、技术基础：三大架构来源

### 2.1 OpenClaw 框架

OpenClaw 是本系统的运行基础，提供：
- **多 Agent 协同**：每个 Agent 绑定独立的 Slack 频道，物理隔离防止干扰。
- **技能系统**：标准化的 `SKILL.md` 格式，支持跨框架移植。
- **A2A 协议**：Agent 之间的通信规范，确保可追溯性。

### 2.2 Claude Code 架构（51 万行源码精华）

2026 年 3 月，Anthropic 的 Claude Code 因 npm 配置失误泄露了 51 万行 TypeScript 源码，揭示了工业级 AI Agent 的核心架构：

**TAOR 引擎（Think-Act-Observe-Repeat）**
> Agent 执行任务不是线性的，而是循环的。遇到错误不是直接报错，而是分析错误、调整策略、重试。这是 Claude Code 的核心执行引擎，也是 Builder 不会"卡死"的根本原因。

**CARROS 四层记忆系统**
> 会话记忆（L0）→ 工作区记忆（L1）→ 知识库（L2）→ Auto Dream（L3）。不同重要程度的信息存储在不同层级，确保重要信息不被遗忘，也避免知识库被垃圾信息污染。

**Fail-closed 安全哲学**
> "所有安全相关的默认值都是最保守的。工具默认不可并行、默认非只读、权限默认需要确认。"危险操作（删除文件、发布网站、修改配置）必须有明确的确认步骤。

**Context Engineering（上下文工程）**
> 当对话上下文接近 Token 上限时，CoS 执行 Closeout：保护头尾（系统提示 + 最近 5 轮对话），压缩中间内容为结构化摘要。这是 Claude Code 在有限 Token 预算内最大化信息保留的核心机制。

### 2.3 Hermes Agent 架构（17K Stars）

Hermes Agent 是 Nous Research 开发的开源自我改进型 AI Agent 框架，提供了 OPT 系统中最前沿的能力：

**技能自进化闭环**
> 创建技能 → 使用技能 → 发现改进点 → 更新技能 → 下次使用更好的版本。这是 Hermes 的核心差异化：Agent 不只是使用技能，还会主动改进技能。

**辩证式用户建模（Honcho 引擎）**
> 不是简单追加"用户也用 Rust"，而是通过正-反-合的辩证逻辑，重新推理生成合题："用户是有 Python 背景的系统程序员，正在向 Rust 转型，关注性能和安全性"。这让 Agent 真正理解用户的演变趋势，而不只是记录表面事实。

**RL 训练数据飞轮**
> Hermes 是目前唯一将 Agent 框架与 RL 训练框架完全打通的系统。Agent 执行任务 → 生成轨迹数据 → 智能压缩 → RL 训练 → 更强模型 → 回到起点。OPT 系统预留了轨迹收集接口，为未来的模型微调做准备。

---

## 三、6 Agent 角色体系

### 3.1 三层协同架构

```
意图对齐层：CoS 幕僚长
    ↓ A2A 两步触发协议
执行层：CTO + Builder + Researcher
    ↓ 工作成果
系统维护层：KO + Ops
```

### 3.2 角色详解

**CoS 幕僚长（Chief of Staff）**

CoS 是整个系统的神经中枢，也是老板与 AI 团队之间的唯一对话窗口。它的核心职责不是执行，而是**意图翻译**。

关键能力：
- 在每次对话开始前读取 `USER_PROFILE.md`，了解老板的最新状态。
- 将模糊的需求拆解为 QAPS 结构的工单，派发给对应的执行 Agent。
- 在长对话中执行 Closeout，压缩上下文，节省 Token。
- 在工作日结束时触发 `opt-daily-report`，生成每日汇报。

**禁止操作**：直接写代码、执行系统命令、在没有澄清意图的情况下拍板重大决策。

---

**CTO 技术合伙人（Chief Technology Officer）**

CTO 是技术层面的最高决策者，负责确保整个系统的技术方向正确、代码质量达标。

关键能力：
- 在 Builder 开始执行前，评估技术方案的可行性和风险。
- 在 Builder 完成后，进行代码 Review，确保没有技术债。
- 当 Builder 陷入 TAOR 循环死循环时，介入提供技术指导。
- 将常用的代码模式和架构决策沉淀到知识库。

**禁止操作**：直接执行 shell 命令、部署生产环境。

---

**Builder 全栈执行者**

Builder 是整个系统中唯一有权执行代码和系统命令的 Agent，也是最容易出错的角色。TAOR 循环是它的核心执行机制。

关键能力：
- 严格遵循 TAOR 循环：Think（分析任务）→ Act（执行代码）→ Observe（检查输出）→ Repeat（如有错误则重试）。
- 遇到错误时，最多重试 5 次，每次使用不同的解决方案。
- 成功解决复杂问题后，主动调用 `opt-skill-evolution` 将解决方案沉淀为 `SKILL.md`。
- 在发布网站前，必须先本地预览验证，再请求 CoS 授权。

**禁止操作**：修改系统配置、删除其他 Agent 的工作成果、绕过 CoS 直接向老板汇报。

---

**Researcher 市场情报官**

Researcher 是系统的"眼睛"，负责收集外部信息，为决策提供数据支撑。

关键能力：
- 对任何信息都进行多源交叉验证（至少 3 个独立来源），绝不依赖单一信息源。
- 所有调研结果必须以结构化格式输出（Markdown 表格或对比矩阵），拒绝散文式描述。
- 调研完成后，主动通知 KO 将重要发现沉淀到知识库。

**禁止操作**：直接写代码、执行系统命令、在没有多源验证的情况下给出结论。

---

**KO 知识管理员（Knowledge Officer）**

KO 是系统的"记忆中枢"，负责确保重要信息不被遗忘，并随着时间的推移变得更加精准。

关键能力：
- **Auto Dream（自动做梦）**：每天凌晨 2 点，将各 Agent 的 L1 工作区记忆提炼到 L2 知识库。
- **辩证式用户建模**：使用正-反-合的辩证逻辑，持续更新 `USER_PROFILE.md`。
- **技能库审核**：定期审核技能库，删除过时的技能，确保技能库的质量。
- **RAG 检索**：当其他 Agent 需要查询历史信息时，提供精准的知识库检索服务。

**禁止操作**：执行系统命令、删除其他 Agent 的工作成果。

---

**Ops 运维审计员（Operations）**

Ops 是系统的"免疫系统"，负责确保整个系统的安全性和稳定性。

关键能力：
- **角色漂移防护**：每周检查所有 Agent 的行为日志，确保没有 Agent 越权执行了不该做的操作。
- **自动备份**：每天凌晨 3 点，将整个系统备份到 GitHub，确保"拷贝即升级"的可靠性。
- **安全审计**：每周一生成安全审计报告，上报给 CoS。
- **Fail-closed 执行**：当发现安全风险时，立即停止相关操作，而不是尝试绕过。

**禁止操作**：修改其他 Agent 的 `SOUL.md`、执行未经授权的系统操作。

---

## 四、四层记忆系统（CARROS）

### 4.1 记忆层级说明

```
L0 会话记忆（内存，临时）
    ↓ 超过 80% 触发 Closeout 压缩
L1 工作区记忆（workspace/{agentId}/memory/，30 天保留）
    ↓ KO 每日 Auto Dream 提炼
L2 知识库（knowledge-base/，永久保留）
    ↓ KO 辩证式融合
L3 Auto Dream 精华（knowledge-base/，永久保留）
```

### 4.2 Closeout 机制（上下文压缩）

当对话上下文超过 80% 时，CoS 执行 Closeout：

1. **识别压缩时机**：监控 Token 使用量，超过 80% 时触发。
2. **保护头尾**：保留最初的系统提示和最近 5 轮对话。
3. **压缩中间**：将中间的对话内容压缩为结构化摘要，保存到 `workspace/cos/closeout-YYYY-MM-DD.md`。
4. **注入摘要**：将摘要作为新的上下文注入，继续对话。

### 4.3 Auto Dream 机制（记忆巩固）

每天凌晨 2 点，KO 执行 Auto Dream：

1. **扫描 L1**：读取所有 Agent 的 `workspace/{agentId}/memory/` 目录。
2. **提炼精华**：识别重要的决策、发现和模式，过滤掉临时性的工作状态。
3. **辩证融合**：将新发现与 L2 知识库中的现有知识进行辩证融合（正-反-合）。
4. **更新画像**：如果发现老板的偏好有新变化，更新 `USER_PROFILE.md`。

---

## 五、10 个内置技能

### 5.1 核心引擎技能

**opt-taor-engine**：TAOR 循环执行引擎
- 来源：Claude Code 核心架构
- 功能：为 Builder 和 Researcher 提供 Think-Act-Observe-Repeat 的标准执行框架
- 触发：所有需要执行代码或系统命令的任务

**opt-autodream-memory**：Auto Dream 记忆巩固
- 来源：Claude Code CARROS 记忆系统
- 功能：每天凌晨 2 点，将 L1 工作区记忆提炼到 L2 知识库
- 触发：定时任务（`0 2 * * *`）

**opt-rag-knowledge**：RAG 知识库检索
- 来源：Hermes Agent + 开源 RAG 生态
- 功能：对 L2 知识库进行语义检索，为 Agent 提供精准的历史信息
- 触发：当 Agent 需要查询历史信息时

### 5.2 安全与进化技能

**opt-security-audit**：安全审计
- 来源：Claude Code Fail-closed 安全哲学
- 功能：每周检查所有 Agent 的行为日志，防止角色漂移
- 触发：定时任务（`0 1 * * 1`，每周一凌晨 1 点）

**opt-skill-evolution**：技能自进化
- 来源：Hermes Agent 闭环学习系统
- 功能：当 Agent 成功解决复杂问题后，自动将解决方案沉淀为 `SKILL.md`
- 触发：当 Builder 或 Researcher 完成复杂任务时

**opt-dialectical-modeling**：辩证式用户建模
- 来源：Hermes Agent Honcho 引擎
- 功能：通过正-反-合的辩证逻辑，持续更新用户画像
- 触发：当 KO 观察到老板有新的偏好变化时

### 5.3 业务技能

**opt-design-system**：品牌设计系统管理
- 功能：管理 OPT 的品牌设计规范，确保所有输出物的视觉一致性

**opt-web-publisher**：网站发布
- 功能：将静态网站部署到 GitHub Pages，包含完整的构建、验证、推送和回滚流程

**opt-auto-backup**：自动备份
- 功能：每天凌晨 3 点，将整个系统备份到 GitHub，确保"拷贝即升级"的可靠性

**opt-daily-report**：每日工作报告
- 功能：在每个工作日结束时，自动生成结构化的日报，并触发 Auto Dream

---

## 六、A2A 通信协议

### 6.1 核心原则

**可见锚点原则（Visible Anchor）**：所有 A2A 调用必须在对话中留下可见的文字锚点：
```
[A2A] CoS → Builder: 执行任务 #TASK-001
```

**两步触发原则（Two-Step Trigger）**：
1. Step 1（声明）：调用方在对话中声明意图，等待确认。
2. Step 2（执行）：确认后，被调用方才开始执行任务。

**单一入口原则（Single Entry Point）**：老板只与 CoS 直接对话，所有任务通过 CoS 分发。

### 6.2 QAPS 任务结构

所有 A2A 任务必须使用 QAPS 结构：

| 字段 | 说明 |
|---|---|
| **Q**uestion | 需要解决的核心问题 |
| **A**nswer | 期望的输出形式 |
| **P**rocess | 执行的关键步骤 |
| **S**ource | 参考的知识库或技能 |

---

## 七、快速开始：拷贝即升级

### 7.1 全新安装（约 10 分钟）

```bash
# 步骤 1：克隆系统
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 步骤 2：配置环境变量
cp .env.example .env
nano .env  # 填入以下必填项：
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_APP_TOKEN=xapp-...
# SLACK_OWNER_USER_ID=U...

# 步骤 3：一键部署
chmod +x deploy.sh && ./deploy.sh

# 步骤 4：验证部署
openclaw agents list   # 应显示 6 个 Agent
openclaw skills list   # 应显示 10 个技能
```

### 7.2 新设备恢复（约 5 分钟）

```bash
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion
cp .env.example .env && nano .env  # 填入 API Keys
./deploy.sh
# 完成！6 个 Agent、10 个技能、所有知识库全部恢复
```

### 7.3 系统升级

```bash
git pull origin main
./deploy.sh
# 系统自动检测变更并应用升级
```

---

## 八、日常运营：The Loop

### 8.1 每日工作流程

1. **早上**：查看 CoS 生成的每日简报（`workspace/cos/daily-YYYY-MM-DD.md`）。
2. **工作中**：始终只与 CoS 对话，让 CoS 负责任务分发。
3. **遇到复杂问题**：鼓励 Builder 在解决后使用 `opt-skill-evolution` 沉淀技能。
4. **晚上**：CoS 自动生成日报，KO 执行 Auto Dream 记忆巩固。

### 8.2 每周维护清单

- 查看 Ops 生成的安全审计报告（`workspace/ops/audit-YYYY-WW.md`）。
- 检查 `knowledge-base/profiles/USER_PROFILE.md`，确认 Agent 是否正确理解了你的近期演变。
- 审核新增的技能文件，确认质量达标。
- 检查备份状态，确认 GitHub 仓库有最新的备份。

### 8.3 技能自进化触发条件

当 Builder 或 Researcher 满足以下条件时，必须调用 `opt-skill-evolution` 沉淀技能：

| 条件 | 说明 |
|---|---|
| 解决了需要 3 次以上重试的问题 | 说明这个问题有一定复杂度，值得沉淀 |
| 发现了一个可复用的工具或方法 | 下次遇到类似问题可以直接使用 |
| 完成了一个新类型的任务 | 系统第一次做这件事，值得记录 |

---

## 九、核心设计哲学

### 9.1 可审计性优于自动化

> "记忆用 Markdown 文件而非向量数据库；技能用结构化文档而非编译代码——用户随时可以查看和编辑 Agent 的'大脑'。"

### 9.2 Fail-closed 安全哲学

> "当系统不确定该做什么时，选择最安全的选项（什么都不做），而不是尝试猜测用户意图并执行可能有风险的操作。"

### 9.3 拷贝即升级

> "系统的所有状态都存储在文件中，`.env` 是唯一需要手动配置的文件。任何人都应该能够通过克隆 Git 仓库来获得一个完整可用的系统。"

### 9.4 The Agent That Grows With You

> "未来最值钱的工程师不是写代码最快的，是能把业务规则、架构约束、安全边界，用 AI 能理解的语言精确定义出来的人。规约写得好，AI 才能跑得准。"

---

## 十、版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| **v4.0** | 2026-04-15 | 整合 Hermes Agent 闭环学习系统，全部文件深度重写，10 个技能，完整的辩证式用户建模 |
| v3.0 | 2026-04-10 | 整合 Claude Code 架构，TAOR 引擎，四层记忆，8 个技能 |
| v2.0 | 2026-04-05 | 修复 deploy.sh，推送源代码到 GitHub，网站上线 |
| v1.0 | 2026-04-01 | 初始版本，6 Agent 基础架构 |

---

*本手册由 Manus AI 构建，基于 OpenClaw 社区最佳实践、Claude Code 工业级架构范式（51 万行源码）和 Hermes Agent 闭环学习系统（17K Stars）。*
