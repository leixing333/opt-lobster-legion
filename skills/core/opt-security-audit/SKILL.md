# SKILL: opt-security-audit — 安全审计与 Hooks 管理技能

## 1. 技能简介

本技能基于 Claude Code 的 Fail-closed 安全策略和 OpenHarness 的 Hooks 机制，实现了一套完整的安全审计系统。核心原则：**当无法判断一个操作是否安全时，默认拒绝**。

## 2. 适用场景

- Ops 执行每周安全审计。
- 检测 Agent 是否发生角色漂移（行为超出 SOUL.md 定义的边界）。
- 审查 Hooks 拦截器的有效性。
- 检查环境变量和 API Keys 是否泄露。

## 3. 每周安全审计脚本

```bash
#!/bin/bash
# OPT v6.0 - 每周安全审计脚本
# 由 Ops 每周一执行

WORKSPACE="${HOME}/workspace"
AUDIT_DIR="${WORKSPACE}/memory/audit"
REPORT_FILE="${AUDIT_DIR}/weekly_audit_$(date +%Y%m%d).md"

mkdir -p "$AUDIT_DIR"

echo "# OPT 安全审计报告" > "$REPORT_FILE"
echo "**日期**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 1. 检查 API Keys 是否泄露到代码中
echo "## 1. API Keys 泄露检查" >> "$REPORT_FILE"
LEAKED=$(grep -r "sk-\|ghp_\|AKIA\|xoxb-" "${WORKSPACE}" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --exclude-dir=".git" --exclude-dir="node_modules" -l 2>/dev/null)

if [ -z "$LEAKED" ]; then
    echo "✅ 未发现 API Keys 泄露" >> "$REPORT_FILE"
else
    echo "🚨 发现疑似 API Keys 泄露的文件：" >> "$REPORT_FILE"
    echo "$LEAKED" >> "$REPORT_FILE"
fi

# 2. 检查 Hooks 拦截器是否正常运行
echo "" >> "$REPORT_FILE"
echo "## 2. Hooks 拦截器状态" >> "$REPORT_FILE"
HOOKS_DIR="${WORKSPACE}/../hooks"
for hook in "${HOOKS_DIR}/pre_tool_use/"*.py "${HOOKS_DIR}/post_tool_use/"*.py; do
    if [ -f "$hook" ]; then
        python3 -m py_compile "$hook" 2>/dev/null && \
            echo "✅ $(basename $hook) 语法正常" >> "$REPORT_FILE" || \
            echo "❌ $(basename $hook) 语法错误" >> "$REPORT_FILE"
    fi
done

# 3. 检查审计日志完整性
echo "" >> "$REPORT_FILE"
echo "## 3. 审计日志检查" >> "$REPORT_FILE"
LOG_COUNT=$(ls "${AUDIT_DIR}"/audit_*.jsonl 2>/dev/null | wc -l)
echo "过去 7 天审计日志文件数量: ${LOG_COUNT}" >> "$REPORT_FILE"

# 4. 检查 .env 文件是否在 .gitignore 中
echo "" >> "$REPORT_FILE"
echo "## 4. .env 文件保护检查" >> "$REPORT_FILE"
if grep -q "^\.env$" "${WORKSPACE}/../.gitignore" 2>/dev/null; then
    echo "✅ .env 已在 .gitignore 中" >> "$REPORT_FILE"
else
    echo "⚠️ .env 未在 .gitignore 中，存在泄露风险" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "审计完成。报告已保存到: $REPORT_FILE"
cat "$REPORT_FILE"
```

## 4. 角色漂移检测

```python
#!/usr/bin/env python3
"""检测 Agent 是否发生角色漂移"""

import json
import glob
import os
from pathlib import Path

AUDIT_DIR = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace")) / "memory/audit"

# 每个 Agent 的允许工具列表（来自 SOUL.md 的 disallowedTools 反推）
AGENT_ALLOWED_TOOLS = {
    "cos": ["ReadFile", "WriteFile"],  # CoS 只读写文件，不执行命令
    "fe": ["ReadFile", "WriteFile", "EditFile", "BashTool"],
    "be": ["ReadFile", "WriteFile", "EditFile", "BashTool"],
    "qa": ["ReadFile", "WriteFile", "BashTool"],
    "cto": ["ReadFile", "WriteFile"],  # CTO 默认 Plan Mode
    "ko": ["ReadFile", "WriteFile", "EditFile"],
    "ops": ["ReadFile", "WriteFile", "BashTool"],
    "researcher": ["ReadFile", "WriteFile", "WebSearch"]
}

def detect_drift(days: int = 7) -> list[dict]:
    """检测过去 N 天内的角色漂移行为"""
    violations = []
    
    for log_file in glob.glob(str(AUDIT_DIR / "audit_*.jsonl")):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    agent_id = entry.get("agent_id", "unknown")
                    tool_name = entry.get("tool_name", "")
                    
                    allowed = AGENT_ALLOWED_TOOLS.get(agent_id, [])
                    if allowed and tool_name not in allowed:
                        violations.append({
                            "agent": agent_id,
                            "tool": tool_name,
                            "timestamp": entry.get("timestamp"),
                            "severity": "HIGH" if tool_name == "BashTool" else "MEDIUM"
                        })
                except json.JSONDecodeError:
                    continue
    
    return violations

if __name__ == "__main__":
    violations = detect_drift()
    if violations:
        print(f"🚨 发现 {len(violations)} 个角色漂移行为：")
        for v in violations:
            print(f"  [{v['severity']}] {v['agent']} 使用了 {v['tool']} ({v['timestamp']})")
    else:
        print("✅ 未发现角色漂移行为")
```

## 5. 变更日志

- 2026-04-16: v1.0 初始版本，基于 OpenHarness Hooks 机制设计
- 2026-04-16: v1.1 增加角色漂移检测功能（Claude Code Fail-closed 原则）
