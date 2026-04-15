# opt-taor-engine: TAOR 引擎执行框架

## 1. 技能简介

`opt-taor-engine` 是 OPT 龙虾军团 v5.0 的核心执行框架，基于 Claude Code 的 TAOR（Think-Act-Observe-Repeat）循环理念设计。
它不是一个简单的脚本，而是一种**防御性编程范式**。当 Builder 或 Researcher 执行复杂任务时，必须通过此引擎进行，以确保错误被自动捕获和重试，而不是直接导致任务失败。

## 2. 核心机制（Harness 层）

- **Think（思考）**：在执行前，强制要求 Agent 输出执行计划和预期结果。
- **Act（行动）**：通过受控的子进程执行命令或代码。
- **Observe（观察）**：自动捕获 `stdout`、`stderr` 和退出状态码（Exit Code）。
- **Repeat（重试）**：如果 Exit Code 不为 0，引擎会拦截错误，将错误日志反馈给 Agent，要求其分析原因并提供新的解决方案，直到成功或达到最大重试次数（默认 3 次）。

## 3. 执行脚本示例

### 3.1 Bash 封装器 (`taor_runner.sh`)

Builder 在执行复杂的 Shell 命令（如部署、构建）时，应使用此封装器：

```bash
#!/bin/bash
# taor_runner.sh - TAOR 引擎 Bash 封装器

MAX_RETRIES=3
COMMAND="$@"
ATTEMPT=1

while [ $ATTEMPT -le $MAX_RETRIES ]; do
    echo "[TAOR] Attempt $ATTEMPT: Executing '$COMMAND'"
    
    # 执行命令并捕获输出
    OUTPUT=$(eval "$COMMAND" 2>&1)
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[TAOR] Success!"
        echo "$OUTPUT"
        exit 0
    else
        echo "[TAOR] Error (Exit Code: $EXIT_CODE)"
        echo "--- Error Log ---"
        echo "$OUTPUT"
        echo "-----------------"
        
        if [ $ATTEMPT -eq $MAX_RETRIES ]; then
            echo "[TAOR] Max retries reached. Escalating to CTO."
            exit $EXIT_CODE
        fi
        
        # 提示 Agent 分析错误并重试
        echo "[TAOR] Please analyze the error log above and provide a fix for the next attempt."
        # 在实际运行中，这里会暂停并等待 Agent 的新输入
        read -p "Press Enter to retry or Ctrl+C to abort..."
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done
```

### 3.2 Python 装饰器 (`taor_engine.py`)

在编写 Python 脚本时，可以使用此装饰器实现自动重试：

```python
import traceback
import time
from functools import wraps

def taor_retry(max_retries=3, delay=2):
    """
    TAOR 引擎 Python 装饰器
    捕获异常，打印详细 Traceback，并自动重试。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_retries:
                try:
                    print(f"[TAOR] Attempt {attempt}: Executing {func.__name__}")
                    result = func(*args, **kwargs)
                    print(f"[TAOR] Success!")
                    return result
                except Exception as e:
                    print(f"[TAOR] Error on attempt {attempt}: {str(e)}")
                    print("--- Traceback ---")
                    traceback.print_exc()
                    print("-----------------")
                    
                    if attempt == max_retries:
                        print("[TAOR] Max retries reached. Escalating to CTO.")
                        raise e
                    
                    print(f"[TAOR] Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

# 使用示例
@taor_retry(max_retries=3)
def fetch_data(url):
    import requests
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()
```

## 4. 协作与触发

- **触发者**：Builder（执行代码/命令）、Researcher（抓取数据）。
- **前置条件**：任务具有不确定性（如网络请求、编译构建、依赖安装）。
- **升级机制**：当 TAOR 循环达到最大重试次数仍失败时，必须触发 A2A 协议，向 CTO 汇报错误日志，请求架构层面的指导。
