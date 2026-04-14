# 技能：OPT TAOR 引擎（Think-Act-Observe-Repeat）

## 简介
本技能为 Builder 和 Researcher 提供**标准化的复杂任务执行框架**，基于 Claude Code 源码中的核心运行机制。它确保 Agent 在遇到错误时能够自动捕获输出、分析原因并重试，而不是直接向用户报错。

## 适用角色
**Builder**（主要）、**Researcher**（次要）

## 触发条件
- 执行复杂的系统命令或多步骤脚本。
- 编写和调试代码，遇到编译或运行时错误。
- 进行深度的网页抓取或数据分析，遇到反爬虫拦截。
- 任何需要多步骤迭代才能完成的任务。

## 执行步骤

### 阶段一：Think（思考规划）
在执行任何操作前，先完成以下规划：
1. **明确目标**：用一句话描述任务的最终成功状态（Success Criteria）。
2. **拆解步骤**：将复杂任务拆解为 3-7 个原子化的可执行步骤。
3. **预判风险**：列出每个步骤可能出现的错误类型（如：网络超时、权限不足、依赖缺失）。

### 阶段二：Act（执行行动）
按照规划，调用底层工具执行具体操作。执行命令时必须捕获错误输出：
```bash
# 正确做法：添加错误捕获，将 stderr 合并到 stdout
npm install --save-dev typescript 2>&1 | tee /tmp/install.log
echo "Exit code: $?"
```

### 阶段三：Observe（观察结果）
仔细读取执行结果，判断是否成功：
- **成功标志**：Exit code 为 0，且输出内容符合预期。
- **失败标志**：Exit code 非 0，或输出中包含 `Error`、`FAILED`、`Exception` 等关键词。
- **关键原则**：绝不跳过错误信息，必须完整阅读错误日志。

### 阶段四：Repeat（重试循环）
如果任务未成功，按照以下策略重试：

| 错误类型 | 重试策略 |
|---|---|
| 网络超时 | 等待 5 秒后重试，最多 3 次 |
| 依赖缺失 | 先安装缺失依赖，再重试原命令 |
| 权限不足 | 使用 `sudo` 或切换到有权限的目录 |
| 语法错误 | 修改代码后重新执行 |
| 反爬虫拦截 | 切换 User-Agent 或搜索引擎后重试 |

**最大重试次数：3 次**。达到上限后，必须向 CTO 或 CoS 汇报详细的错误日志和已尝试的方案，绝不沉默失败。

## 注意事项与避坑指南
- **绝不静默失败**：遇到错误时，必须打印完整的错误信息，而不是只打印"失败"。
- **Fail-closed 原则**：在重试过程中，如果涉及危险操作（如删除文件、修改生产配置），必须暂停并请求 CoS 确认，绝不自动执行。
- **日志持久化**：对于重要任务，将执行日志写入 `workspace/{agent}/logs/YYYY-MM-DD.log` 文件，供 Ops 审计。

## 变更日志
- 2026-04-15 v4.0：基于 Claude Code 源码泄露事件深度重写，增加错误类型分类表和日志持久化要求。

---

## 完整示例：网站发布任务（TAOR 全流程）

