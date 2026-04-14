# 🦞 OpenClaw 养虾宝典：OPT 龙虾军团构建指南 v4.0

> **版本说明 (v4.0)**：本版本深度整合了 **Claude Code** 的工业级安全与执行架构（TAOR 引擎、Fail-closed 安全），以及 **Hermes Agent** 的前沿自我进化机制（闭环学习、辩证式用户建模、技能自进化、RL 训练管道）。这是目前最强大的“一人公司” AI 团队构建指南。

---

## 一、系统愿景：从“工具”到“自我进化的协作体”

OPT（One-Person Team）龙虾军团不再仅仅是一个被动响应指令的工具集合。基于 Hermes Agent 的设计哲学，它是一个**持续自我改进的训练数据工厂与协作伙伴**。

你的价值在于：**定义品味、设定边界、验收结果**。
Agent 的价值在于：**执行任务、沉淀技能、理解你的演变、并随着你的使用而变得更强**。

---

## 二、核心架构升级 (v4.0 亮点)

### 1. 五层记忆与辩证式用户建模 (Dialectical User Modeling)
借鉴 Hermes 的 Honcho 引擎，OPT 引入了动态进化的用户画像机制：
- **不再是静态标签**：Agent 不会简单地记录“你喜欢 Python”，而是通过“正-反-合”的辩证逻辑，理解你“正在从 Python 开发者向关注内存安全的 Rust 程序员转型”。
- **实现方式**：通过 `opt-dialectical-modeling` 技能，KO（知识管理员）会在每次 Closeout 时，将新观察到的偏好与旧画像融合，生成更新的自然语言描述（`USER_PROFILE.md`）。

### 2. 技能自进化引擎 (Skill Evolution Engine)
- **开放标准**：所有技能严格遵循 `agentskills.io` 的 `SKILL.md` 格式，确保跨框架的可移植性。
- **闭环学习**：当 Builder 或 Researcher 解决了一个复杂问题，它们会通过 `opt-skill-evolution` 技能，自主将其沉淀为标准化的 `SKILL.md`。在后续使用中，如果发现步骤缺失或有更优解，Agent 会主动修改并迭代该技能文档。

### 3. TAOR 引擎与上下文精细化管理
- **TAOR 循环**：Think → Act → Observe → Repeat。Agent 在遇到错误时不会直接崩溃，而是进入内部重试循环，直到成功或达到最大重试次数。
- **四阶段压缩流水线**：在长对话中，CoS（幕僚长）会采用 Hermes 的策略：保护对话头尾（系统提示和最新推理），将中间冗长的工具交互替换为 LLM 摘要，从而在有限的 Token 预算内最大化保留关键信息。

### 4. 强化学习 (RL) 训练数据飞轮
- **轨迹收集**：OPT 军团的每一次成功任务执行，其完整的对话记录（Trajectory）都可以被收集并压缩。
- **数据工厂**：这些高质量的轨迹数据，未来可以直接对接类似 Atropos 的 RL 训练环境，用于微调你专属的底层大模型。

---

## 三、6 Agent 角色体系 (v4.0 增强版)

| 角色 | 职责 | v4.0 核心增强能力 |
|---|---|---|
| **CoS (幕僚长)** | 唯一对话窗口，任务拆解，结果验收 | 掌握辩证式用户画像，执行上下文智能压缩 |
| **CTO (技术合伙人)** | 技术架构设计，代码 Review | 监督 Builder 的 TAOR 循环，确保代码质量 |
| **Builder (执行者)** | 编写代码，执行具体任务 | 具备技能自进化能力，自主沉淀 `SKILL.md` |
| **Researcher (研究员)** | 市场调研，情报收集 | 结构化输出调研报告，辅助构建知识库 |
| **KO (知识管理员)** | 知识沉淀，RAG 检索，画像更新 | 执行“正-反-合”逻辑，维护动态用户画像 |
| **Ops (运维审计员)** | 安全审计，自动备份，权限管控 | 监督所有自动生成的技能，确保 Fail-closed 安全 |

---

## 四、快速开始：拷贝即升级

### 步骤 1：克隆系统
```bash
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion
```

### 步骤 2：配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入必要的 API Keys
```

### 步骤 3：一键部署
```bash
chmod +x deploy.sh && ./deploy.sh
```

### 步骤 4：验证部署
```bash
openclaw agents list      # 确认 6 个 Agent 均已就绪
openclaw skills list      # 确认 8+ 个核心技能已加载
```

---

## 五、日常运营与维护 (The Loop)

1. **任务下发**：始终只与 CoS 对话。
2. **技能沉淀**：鼓励 Agent 在完成复杂任务后，使用 `opt-skill-evolution` 技能。
3. **画像核对**：定期查看 `knowledge-base/profiles/USER_PROFILE.md`，确认 Agent 是否正确理解了你的近期演变。
4. **安全审计**：每周查看 Ops 生成的审计报告，Review 新增的技能和修改的系统配置。

> **"The agent that grows with you."** —— 欢迎来到 OPT 龙虾军团 v4.0 时代。
