# opt-autodream-memory: Auto Dream 记忆巩固

## 1. 技能简介

`opt-autodream-memory` 是 OPT 龙虾军团 v5.0 的核心记忆管理技能，基于 Claude Code 的 Auto Dream 机制设计。
它负责在系统空闲时（如夜间），自动扫描工作区中的临时文件、日志和对话摘要，提炼出具有长期价值的知识（如架构模式、错误解决方案），并将其归档到知识库中。

## 2. 核心机制（Harness 层）

- **扫描（Scan）**：遍历 `workspace/` 目录下的所有 `.log`、`.md` 和 `.txt` 文件。
- **提炼（Extract）**：使用 LLM 提取文件中的关键信息，过滤掉冗余的中间过程。
- **分类（Classify）**：将提炼出的知识分类为 `patterns`（架构模式）、`errors`（错误解决方案）或 `principles`（设计原则）。
- **归档（Archive）**：将分类后的知识写入 `knowledge-base/` 的对应子目录中。

## 3. 执行脚本示例

### 3.1 Bash 自动化脚本 (`autodream.sh`)

KO（知识管理员）可以定期执行此脚本来完成记忆巩固：

```bash
#!/bin/bash
# autodream.sh - Auto Dream 记忆巩固脚本

WORKSPACE_DIR="workspace"
KB_DIR="knowledge-base"
LOG_FILE="workspace/ko/autodream.log"

echo "[Auto Dream] Starting memory consolidation at $(date)" | tee -a "$LOG_FILE"

# 1. 扫描工作区文件
FILES_TO_PROCESS=$(find "$WORKSPACE_DIR" -type f \( -name "*.log" -o -name "*.md" \) -mtime -1)

if [ -z "$FILES_TO_PROCESS" ]; then
    echo "[Auto Dream] No new files to process." | tee -a "$LOG_FILE"
    exit 0
fi

# 2. 遍历并提炼（模拟 LLM 提炼过程）
for FILE in $FILES_TO_PROCESS; do
    echo "[Auto Dream] Processing $FILE..." | tee -a "$LOG_FILE"
    
    # 检查是否包含错误日志
    if grep -qi "error\|exception\|failed" "$FILE"; then
        echo "[Auto Dream] Found error logs in $FILE. Extracting solution..." | tee -a "$LOG_FILE"
        # 在实际运行中，这里会调用 LLM 提取错误和解决方案
        # 示例：将提取的内容写入 errors 目录
        ERROR_SUMMARY="Extracted from $FILE on $(date)\n\n$(grep -i -A 5 "error\|exception\|failed" "$FILE")"
        echo -e "$ERROR_SUMMARY" > "$KB_DIR/errors/$(basename "$FILE").md"
    fi
    
    # 检查是否包含架构模式
    if grep -qi "architecture\|pattern\|design" "$FILE"; then
        echo "[Auto Dream] Found architecture patterns in $FILE. Extracting..." | tee -a "$LOG_FILE"
        # 示例：将提取的内容写入 patterns 目录
        PATTERN_SUMMARY="Extracted from $FILE on $(date)\n\n$(grep -i -A 10 "architecture\|pattern\|design" "$FILE")"
        echo -e "$PATTERN_SUMMARY" > "$KB_DIR/patterns/$(basename "$FILE").md"
    fi
done

echo "[Auto Dream] Memory consolidation completed at $(date)" | tee -a "$LOG_FILE"
```

## 4. 协作与触发

- **触发者**：KO（知识管理员）或 Ops（定时任务）。
- **前置条件**：系统处于空闲状态，或积累了大量未处理的日志文件。
- **输出结果**：更新后的 `knowledge-base/` 目录，供其他 Agent 通过 RAG 检索使用。
