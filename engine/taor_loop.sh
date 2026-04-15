#!/bin/bash
# OPT v6.0 - TAOR Engine: Think-Act-Observe-Repeat Loop
# 基于 Claude Code 的 Agent Loop 设计，赋予 Agent 自动纠错能力

set -euo pipefail

MAX_RETRIES=3
RETRY_COUNT=0
LOG_DIR="${HOME}/workspace/memory/session/taor_logs"
mkdir -p "$LOG_DIR"

LOG_FILE="${LOG_DIR}/taor_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# THINK: 分析当前状态
think() {
    local task="$1"
    log "🤔 THINK: 分析任务 - $task"
    log "  当前目录: $(pwd)"
    log "  Node 版本: $(node --version 2>/dev/null || echo 'N/A')"
    log "  Git 状态: $(git status --short 2>/dev/null | head -5 || echo 'N/A')"
}

# ACT: 执行命令
act() {
    local cmd="$1"
    log "⚡ ACT: 执行 - $cmd"
    eval "$cmd"
}

# OBSERVE: 捕获输出
observe() {
    local cmd="$1"
    local output
    local exit_code
    
    output=$(eval "$cmd" 2>&1) && exit_code=0 || exit_code=$?
    
    log "👁️ OBSERVE: 退出码=$exit_code"
    if [ -n "$output" ]; then
        log "  输出: ${output:0:500}"
    fi
    
    echo "$exit_code:$output"
}

# TAOR 主循环
taor_execute() {
    local task_name="$1"
    local command="$2"
    
    think "$task_name"
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        log "🔄 REPEAT: 第 $((RETRY_COUNT + 1)) 次尝试"
        
        result=$(observe "$command")
        exit_code="${result%%:*}"
        output="${result#*:}"
        
        if [ "$exit_code" -eq 0 ]; then
            log "✅ 成功完成: $task_name"
            return 0
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            log "❌ 失败 (第 $RETRY_COUNT 次): $output"
            
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                log "🔧 调整策略并重试..."
                sleep $((RETRY_COUNT * 2))  # 指数退避
            fi
        fi
    done
    
    # TAOR 循环耗尽 - 触发 Escalation
    log "🚨 ESCALATION: TAOR 循环耗尽 ($MAX_RETRIES 次重试均失败)"
    log "  任务: $task_name"
    log "  最后错误: $output"
    log "  请 CoS 介入处理"
    
    # 写入 Escalation 文件
    ESCALATION_FILE="${HOME}/workspace/memory/workspace/escalations/$(date +%Y%m%d_%H%M%S)_${task_name// /_}.md"
    mkdir -p "$(dirname "$ESCALATION_FILE")"
    cat > "$ESCALATION_FILE" << EOF
# Escalation Report

**时间**: $(date '+%Y-%m-%d %H:%M:%S')
**任务**: $task_name
**命令**: $command
**重试次数**: $MAX_RETRIES
**最后错误**: $output
**日志文件**: $LOG_FILE

## 建议处理方式
1. 检查环境变量配置是否正确
2. 确认依赖版本是否兼容
3. 查看完整日志文件获取详细信息
EOF
    
    return 1
}

# 示例用法
# taor_execute "前端构建" "cd /home/ubuntu/workspace/frontend && npm run build"
# taor_execute "数据库迁移" "cd /home/ubuntu/workspace/backend && npm run db:migrate"

# 如果直接运行脚本，接受参数
if [ $# -ge 2 ]; then
    taor_execute "$1" "$2"
fi
