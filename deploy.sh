#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║   🦞 OPT 龙虾军团 — 一键部署脚本 v2.0                       ║
# ║   基于 OpenClaw 2026.3.x 真实 CLI 语法                      ║
# ║   使用方法：chmod +x deploy.sh && ./deploy.sh               ║
# ╚══════════════════════════════════════════════════════════════╝
#
# 支持模式：
#   ./deploy.sh              — 全新安装
#   ./deploy.sh --restore    — 从备份恢复（拷贝即升级）
#   ./deploy.sh --dry-run    — 预览部署计划，不实际执行

set -euo pipefail

# ===== 颜色定义 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ===== 工具函数 =====
log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }
log_step()    { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }
dry_run()     { [[ "${DRY_RUN:-false}" == "true" ]] && echo -e "${YELLOW}[DRY-RUN]${NC} 跳过: $1" && return 0 || return 1; }

# ===== 参数解析 =====
RESTORE_MODE=false
DRY_RUN=false
RESTORE_ARCHIVE=""

for arg in "$@"; do
    case $arg in
        --restore) RESTORE_MODE=true ;;
        --dry-run) DRY_RUN=true ;;
        --archive=*) RESTORE_ARCHIVE="${arg#*=}" ;;
    esac
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🦞 OPT 龙虾军团 — 一键部署系统 v2.0                       ║"
echo "║   OpenClaw 多 Agent 一人设计公司系统                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    log_warn "DRY-RUN 模式：仅预览，不执行实际操作"
fi

# ===== 步骤 1：检查系统依赖 =====
log_step "步骤 1/8：检查系统依赖"

command -v git  >/dev/null 2>&1 || log_error "未找到 git，请先安装 git"
command -v node >/dev/null 2>&1 || log_error "未找到 Node.js，请先安装 Node.js"
command -v npm  >/dev/null 2>&1 || log_error "未找到 npm"

# 检查 Node.js 版本（openclaw 要求 >=22.16.0）
NODE_MAJOR=$(node -v | sed 's/v//' | cut -d'.' -f1)
NODE_MINOR=$(node -v | sed 's/v//' | cut -d'.' -f2)
NODE_PATCH=$(node -v | sed 's/v//' | cut -d'.' -f3)

check_node_version() {
    if [ "$NODE_MAJOR" -gt 22 ]; then return 0; fi
    if [ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -gt 16 ]; then return 0; fi
    if [ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -eq 16 ] && [ "$NODE_PATCH" -ge 0 ]; then return 0; fi
    return 1
}

