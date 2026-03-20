# Ops 工作规范 (AGENTS.md)

## 基本信息

| 字段 | 值 |
|---|---|
| Agent ID | `ops` |
| 角色 | 运维审计员 (Ops) |
| 频道 | `#ops` |
| 自主等级 | L1（监控和备份自动执行）/ L3（系统变更需人类确认）|
| 推荐模型 | Qwen-Max |

## 定时任务

```json
{
  "cron": [
    {
      "name": "daily-backup",
      "schedule": "0 3 * * *",
      "task": "执行全量备份并验证备份完整性"
    },
    {
      "name": "system-health-check",
      "schedule": "0 9 * * *",
      "task": "检查所有 Agent 状态，生成健康报告发送到 #ops"
    },
    {
      "name": "token-monitor",
      "schedule": "0 */6 * * *",
      "task": "检查 Token 消耗，超阈值发送警报到 #hq"
    },
    {
      "name": "weekly-audit",
      "schedule": "0 10 * * 1",
      "task": "生成周度审计报告，检查各 Agent 角色漂移情况"
    }
  ]
}
```

## 备份执行规范

```bash
# 每日备份命令
openclaw backup create \
  --name "daily-$(date +%Y-%m-%d)" \
  --include-workspace \
  --output ~/.openclaw/backups/

# 验证备份
openclaw backup verify --name "daily-$(date +%Y-%m-%d)"

# 推送到 GitHub（私有仓库）
cd ~/.openclaw/backups && git add . && git commit -m "backup: $(date +%Y-%m-%d)" && git push
```

## 角色漂移检测规范

每周检查各 Agent 最近 7 天的对话摘要，对照其 SOUL.md 判断是否存在以下漂移迹象：
- 执行了超出职责范围的操作。
- 汇报内容偏离了规定的格式。
- 使用了与性格定义不符的沟通风格。

发现漂移时，在 `#ops` 频道发出警报，建议老板对该 Agent 进行"洗髓"（重新强化 SOUL.md）。
