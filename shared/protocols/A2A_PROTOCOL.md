# OPT 龙虾军团 A2A（Agent-to-Agent）通信协议 v4.0

## 协议概述
本协议定义了 OPT 龙虾军团中 6 个 Agent 之间的通信规范，基于 Claude Code 的 `requireVisibleAnchor` 两步触发机制，确保所有 Agent 间的协作都是**可追溯、可审计、有边界**的。

---

## 核心原则

### 1. 可见锚点原则（Visible Anchor）
所有 A2A 调用必须在对话中留下**可见的文字锚点**，格式如下：
```
[A2A] CoS → Builder: 执行任务 #TASK-001
```
这个锚点的作用是：
- 让老板随时可以看到 Agent 之间在做什么。
- 防止 Agent 在后台"悄悄"执行未经授权的操作。
- 为 Ops 的安全审计提供可追溯的日志。

### 2. 两步触发原则（Two-Step Trigger）
A2A 调用分为两个步骤：
1. **Step 1（声明）**：调用方 Agent 在对话中声明意图，等待确认。
2. **Step 2（执行）**：确认后，被调用方 Agent 才开始执行任务。

### 3. 单一入口原则（Single Entry Point）
老板只与 **CoS（幕僚长）** 直接对话。其他 Agent 不直接接受老板的指令，所有任务都通过 CoS 分发。

---

## 频道隔离（Channel Isolation）
每个 Agent 绑定一个独立的 Slack 频道：

| 频道 | 绑定 Agent | 用途 |
|---|---|---|
| `#hq` | CoS | 老板与 CoS 的专属频道 |
| `#cto` | CTO | 技术架构讨论 |
| `#build` | Builder | 代码提交和部署 |
| `#research` | Researcher | 市场调研和竞品分析 |
| `#know` | KO | 知识沉淀和技能提炼 |
| `#ops` | Ops | 系统监控和安全审计 |

---

## QAPS 任务结构
所有 A2A 任务必须使用 QAPS 结构进行描述：

| 字段 | 说明 | 示例 |
|---|---|---|
| **Q**uestion（问题） | 需要解决的核心问题 | "如何将网站部署到 GitHub Pages？" |
| **A**nswer（预期答案） | 期望的输出形式 | "一个可访问的 GitHub Pages URL" |
| **P**rocess（执行过程） | 执行的关键步骤 | "1. 创建 gh-pages 分支 2. 推送文件 3. 启用 Pages" |
| **S**ource（信息来源） | 参考的知识库或技能 | "`skills/opt-web-publisher/SKILL.md`" |

---

## Agent 通信矩阵

| 调用方 | 可调用的 Agent | 调用场景 |
|---|---|---|
| **CoS** | 所有 Agent | 任务分发、结果验收 |
| **CTO** | Builder | 技术方案实施 |
| **Builder** | CTO | 遇到架构问题时请求指导 |
| **Researcher** | KO | 将调研结果沉淀到知识库 |
| **KO** | 所有 Agent | 请求提供工作成果用于知识沉淀 |
| **Ops** | CoS | 上报安全审计结果 |

**禁止的调用关系：**
- Builder 不得直接调用 Researcher（必须通过 CoS）。
- 任何 Agent 不得直接修改其他 Agent 的 `SOUL.md`。

---

## 标准 A2A 消息格式

### 任务派发消息（CoS → 其他 Agent）
```markdown
[A2A] CoS → {AgentName}: 任务 #{TASK-ID}

**任务描述**：{简要描述任务目标}

**QAPS 结构**：
- Q：{需要解决的核心问题}
- A：{期望的输出形式}
- P：{执行的关键步骤}
- S：{参考的知识库或技能路径}

**截止时间**：{预计完成时间}
**优先级**：{高/中/低}
```

### 任务完成消息（其他 Agent → CoS）
```markdown
[A2A] {AgentName} → CoS: 任务 #{TASK-ID} 完成

**完成状态**：✅ 成功 / ⚠️ 部分完成 / ❌ 失败

**产出物**：
- {产出物描述} - {文件路径或 URL}

**遇到的问题**：
- {问题描述（如有）}

**建议后续行动**：
- {建议（如有）}
```

### 错误上报消息（任何 Agent → CoS）
```markdown
[A2A] {AgentName} → CoS: 错误上报 #{ERROR-ID}

**错误类型**：{技术错误/权限错误/资源不足/其他}
**错误描述**：{详细描述错误情况}
**已尝试的解决方案**：{描述已经尝试过的方法}
**需要的支持**：{需要 CoS 或其他 Agent 提供什么帮助}
```

---

## Closeout 机制（上下文压缩）
基于 Claude Code 的 Context Engineering，当对话上下文接近 Token 上限时，CoS 必须执行 Closeout：

1. **识别压缩时机**：当上下文超过 80% 时触发。
2. **保护头尾**：保留最初的系统提示和最近 5 轮对话。
3. **压缩中间**：将中间的对话内容压缩为结构化摘要，保存到 `workspace/cos/closeout-YYYY-MM-DD.md`。
4. **注入摘要**：将摘要作为新的上下文注入，继续对话。

---

## 变更日志
- 2026-04-15 v4.0：基于 Claude Code `requireVisibleAnchor` 机制深度重写，增加频道隔离表、QAPS 任务结构、Agent 通信矩阵、标准消息格式和 Closeout 机制。
- 2026-03-15 v3.0：初始版本。
