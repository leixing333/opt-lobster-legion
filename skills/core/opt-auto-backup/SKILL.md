# SKILL: opt-auto-backup — 自动备份技能

## 1. 技能简介

本技能实现 OPT 系统的**全量自动备份**与**增量快照**机制，确保系统状态可随时恢复。备份策略遵循 3-2-1 原则：3 份副本、2 种介质、1 份异地（GitHub）。

## 2. 适用场景

- Ops 执行每日自动备份任务。
- 重大变更前的手动快照。
- 新设备恢复（拷贝即升级）。
- 技能库、Agent 配置、知识库的版本管理。

## 3. 备份脚本

```bash
#!/bin/bash
# OPT v6.0 - 自动备份脚本
# 由 Ops 每日执行

set -euo pipefail

WORKSPACE="${OPT_WORKSPACE:-$HOME/workspace}"
BACKUP_DIR="${OPT_BACKUP_DIR:-$HOME/opt-backups}"
OPENCLAW_DIR="${HOME}/.openclaw"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="opt-backup-${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}"

echo "🔒 开始备份 — ${TIMESTAMP}"

# 1. 备份 openclaw 配置
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}-config.tar.gz" \
    --exclude="*.log" \
    --exclude="session/" \
    "${OPENCLAW_DIR}/" 2>/dev/null
echo "  ✓ openclaw 配置备份完成"

# 2. 备份工作区记忆（排除临时文件）
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}-memory.tar.gz" \
    --exclude="session/" \
    --exclude="*.tmp" \
    "${WORKSPACE}/memory/" 2>/dev/null
echo "  ✓ 记忆系统备份完成"

# 3. 推送到 GitHub（异地备份）
if [ -n "${GITHUB_TOKEN:-}" ] && [ -d "${WORKSPACE}/.git" ]; then
    cd "${WORKSPACE}"
    git add -A && git commit -m "auto-backup: ${TIMESTAMP}" --allow-empty
    git push origin main 2>/dev/null
    echo "  ✓ GitHub 异地备份完成"
fi

# 4. 清理 30 天前的旧备份
find "${BACKUP_DIR}" -name "opt-backup-*.tar.gz" -mtime +30 -delete
echo "  ✓ 旧备份清理完成"

echo "✅ 备份完成: ${BACKUP_DIR}/${BACKUP_NAME}-*.tar.gz"
```

## 4. 恢复命令

```bash
# 从最新备份恢复
LATEST=$(ls -t ~/opt-backups/opt-backup-*-config.tar.gz | head -1)
tar -xzf "${LATEST}" -C ~/

# 从 GitHub 恢复（新设备）
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion && ./deploy.sh
```

## 5. 变更日志

- 2026-04-16: v1.0 初始版本，3-2-1 备份策略
