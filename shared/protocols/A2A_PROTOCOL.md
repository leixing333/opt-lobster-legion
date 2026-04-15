# A2A (Agent-to-Agent) 协作协议 v5.0

## 1. 协议简介

本协议定义了 OPT 龙虾军团中 6 个 Agent 之间的协作规范。基于 OpenHarness 的 Swarm 架构和 Claude Code 的 Fail-closed 原则，本协议确保多 Agent 协作的高效性、可追溯性和安全性。

## 2. 核心原则

1. **单点入口**：所有外部任务必须由 CoS（幕僚长）接收并拆解，其他 Agent 不直接与用户交互。
2. **显式锚点（Visible Anchor）**：Agent 之间的任务交接必须通过写入文件（如 `workspace/shared/task-123.md`）进行，禁止仅通过内存或隐藏消息传递。
3. **QAPS 结构**：所有派单必须遵循 QAPS（Question, Assets, Plan, Success Criteria）结构。
4. **Fail-closed 升级**：当底层 Agent（如 Builder）遇到无法解决的错误时，必须向上级（CTO 或 CoS）汇报，禁止静默失败。

## 3. QAPS 派单结构

当一个 Agent 向另一个 Agent 派发任务时，必须在共享目录中创建一个 Markdown 文件，包含以下四个部分：

```markdown
# 任务：[任务名称]

## 1. Question (核心问题/目标)
[明确说明需要解决的问题或达成的目标]

## 2. Assets (可用资产/上下文)
[列出相关的代码文件路径、API 文档链接、历史错误日志等]

## 3. Plan (执行计划/约束)
[说明执行步骤的建议，以及必须遵守的约束条件（如：不能修改数据库结构）]

## 4. Success Criteria (验收标准)
[明确说明什么情况下算作任务完成（如：所有单元测试通过，且覆盖率 > 80%）]
```

## 4. 协作链路示例

### 场景：开发一个新功能

1. **CoS -> CTO**：CoS 接收用户需求，向 CTO 派发架构设计任务。
2. **CTO -> Builder**：CTO 完成设计后，向 Builder 派发具体的编码任务（附带 QAPS 文档）。
3. **Builder -> Researcher**（可选）：Builder 在编码时遇到未知的第三方 API，向 Researcher 派发调研任务。
4. **Builder -> CTO**：Builder 完成编码，向 CTO 提交代码审查请求。
5. **CTO -> CoS**：CTO 审查通过，向 CoS 汇报功能已完成。
6. **CoS -> 用户**：CoS 向用户交付最终成果。

## 5. 异常处理与升级（Escalation）

当 Agent 遇到以下情况时，必须触发升级流程：

- **TAOR 循环耗尽**：Builder 重试 3 次仍失败 -> 升级给 CTO。
- **权限不足**：需要执行危险命令（如删除数据库） -> 升级给 Ops 审计，并由 CoS 确认。
- **需求模糊**：CTO 发现需求存在逻辑漏洞 -> 升级给 CoS，由 CoS 向用户澄清。
```
