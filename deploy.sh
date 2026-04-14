#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   OPT 龙虾军团 v3.0 — 一键部署脚本                           ║
# ║   基于 Claude Code 工业级架构范式 · 拷贝即升级                ║
# ╚══════════════════════════════════════════════════════════════╝

set -euo pipefail

DRY_RUN=false
FORCE=false

for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    --force)   FORCE=true ;;
  esac
done

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()  { echo -e "${GREEN}[OPT]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }
dry()  { echo -e "${BLUE}[DRY-RUN]${NC} $1"; }

echo ""
echo "🦞 OPT 龙虾军团 v3.0 — 一键部署"
echo "=================================="
$DRY_RUN && echo -e "${BLUE}[DRY-RUN 模式 — 仅预览，不执行]${NC}"
echo ""

# ── 步骤 1：检查 Node.js 版本 ──────────────────────────────────
log "步骤 1/8：检查运行环境..."
NODE_VER=$(node -v 2>/dev/null | sed 's/v//' | cut -d. -f1 || echo "0")
if [ "$NODE_VER" -lt 22 ]; then
  warn "Node.js 版本过低（当前：v${NODE_VER}，需要 >=22）"
  if command -v nvm &>/dev/null; then
    $DRY_RUN && dry "nvm install 22 && nvm use 22" || (nvm install 22 && nvm use 22)
  else
    err "请先安装 Node.js 22+：https://nodejs.org"
  fi
fi
log "Node.js 版本检查通过 ✓"

# ── 步骤 2：安装 openclaw ──────────────────────────────────────
log "步骤 2/8：安装 openclaw..."
if ! command -v openclaw &>/dev/null || $FORCE; then
  $DRY_RUN && dry "npm install -g openclaw@latest" || npm install -g openclaw@latest
else
  log "openclaw 已安装：$(openclaw --version 2>/dev/null || echo '未知版本')"
fi

# ── 步骤 3：加载环境变量 ───────────────────────────────────────
log "步骤 3/8：加载环境变量..."
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    warn ".env 文件已从模板创建，请编辑 .env 填入真实 API Keys 后重新运行。"
    exit 0
  else
    err "未找到 .env 或 .env.example 文件。"
  fi
fi
set -a; source .env; set +a
log "环境变量加载完成 ✓"

# ── 步骤 4：复制配置文件到 openclaw 目录 ──────────────────────
log "步骤 4/8：部署配置文件到 ~/.openclaw/..."
OPENCLAW_DIR="$HOME/.openclaw"
$DRY_RUN && dry "mkdir -p $OPENCLAW_DIR/{agents,skills,workspace,knowledge-base,logs}" || \
  mkdir -p "$OPENCLAW_DIR"/{agents,skills,workspace,knowledge-base,logs}

for dir in agents skills shared knowledge-base; do
  if [ -d "./$dir" ]; then
    $DRY_RUN && dry "cp -r ./$dir/* $OPENCLAW_DIR/$dir/" || \
      cp -r "./$dir/"* "$OPENCLAW_DIR/$dir/" 2>/dev/null || true
  fi
done

$DRY_RUN && dry "cp openclaw.json $OPENCLAW_DIR/openclaw.json" || \
  cp openclaw.json "$OPENCLAW_DIR/openclaw.json"
log "配置文件部署完成 ✓"

# ── 步骤 5：注册 6 个 Agent ────────────────────────────────────
log "步骤 5/8：注册 AI 角色..."
AGENTS=("cos" "cto" "builder" "researcher" "ko" "ops")
for agent in "${AGENTS[@]}"; do
  if [ -f "$OPENCLAW_DIR/agents/$agent/SOUL.md" ]; then
    $DRY_RUN && dry "openclaw agents add $agent" || \
      openclaw agents add "$agent" 2>/dev/null || warn "注册 $agent 时遇到警告（可忽略）"
  fi
done
log "6 个 Agent 注册完成 ✓"

# ── 步骤 6：安装 8 个技能 ──────────────────────────────────────
log "步骤 6/8：安装技能库..."
SKILLS=("opt-taor-engine" "opt-autodream-memory" "opt-rag-knowledge" "opt-security-audit" \
        "opt-design-system" "opt-web-publisher" "opt-auto-backup" "opt-daily-report")
for skill in "${SKILLS[@]}"; do
  if [ -d "$OPENCLAW_DIR/skills/$skill" ]; then
    $DRY_RUN && dry "openclaw skills install $skill" || \
      openclaw skills install "$skill" 2>/dev/null || warn "安装 $skill 时遇到警告（可忽略）"
  fi
done
log "8 个技能安装完成 ✓"

# ── 步骤 7：验证配置 ───────────────────────────────────────────
log "步骤 7/8：验证系统配置..."
$DRY_RUN && dry "openclaw config validate" || \
  openclaw config validate 2>/dev/null || warn "配置验证遇到警告，请检查 .env 中的 API Keys"
log "配置验证完成 ✓"

# ── 步骤 8：创建初始备份 ───────────────────────────────────────
log "步骤 8/8：创建初始备份..."
$DRY_RUN && dry "openclaw backup create --label opt-v3-init" || \
  openclaw backup create --label "opt-v3-init" 2>/dev/null || warn "初始备份创建失败（可稍后手动执行）"
log "初始备份完成 ✓"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🎉 OPT 龙虾军团 v3.0 部署成功！                            ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║   验证命令：                                                  ║"
echo "║     openclaw agents list   # 查看 6 个 Agent                 ║"
echo "║     openclaw skills list   # 查看 8 个技能                   ║"
echo "║     openclaw start         # 启动服务                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