```bash
#!/bin/bash
# TAOR 引擎示例：发布网站到 GitHub Pages

# === Phase 1: Think ===
echo "📋 分析任务..."
REPO="leixing333/opt-lobster-legion"
BRANCH="gh-pages"
SOURCE_DIR="./dist"
MAX_RETRIES=3
RETRY_COUNT=0

# 验证源目录存在
if [ ! -d "$SOURCE_DIR" ]; then
  echo "❌ 源目录不存在，先执行构建"
  npm run build 2>&1 | tee /tmp/build.log
  if [ $? -ne 0 ]; then
    echo "❌ 构建失败，上报给 CTO"
    exit 1
  fi
fi

# === Phase 2 + 3 + 4: Act → Observe → Repeat ===
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "🚀 第 $RETRY_COUNT 次尝试发布..."

  # Act：执行发布
  cd "$SOURCE_DIR"
  git init && git add . && git commit -m "Deploy $(date +%Y-%m-%d)"
  git push -f "https://$GITHUB_TOKEN@github.com/$REPO.git" HEAD:$BRANCH 2>&1 | tee /tmp/deploy.log
  EXIT_CODE=$?

  # Observe：检查结果
  if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 发布成功！"
    echo "🌐 网站地址: https://leixing333.github.io/opt-lobster-legion/"
    break
  else
    ERROR=$(cat /tmp/deploy.log | grep -i "error\|failed" | head -3)
    echo "❌ 第 $RETRY_COUNT 次失败: $ERROR"

    # Repeat：根据错误类型调整策略
    if echo "$ERROR" | grep -qi "network\|timeout"; then
      echo "🔄 网络错误，等待 5 秒后重试..."
      sleep 5
    elif echo "$ERROR" | grep -qi "permission\|403"; then
      echo "🔄 权限错误，检查 Token..."
      break  # 权限问题不重试，上报
    else
      echo "🔄 未知错误，尝试备用方案..."
    fi
  fi
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ] && [ $EXIT_CODE -ne 0 ]; then
  echo "❌ 已达到最大重试次数，上报给 CoS"
  # 写入错误日志供 Ops 审计
  cp /tmp/deploy.log "workspace/builder/logs/$(date +%Y-%m-%d)-deploy-error.log"
fi
```

---

## 完整示例：Python 数据处理任务

```python
#!/usr/bin/env python3
# TAOR 引擎示例：处理 CSV 数据

import sys
import time
import traceback

def taor_execute(task_fn, max_retries=3, retry_delay=2):
    """TAOR 引擎装饰器：自动重试，捕获错误"""
    
    for attempt in range(1, max_retries + 1):
        try:
            # Phase 2: Act
            print(f"🚀 第 {attempt} 次尝试...")
            result = task_fn()
            
            # Phase 3: Observe（成功）
            print(f"✅ 执行成功！")
            return result
            
        except FileNotFoundError as e:
            # Phase 3: Observe（文件不存在）
            print(f"❌ 文件不存在: {e}")
            if attempt < max_retries:
                print(f"🔄 创建目录后重试...")
                import os
                os.makedirs(os.path.dirname(str(e).split("'")[1]), exist_ok=True)
                
        except PermissionError as e:
            # Phase 3: Observe（权限错误）
            print(f"❌ 权限错误: {e}")
            print("🛑 权限问题需要人工介入，上报给 Ops")
            break  # 权限问题不重试
            
        except Exception as e:
            # Phase 3: Observe（未知错误）
            print(f"❌ 第 {attempt} 次失败: {type(e).__name__}: {e}")
            if attempt < max_retries:
                # Phase 4: Repeat
                print(f"🔄 等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print(f"❌ 已达到最大重试次数，完整错误信息：")
                traceback.print_exc()
                
    return None

# Phase 1: Think（在调用前规划）
def process_data():
    """实际的数据处理任务"""
    import pandas as pd
    df = pd.read_csv('data/input.csv')
    result = df.groupby('category').sum()
    result.to_csv('data/output.csv')
    return f"处理完成，共 {len(result)} 行"

# 执行
result = taor_execute(process_data)
if result:
    print(f"📊 结果: {result}")
```

---

## 与其他技能的协作

| 技能 | 协作方式 |
|---|---|
| `opt-skill-evolution` | 当 TAOR 循环发现了新的错误处理模式，通知 opt-skill-evolution 沉淀为新技能 |
| `opt-security-audit` | 所有 TAOR 执行日志都会被 Ops 的安全审计扫描，日志路径：`workspace/{agent}/logs/` |
| `opt-auto-backup` | 在执行不可逆操作前，先触发 opt-auto-backup 创建快照 |
| `opt-autodream-memory` | 每日 Auto Dream 会扫描 TAOR 日志，提炼常见错误模式到知识库 |
