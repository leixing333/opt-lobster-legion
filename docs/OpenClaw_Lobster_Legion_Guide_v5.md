# OpenClaw 养虾宝典：OPT 龙虾军团 v5.0 构建指南

## 1. 系统简介

**OPT 龙虾军团 v5.0** 是一个基于 OpenClaw 框架构建的超级智能体基础设施。它不仅仅是一个多 Agent 聊天系统，而是一个融合了三大顶尖开源项目架构理念的**自我进化型生产力引擎**。

本系统旨在帮助"一人公司"（One-Person Team, OPT）实现设计、开发、研究、运维的全链路自动化。

### 1.1 三大架构基石

v5.0 版本的核心架构汲取了以下三个顶尖项目的精华：

1. **Claude Code (51万行源码)**：
   - **TAOR 引擎**：Think-Act-Observe-Repeat 循环，赋予 Agent 自动纠错能力。
   - **Fail-closed 安全**：默认不可并行、默认非只读，所有危险操作必须显式授权。
   - **Context Engineering**：多级上下文压缩，保护 Token 预算。

2. **Hermes Agent (自我进化)**：
   - **技能自进化**：Agent 在执行中发现成功模式，自动提炼并生成新的 `SKILL.md`。
   - **辩证式用户建模**：采用"正-反-合"逻辑，动态捕捉用户偏好的演变趋势，而非简单累加。

3. **OpenHarness (基础设施范式)**：
   - **Harness 理念**：`Functional Agent = LLM + Harness`。模型负责推理，Harness（代码）提供手、眼、记忆和安全边界。
   - **Hooks 机制**：在工具调用的前后注入拦截器，实现细粒度的权限控制和数据清洗。

## 2. 核心架构：6 Agent 协同体系

系统由 6 个专业化 Agent 组成，每个 Agent 都有明确的职责边界和专属的 `SOUL.md`。

| 角色 | 代号 | 核心职责 | 架构特性 |
|---|---|---|---|
| **幕僚长** | CoS | 唯一对话窗口，任务拆解，结果验收 | 掌握上下文压缩与辩证建模 |
| **技术合伙人** | CTO | 架构设计，代码审查，技术选型 | 监督 TAOR 循环，防范技术债 |
| **执行者** | Builder | 编写代码，执行脚本，部署服务 | 运行 TAOR 引擎，触发技能进化 |
| **研究员** | Researcher | 市场调研，竞品分析，数据收集 | 多源交叉验证，结构化输出 |
| **知识管理员** | KO | 知识沉淀，记忆巩固，画像更新 | 执行 Auto Dream，审核新技能 |
| **运维审计员** | Ops | 安全审计，角色漂移检测，备份 | 运行 Hooks 拦截，执行 Fail-closed |

## 3. 核心机制详解

### 3.1 TAOR 引擎 (Think-Act-Observe-Repeat)
Builder 在执行任务时，不再是"写完代码就报错退出"，而是进入一个闭环：
1. **Think**：分析当前状态，决定下一步。
2. **Act**：执行命令或修改代码。
3. **Observe**：捕获终端输出或错误日志。
4. **Repeat**：如果失败，根据错误日志调整策略并重试（最多 3 次）。

### 3.2 技能自进化 (Skill Evolution)
当 Builder 成功解决一个复杂问题时，会触发进化机制：
1. 提取成功的命令组合。
2. 使用 LLM 抽象化参数。
3. 自动生成标准化的 `SKILL.md`。
4. 注册到知识库，供下次直接调用。

### 3.3 辩证式用户建模 (Dialectical Modeling)
KO 在更新用户画像时，遵循黑格尔的辩证法：
- **正题**：旧画像（如：偏好 Python）。
- **反题**：新观察（如：最近在看 Rust 教程）。
- **合题**：新画像（如：有 Python 背景，正向 Rust 转型，关注性能）。

### 3.4 A2A 协作协议 (Agent-to-Agent)
Agent 之间的协作必须遵循 **QAPS 结构**（Question, Assets, Plan, Success Criteria），并通过写入共享文件（Visible Anchor）进行交接，确保全链路可审计。

## 4. 快速上手

### 4.1 部署步骤

```bash
# 1. 克隆系统
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入必要的 API Keys

# 3. 一键部署
chmod +x deploy.sh && ./deploy.sh
```

### 4.2 日常运营 (The Loop)

- **每日早晨**：CoS 读取 `USER_PROFILE.md`，对齐当天目标。
- **任务执行**：CoS 派单给 CTO/Builder，Builder 运行 TAOR 引擎。
- **每日结束**：CoS 执行 Closeout（上下文压缩）。
- **每周一凌晨**：Ops 执行安全审计，KO 执行 Auto Dream（记忆巩固与技能提炼）。

## 5. 结语

"The model is the agent. The code is the harness."
在 OPT 龙虾军团 v5.0 中，你的价值不再是亲自写每一行代码，而是**定义品味、设定边界、验收结果**。让超级智能体为你工作。
