#!/usr/bin/env python3
"""
OPT v6.0 - PostToolUse Hook: Audit Logger
基于 OpenHarness Hooks 机制实现的审计日志记录器
"""

import json
import sys
import os
from datetime import datetime

AUDIT_LOG_PATH = "/home/ubuntu/workspace/memory/audit"

SENSITIVE_PATTERNS = [
    "api_key", "apikey", "secret", "password", "passwd",
    "token", "bearer", "authorization", "private_key"
]

def sanitize_output(output: str) -> str:
    """清洗输出中的敏感信息"""
    lines = output.split("\n")
    sanitized = []
    for line in lines:
        lower_line = line.lower()
        if any(pattern in lower_line for pattern in SENSITIVE_PATTERNS):
            sanitized.append("[REDACTED - 敏感信息已脱敏]")
        else:
            sanitized.append(line)
    return "\n".join(sanitized)

def log_audit(tool_name: str, tool_input: dict, tool_output: str, agent_id: str):
    """记录审计日志"""
    os.makedirs(AUDIT_LOG_PATH, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "tool_name": tool_name,
        "tool_input_summary": str(tool_input)[:200],  # 只记录前200字符
        "tool_output_summary": sanitize_output(tool_output)[:500],
        "status": "completed"
    }
    
    log_file = os.path.join(AUDIT_LOG_PATH, f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_output = input_data.get("tool_output", "")
        agent_id = input_data.get("agent_id", "unknown")
        
        # 清洗输出
        sanitized_output = sanitize_output(tool_output)
        
        # 记录审计日志
        log_audit(tool_name, tool_input, tool_output, agent_id)
        
        # 返回清洗后的输出
        print(json.dumps({
            "status": "logged",
            "sanitized_output": sanitized_output
        }))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({"status": "error", "reason": str(e)}))
        sys.exit(0)  # PostToolUse 错误不应阻断主流程

if __name__ == "__main__":
    main()
