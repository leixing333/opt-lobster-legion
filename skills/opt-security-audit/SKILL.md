# 技能：OPT 安全审计系统

## 简介
本技能基于 Claude Code 的 Fail-closed 安全哲学，为 Ops（运维审计员）提供**系统安全审计**能力。它通过定期检查 Agent 的行为日志，防止角色漂移、越权操作和技能滥用，确保整个 OPT 系统在安全可控的边界内运行。

## 适用角色
**Ops**（主要）

## 触发条件
- 每周一凌晨定时任务触发（推荐 01:00 AM）。
- 当 CoS 收到异常报告时手动触发。
- 当某个 Agent 在 24 小时内调用了超过 50 次工具时自动触发。

## 执行步骤

### 步骤 1：日志收集（Log Collection）
收集各 Agent 的操作日志：
```bash
# 收集过去 7 天的操作日志
find ./workspace -name "*.log" -newer $(date -d "7 days ago" +%Y-%m-%d) -type f
```

### 步骤 2：角色漂移检测（Role Drift Detection）
对照每个 Agent 的 `SOUL.md`，检查其操作日志是否存在越界行为：

| 检测项目 | 违规示例 | 严重程度 |
|---|---|---|
| CoS 直接写代码 | CoS 调用了 `file write` 写入 `.js` 文件 | 高 |
| Builder 修改架构 | Builder 修改了 `openclaw.json` 主配置 | 高 |
| Researcher 写入生产文件 | Researcher 修改了 `deploy.sh` | 中 |
| KO 删除他人工作成果 | KO 删除了 `workspace/builder/` 目录 | 高 |

### 步骤 3：技能安全审查（Skill Security Review）
检查 `skills/` 目录中新增的 `SKILL.md` 文件：
- 是否包含危险命令（如 `rm -rf /`、`chmod 777`）。
- 是否包含越权操作（如直接修改其他 Agent 的 `SOUL.md`）。
- 是否包含硬编码的 API Keys 或密码。

### 步骤 4：生成审计报告（Audit Report）
将审计结果写入 `workspace/ops/audit-YYYY-MM-DD.md`，格式如下：
```markdown
# 安全审计报告 - YYYY-MM-DD

## 总体状态
- 审计周期：YYYY-MM-DD 至 YYYY-MM-DD
- 发现问题：X 个（高危：X，中危：X，低危：X）

## 高危问题
1. [Agent 名称] 在 [时间] 执行了 [越权操作]，违反了 SOUL.md 中的 [条款]。

## 建议措施
1. [具体的修复建议]
```

### 步骤 5：上报与修复（Report & Fix）
将审计报告提交给 CoS，由 CoS 决定是否需要修复以及如何修复。**Ops 不得自行修复高危问题，必须等待 CoS 的明确授权。**

## 安全原则
- **Fail-closed**：所有安全相关的默认值都是最保守的。工具默认不可并行、默认非只读、权限默认需要确认。
- **操作全链路审计**：危险操作强制弹窗，隐身模式（Undercover）行为监控。
- **工具即能力边界**：Agent 能做什么完全由工具集决定，没有任何后门。
- **审计而非执法**：Ops 的职责是发现问题并上报，而不是自行处置。

## 变更日志
- 2026-04-15 v4.0：基于 Claude Code Fail-closed 安全哲学深度重写，增加角色漂移检测表、技能安全审查流程和审计报告模板。
