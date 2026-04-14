# 技能：OPT 自动备份系统

## 简介
本技能为 Ops（运维审计员）提供**自动化系统备份**能力，确保整个 OPT 龙虾军团的配置文件、工作区和知识库可以随时恢复。实现"拷贝即升级"——在新设备上解压备份文件后，执行 `deploy.sh` 即可在 15 分钟内恢复完整的工作状态。

## 适用角色
**Ops**（主要）

## 触发条件
- 每天凌晨定时任务触发（推荐 03:00 AM）。
- 在执行重大系统变更（如升级 openclaw 版本、修改 openclaw.json）前手动触发。
- 在完成重要项目里程碑后手动触发。

## 执行步骤

### 步骤 1：创建备份目录（Prepare）
```bash
BACKUP_DATE=$(date +%Y-%m-%d)
BACKUP_DIR="./backups/opt-${BACKUP_DATE}"
mkdir -p "${BACKUP_DIR}"
echo "备份目录已创建：${BACKUP_DIR}"
```

### 步骤 2：备份核心文件（Backup）
备份以下核心目录和文件：

| 备份内容 | 源路径 | 重要性 |
|---|---|---|
| 系统主配置 | `openclaw.json` | 极高 |
| 环境变量模板 | `.env.example` | 高 |
| 所有 Agent 配置 | `agents/` | 极高 |
| 所有技能文件 | `skills/` | 极高 |
| 知识库 | `knowledge-base/` | 极高 |
| 共享协议 | `shared/` | 高 |
| 部署脚本 | `deploy.sh` | 高 |

```bash
# 打包核心文件（排除敏感的 .env 文件）
tar -czf "${BACKUP_DIR}/opt-system-${BACKUP_DATE}.tar.gz" \
  openclaw.json \
  .env.example \
  deploy.sh \
  agents/ \
  skills/ \
  knowledge-base/ \
  shared/ \
  --exclude="**/.env" \
  --exclude="**/node_modules" \
  --exclude="**/.git"

echo "备份文件已创建：${BACKUP_DIR}/opt-system-${BACKUP_DATE}.tar.gz"
```

### 步骤 3：验证备份完整性（Verify）
```bash
# 验证备份文件是否可以正常解压
tar -tzf "${BACKUP_DIR}/opt-system-${BACKUP_DATE}.tar.gz" | head -20
echo "备份文件验证通过，共包含 $(tar -tzf ${BACKUP_DIR}/opt-system-${BACKUP_DATE}.tar.gz | wc -l) 个文件"
```

### 步骤 4：推送到 GitHub（Remote Backup）
```bash
# 将备份文件推送到 GitHub 仓库
git add "backups/opt-${BACKUP_DATE}/"
git commit -m "backup: opt-system-${BACKUP_DATE}"
git push origin main
echo "备份已推送到 GitHub"
```

### 步骤 5：清理旧备份（Cleanup）
保留最近 7 天的备份，删除更早的备份：
```bash
find ./backups -name "opt-*" -type d -mtime +7 -exec rm -rf {} +
echo "旧备份已清理，保留最近 7 天"
```

## 恢复流程（拷贝即升级）
在新设备上恢复系统：
```bash
# 1. 克隆仓库
git clone https://github.com/leixing333/opt-lobster-legion.git
cd opt-lobster-legion

# 2. 解压最新备份
tar -xzf backups/opt-YYYY-MM-DD/opt-system-YYYY-MM-DD.tar.gz

# 3. 配置环境变量
cp .env.example .env && nano .env

# 4. 一键部署
./deploy.sh
```

## 注意事项与避坑指南
- **绝不备份 .env 文件**：`.env` 文件包含 API Keys 等敏感信息，绝不能提交到 Git 仓库。
- **验证后再推送**：在推送到 GitHub 前，必须先验证备份文件的完整性。
- **异地备份**：除了 GitHub，建议同时备份到本地外部硬盘，防止 GitHub 账号被封禁。

## 变更日志
- 2026-04-15 v4.0：深度重写，增加备份内容分类表、完整的命令示例和恢复流程。
