# SKILL: TAOR Engine (Think-Act-Observe-Repeat)

## 1. 技能简介
本技能是 OPT 龙虾军团 v6.0 的核心执行引擎，基于 Claude Code 的 TAOR 循环设计。
它赋予 Agent（特别是 BE 和 FE）自动纠错的能力，确保在遇到错误时不会直接崩溃，而是通过闭环反馈进行自我修复。

## 2. 核心机制

### 2.1 循环控制 (Agent Loop)
TAOR 引擎通过一个严格的四步循环来执行任务：
1. **Think**：分析当前状态，决定下一步行动。
2. **Act**：执行命令或修改代码。
3. **Observe**：捕获终端输出或错误日志。
4. **Repeat**：如果失败，根据错误日志调整策略并重试（最多 3 次）。

### 2.2 异常捕获与重试
- 所有的命令执行必须捕获标准输出（stdout）和标准错误（stderr）。
- 如果命令返回非零退出码，必须进入重试逻辑。
- 每次重试前，必须分析错误原因，并调整执行策略。

## 3. 执行脚本示例

### 3.1 Bash 脚本示例 (taor_loop.sh)
```bash
#!/bin/bash

# TAOR 循环执行器
MAX_RETRIES=3
RETRY_COUNT=0

execute_command() {
    local cmd="$1"
    echo "Executing: $cmd"
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        # Act & Observe
        output=$(eval "$cmd" 2>&1)
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "Success: $output"
            return 0
        else
            echo "Error: $output"
            echo "Retrying... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
            RETRY_COUNT=$((RETRY_COUNT + 1))
            # Think: 在这里可以加入 LLM 调用来分析错误并调整命令
            sleep 2
        fi
    done
    
    echo "Failed after $MAX_RETRIES retries."
    return 1
}

# 示例调用
execute_command "npm run build"
```

## 4. 协作与升级 (Escalation)
- 如果 TAOR 循环耗尽（重试 3 次仍失败），必须触发升级流程。
- 将错误日志和已尝试的解决方案打包，向上级（CTO 或 CoS）汇报。
- 禁止静默失败，所有错误必须记录。
