#!/usr/bin/env python3
"""
OPT v6.0 - PreToolUse Hook: Permission Check
基于 OpenHarness Hooks 机制实现的权限检查拦截器
"""

import json
import sys
import os

# 权限配置（对应 openclaw.json 中的 permissions 配置）
PERMISSION_CONFIG = {
    "mode": "plan",  # default / auto / plan
    "blocked_commands": ["rm -rf /", "mkfs", "dd if=/dev/", ":(){ :|:& };:"],
    "allowed_paths": ["/home/ubuntu/workspace", "/tmp"],
    "high_risk_patterns": ["DROP TABLE", "DELETE FROM", "TRUNCATE", "rm -rf"],
    "require_confirmation": ["git push", "npm publish", "docker push"]
}

def check_permission(tool_name: str, tool_input: dict) -> dict:
    """
    检查工具调用权限
    返回: {"allowed": bool, "reason": str, "require_confirmation": bool}
    """
    result = {"allowed": True, "reason": "", "require_confirmation": False}
    
    # 检查 BashTool 命令
    if tool_name == "BashTool":
        command = tool_input.get("command", "")
        
        # 检查黑名单命令
        for blocked in PERMISSION_CONFIG["blocked_commands"]:
            if blocked in command:
                result["allowed"] = False
                result["reason"] = f"命令被安全策略拒绝：包含危险模式 '{blocked}'"
                return result
        
        # 检查高风险命令（需要确认）
        for pattern in PERMISSION_CONFIG["require_confirmation"]:
            if pattern in command:
                result["require_confirmation"] = True
                result["reason"] = f"高风险操作 '{pattern}' 需要 CoS 确认"
                return result
    
    # 检查文件写入路径
    if tool_name in ["WriteFile", "EditFile"]:
        file_path = tool_input.get("path", "")
        allowed = any(file_path.startswith(p) for p in PERMISSION_CONFIG["allowed_paths"])
        if not allowed:
            result["allowed"] = False
            result["reason"] = f"文件路径 '{file_path}' 超出允许范围"
            return result
    
    return result

def main():
    """Hook 入口函数，从 stdin 读取工具调用信息"""
    try:
        input_data = json.loads(sys.stdin.read())
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        result = check_permission(tool_name, tool_input)
        
        if not result["allowed"]:
            print(json.dumps({
                "status": "blocked",
                "reason": result["reason"],
                "action": "reject"
            }))
            sys.exit(1)
        
        if result["require_confirmation"]:
            print(json.dumps({
                "status": "pending",
                "reason": result["reason"],
                "action": "ask_cos"
            }))
            sys.exit(2)
        
        print(json.dumps({"status": "allowed", "action": "proceed"}))
        sys.exit(0)
        
    except Exception as e:
        print(json.dumps({"status": "error", "reason": str(e), "action": "reject"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
