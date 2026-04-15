# OPT v6.0 A2A 协作协议

## 1. 核心原则

所有 Agent 之间的协作必须遵循本协议。协议的核心是**可见锚点（Visible Anchor）**原则：任何跨 Agent 的任务交接，必须通过写入共享文件（而非口头约定）来完成，确保全链路可审计。

## 2. QAPS 任务结构

所有派单必须遵循 QAPS 结构：

| 字段 | 含义 | 示例 |
|---|---|---|
| **Q** (Question) | 需要解决的核心问题 | "实现用户登录 API" |
| **A** (Assets) | 可用的资产和上下文 | "现有数据库 Schema、API 规范文档" |
| **P** (Plan) | 建议的执行计划 | "1. 设计 JWT 认证流程 2. 实现 /auth/login 端点 3. 编写单元测试" |
| **S** (Success Criteria) | 成功的验收标准 | "POST /auth/login 返回 200 和 JWT Token，QA 测试通过" |

## 3. 派单流程

```
CoS → [写入 memory/workspace/tasks/{task_id}.md] → 目标 Agent
目标 Agent → [执行任务] → [写入 memory/workspace/results/{task_id}.md] → CoS
CoS → [验收] → [更新 memory/workspace/tasks/{task_id}.md 状态为 DONE]
```

## 4. Escalation 升级链路

当 Agent 遇到无法自行解决的问题时，必须触发 Escalation：

```
BE/FE → (TAOR 3次重试失败) → 写入 memory/workspace/escalations/{timestamp}.md → CTO
CTO → (架构级问题) → 通知 CoS
CoS → (影响交付) → 通知用户
```

## 5. Swarm 临时团队协议

CoS 可以动态组建 Swarm 临时团队：

```bash
# 示例：组建 Feature Team 开发登录功能
/swarm create feature-auth FE BE QA
# 共享工作区：memory/workspace/swarms/feature-auth/
# 任务完成后：/swarm dissolve feature-auth
```

Swarm 成员共享一个局部的 `workspace` 记忆，任务完成后自动解散，成果合并到主干。