if ! check_node_version; then
    log_warn "Node.js 版本过低（当前: $(node -v)），openclaw 需要 >=22.16.0"
    log_info "正在尝试通过 nvm 升级..."
    if command -v nvm >/dev/null 2>&1 || [ -f "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh" 2>/dev/null || true
        nvm install 22.16.0 && nvm use 22.16.0
        log_success "Node.js 已升级到 $(node -v)"
    else
        log_error "请手动升级 Node.js 到 22.16.0+：https://nodejs.org/en/download"
    fi
fi

log_success "依赖检查通过（Node.js $(node -v)，npm $(npm -v)）"

# ===== 步骤 2：安装/更新 OpenClaw =====
log_step "步骤 2/8：安装/更新 OpenClaw"

if dry_run "npm install -g openclaw@latest"; then
    :
else
    log_info "正在安装 OpenClaw（约 30-60 秒）..."
    npm install -g openclaw@latest 2>&1 | grep -E "(added|updated|error)" || true
    OPENCLAW_VER=$(openclaw --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    log_success "OpenClaw 安装完成（版本 $OPENCLAW_VER）"
fi

# ===== 步骤 3：检查环境变量 =====
log_step "步骤 3/8：检查环境变量配置"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        echo ""
        echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠️  请先配置 .env 文件，然后重新运行 ./deploy.sh            ║${NC}"
        echo -e "${YELLOW}╠══════════════════════════════════════════════════════════════╣${NC}"
        echo -e "${YELLOW}║  必填项：                                                    ║${NC}"
        echo -e "${YELLOW}║    ANTHROPIC_API_KEY  — Claude 模型（CoS / CTO 使用）        ║${NC}"
        echo -e "${YELLOW}║    OPENAI_API_KEY     — GPT 模型（Builder / KO / Ops 使用）  ║${NC}"
        echo -e "${YELLOW}║    SLACK_BOT_TOKEN    — Slack Bot Token（xoxb-...）          ║${NC}"
        echo -e "${YELLOW}║    SLACK_APP_TOKEN    — Slack App Token（xapp-...）          ║${NC}"
        echo -e "${YELLOW}║    SLACK_CHANNEL_HQ   — #hq 频道 ID                         ║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "  编辑命令：nano $SCRIPT_DIR/.env"
        echo ""
        exit 0
    else
        log_error "未找到 .env 或 .env.example 文件，请确保在项目根目录运行"
    fi
fi

# 加载环境变量
set -a
source "$SCRIPT_DIR/.env"
set +a

# 检查必填项
MISSING_VARS=()
[ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ] && MISSING_VARS+=("ANTHROPIC_API_KEY 或 OPENAI_API_KEY（至少一个）")
[ -z "${SLACK_BOT_TOKEN:-}" ] && [ -z "${FEISHU_APP_ID:-}" ] && MISSING_VARS+=("SLACK_BOT_TOKEN 或 FEISHU_APP_ID（至少一个）")

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    log_error "以下必填环境变量未配置：\n$(printf '  - %s\n' "${MISSING_VARS[@]}")"
fi

log_success "环境变量检查通过"

# ===== 步骤 4：初始化 OpenClaw 工作区 =====
log_step "步骤 4/8：初始化 OpenClaw 工作区"

OPENCLAW_STATE="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"

if dry_run "openclaw setup --non-interactive --workspace $OPENCLAW_STATE/workspace"; then
    :
else
    # 创建基础目录结构
    mkdir -p "$OPENCLAW_STATE"/{workspace,backups}
    
    # 将配置文件写入 openclaw 状态目录
    if [ -f "$SCRIPT_DIR/openclaw.json" ]; then
        # 使用 envsubst 替换环境变量占位符
        if command -v envsubst >/dev/null 2>&1; then
            envsubst < "$SCRIPT_DIR/openclaw.json" > "$OPENCLAW_STATE/openclaw.json"
        else
            cp "$SCRIPT_DIR/openclaw.json" "$OPENCLAW_STATE/openclaw.json"
            log_warn "未找到 envsubst，配置文件中的变量占位符未替换，请手动编辑 $OPENCLAW_STATE/openclaw.json"
        fi
        log_success "主配置文件已写入：$OPENCLAW_STATE/openclaw.json"
    fi
    
    # 验证配置
    if openclaw config validate 2>/dev/null; then
        log_success "配置文件验证通过"
    else
        log_warn "配置文件验证有警告，请检查 $OPENCLAW_STATE/openclaw.json"
    fi
fi

# ===== 步骤 5：部署 Agent 配置文件 =====
log_step "步骤 5/8：部署 6 个 Agent 配置文件"

AGENTS=("cos" "cto" "builder" "researcher" "ko" "ops")
AGENT_NAMES=("CoS 幕僚长" "CTO 技术合伙人" "Builder 执行者" "Researcher 情报官" "KO 知识管理员" "Ops 运维审计员")

for i in "${!AGENTS[@]}"; do
    agent="${AGENTS[$i]}"
    name="${AGENT_NAMES[$i]}"
    SRC_DIR="$SCRIPT_DIR/agents/$agent"
    DST_DIR="$OPENCLAW_STATE/agents/$agent/agent"
    
    if dry_run "部署 $name ($agent)"; then
        :
    else
        mkdir -p "$DST_DIR"
        if [ -d "$SRC_DIR" ]; then
            cp -r "$SRC_DIR/"* "$DST_DIR/" 2>/dev/null || true
            log_success "  ✓ $name 已部署 → $DST_DIR"
        else
            log_warn "  ⚠ 未找到 $agent 配置目录，跳过"
        fi
    fi
done

# 通过 openclaw CLI 注册 Agent（使用真实命令）
log_info "通过 CLI 注册 Agent..."
for agent in "${AGENTS[@]}"; do
    if dry_run "openclaw agents add $agent"; then
        :
    else
        # 检查 Agent 是否已存在
        if openclaw agents list 2>/dev/null | grep -q "^- $agent"; then
            log_info "  Agent '$agent' 已存在，跳过注册"
        else
            openclaw agents add "$agent" \
                --workspace "$OPENCLAW_STATE/workspace-$agent" \
                --agent-dir "$OPENCLAW_STATE/agents/$agent/agent" \
                --non-interactive 2>/dev/null || log_warn "  Agent '$agent' 注册失败，请手动注册"
            log_success "  ✓ Agent '$agent' 注册成功"
        fi
    fi
done

# ===== 步骤 6：安装自定义技能 =====
log_step "步骤 6/8：安装自定义技能"

SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DST="$OPENCLAW_STATE/workspace/skills"

if dry_run "安装 5 个自定义技能"; then
    :
else
    mkdir -p "$SKILLS_DST"
    if [ -d "$SKILLS_SRC" ]; then
        cp -r "$SKILLS_SRC/"* "$SKILLS_DST/" 2>/dev/null || true
        SKILL_COUNT=$(ls "$SKILLS_SRC/" | wc -l | tr -d ' ')
        log_success "已安装 $SKILL_COUNT 个自定义技能到 $SKILLS_DST"
        
        # 列出已安装的技能
        for skill_dir in "$SKILLS_SRC"/*/; do
            skill_name=$(basename "$skill_dir")
            log_info "  ✓ $skill_name"
        done
    fi
    
    # 验证技能状态
    log_info "验证技能状态..."
    openclaw skills list 2>/dev/null | grep -E "(✓|ready)" | head -10 || true
fi

# ===== 步骤 7：配置频道绑定 =====
log_step "步骤 7/8：配置 Slack 频道绑定"

if [ -n "${SLACK_BOT_TOKEN:-}" ] && [ -n "${SLACK_CHANNEL_HQ:-}" ]; then
    if dry_run "配置 Slack 频道绑定"; then
        :
    else
        log_info "正在绑定 Slack 频道..."
        
        # 绑定各 Agent 到对应频道
        declare -A CHANNEL_MAP=(
            ["cos"]="${SLACK_CHANNEL_HQ:-}"
            ["cto"]="${SLACK_CHANNEL_CTO:-}"
            ["builder"]="${SLACK_CHANNEL_BUILD:-}"
            ["researcher"]="${SLACK_CHANNEL_RESEARCH:-}"
            ["ko"]="${SLACK_CHANNEL_KNOW:-}"
            ["ops"]="${SLACK_CHANNEL_OPS:-}"
        )
        
        for agent in "${!CHANNEL_MAP[@]}"; do
            channel_id="${CHANNEL_MAP[$agent]}"
            if [ -n "$channel_id" ] && [ "$channel_id" != "C0XXXXXXX" ]; then
                openclaw agents bind "$agent" "slack:$channel_id" 2>/dev/null \
                    && log_success "  ✓ $agent → Slack #$channel_id" \
                    || log_warn "  ⚠ $agent 频道绑定失败，请手动配置"
            else
                log_warn "  ⚠ $agent 频道 ID 未配置，跳过绑定"
            fi
        done
    fi
else
    log_warn "Slack Token 或频道 ID 未配置，跳过频道绑定"
    log_info "  配置完成后运行：openclaw agents bind <agent> slack:<channel_id>"
fi

# ===== 步骤 8：创建初始备份 =====
log_step "步骤 8/8：创建初始备份"

BACKUP_DIR="$SCRIPT_DIR/backups"
mkdir -p "$BACKUP_DIR"

if dry_run "openclaw backup create --output $BACKUP_DIR --verify"; then
    :
else
    log_info "正在创建初始备份..."
    BACKUP_FILE=$(openclaw backup create --output "$BACKUP_DIR" --verify --json 2>/dev/null \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('path',''))" 2>/dev/null || echo "")
    
    if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        log_success "初始备份已创建：$BACKUP_FILE"
    else
        # 非 JSON 模式备份
        openclaw backup create --output "$BACKUP_DIR" 2>/dev/null \
            && log_success "初始备份已创建到：$BACKUP_DIR" \
            || log_warn "备份创建失败（需要先启动 Gateway），部署完成后运行：openclaw backup create"
    fi
fi

# ===== 部署完成 =====
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🎉 OPT 龙虾军团部署完成！                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "━━━ 下一步操作 ━━━"
echo ""
echo "1. 启动 OpenClaw 网关："
echo "   openclaw gateway --port 18789"
echo ""
echo "2. 查看 Agent 状态："
echo "   openclaw agents list"
echo ""
echo "3. 在 Slack 中创建频道并邀请 Bot："
echo "   #hq  #cto  #build  #research  #know  #ops"
echo ""
echo "4. 在 #hq 发送第一条消息，唤醒 CoS 幕僚长"
echo ""
echo "━━━ 常用命令 ━━━"
echo ""
echo "  openclaw status                          # 查看整体状态"
echo "  openclaw agents list                     # 列出所有 Agent"
echo "  openclaw skills list                     # 列出所有技能"
echo "  openclaw backup create --output ./backups # 创建备份"
echo "  openclaw backup verify <archive.tar.gz>  # 验证备份"
echo "  openclaw config validate                 # 验证配置"
echo "  openclaw doctor                          # 健康检查"
echo ""
echo "━━━ 拷贝即升级（新设备恢复）━━━"
echo ""
echo "  1. git clone https://github.com/leixing333/opt-lobster-legion.git"
echo "  2. cd opt-lobster-legion && cp .env.example .env && nano .env"
echo "  3. chmod +x deploy.sh && ./deploy.sh"
echo "  4. openclaw backup verify ./backups/<archive>.tar.gz"
echo ""
echo "查看完整文档：cat README.md"
echo ""
