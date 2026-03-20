---
name: opt-auto-backup
description: OPT 公司自动备份技能。定时备份所有 Agent 配置、工作区和知识库，支持 GitHub 远程备份和一键恢复。
user-invocable: true
---

# OPT 自动备份技能

## 功能说明

此技能为 OPT 龙虾军团提供完整的备份和恢复能力，确保"拷贝即升级"的可移植性。

## 备份策略

| 备份类型 | 频率 | 保留时间 | 存储位置 |
|---|---|---|---|
| 每日全量备份 | 每天 03:00 | 30 天 | 本地 + GitHub |
| 每周快照 | 每周一 02:00 | 3 个月 | GitHub |
| 项目里程碑备份 | 手动触发 | 永久 | GitHub |

## 备份内容清单

```
opt-backup-{YYYY-MM-DD}/
├── config/
│   └── openclaw.json          # 主配置文件
├── agents/
│   ├── cos/
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   ├── MEMORY.md
│   │   └── memory/            # 日记忆文件
│   ├── cto/  ...
│   ├── builder/  ...
│   ├── researcher/  ...
│   ├── ko/  ...
│   └── ops/  ...
├── skills/                    # 所有自定义技能
├── knowledge-base/            # 知识库
└── workspace/
    ├── projects/              # 项目文件
    └── deliverables/          # 交付物
```

## 执行备份

```bash
# 手动执行全量备份
openclaw backup create \
  --name "opt-$(date +%Y-%m-%d)" \
  --include-workspace \
  --output ~/.openclaw/backups/

# 验证备份完整性
openclaw backup verify --name "opt-$(date +%Y-%m-%d)"

# 查看备份列表
openclaw backup list

# 推送到 GitHub 私有仓库
cd ~/.openclaw/backups
git add .
git commit -m "backup: $(date +%Y-%m-%d %H:%M)"
git push origin main
```

## 恢复流程

```bash
# 从备份恢复（先 dry-run 确认）
openclaw backup restore --name "opt-2026-03-19" --dry-run

# 确认无误后执行恢复
openclaw backup restore --name "opt-2026-03-19"

# 重启网关
openclaw gateway restart
```

## "拷贝即升级"操作指南

要在新设备上部署完整的 OPT 龙虾军团：

1. 在新设备安装 OpenClaw：`npm install -g openclaw@latest`
2. 克隆备份仓库：`git clone https://github.com/{你的用户名}/opt-backup.git ~/.openclaw/backups`
3. 恢复最新备份：`openclaw backup restore --name $(ls ~/.openclaw/backups | tail -1)`
4. 配置环境变量（API Keys）
5. 启动网关：`openclaw gateway --install-daemon`
6. 验证所有 Agent 正常运行：`openclaw agents list --bindings`

整个过程约 15 分钟，新设备即可拥有与原设备完全相同的龙虾军团。
