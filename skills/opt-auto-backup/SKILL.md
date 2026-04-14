# OPT 自动备份技能

## 技能描述
本技能为 Ops（运维审计员）提供一套标准的系统备份与恢复流程，确保 OPT 龙虾军团的所有配置、记忆和知识库能够安全备份，并在新设备上快速恢复（拷贝即升级）。

## 备份内容

| 备份项目 | 路径 | 频率 |
|---|---|---|
| Agent 配置文件 | `~/.openclaw/agents/` | 每天 |
| 技能文件 | `~/.openclaw/skills/` | 每天 |
| L1 记忆工作区 | `~/.openclaw/workspace/` | 每天 |
| L2 知识库 | `~/.openclaw/knowledge-base/` | 每天 |
| 主配置文件 | `~/.openclaw/openclaw.json` | 每次变更 |

## 备份流程

### 1. 创建备份
```bash
# 手动创建备份
openclaw backup create --label "opt-$(date +%Y-%m-%d)"

# 自动备份（由 Ops 定时任务触发，每天凌晨 3 点）
# 在 openclaw.json 中配置：
# "schedule": { "backup": "0 3 * * *" }
```

### 2. 恢复备份（拷贝即升级）
```bash
# 在新设备上恢复
git clone https://github.com/your-name/opt-lobster-legion.git
cd opt-lobster-legion
cp .env.example .env && nano .env  # 填入 API Keys
./deploy.sh

# 验证恢复结果
openclaw agents list   # 应显示 6 个 Agent
openclaw skills list   # 应显示 8 个技能
```

## 注意事项
`.env` 文件包含敏感的 API Keys，**绝对不能**提交到 GitHub 仓库。备份时应将 `.env` 排除在外（已在 `.gitignore` 中配置）。
