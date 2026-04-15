# opt-security-audit: 安全审计与权限控制

## 1. 技能简介

`opt-security-audit` 是 OPT 龙虾军团 v5.0 的安全基石，基于 Claude Code 的 Fail-closed 原则和 OpenHarness 的 Hooks 机制设计。
它由 Ops（运维审计员）执行，负责拦截危险操作、审计执行日志，并防止 Agent 发生角色漂移（Role Drift）。

## 2. 核心机制（Harness 层）

- **PreToolUse Hook（事前拦截）**：在执行任何工具调用前，检查命令是否在黑名单中（如 `rm -rf /`、`chmod 777`）。
- **PostToolUse Hook（事后清洗）**：在工具执行后，扫描输出日志，脱敏敏感信息（如 API Keys、密码）。
- **Role Drift Check（角色漂移检查）**：定期扫描各 Agent 的行为日志，确保其没有越权执行任务（如 Researcher 写代码）。

## 3. 执行脚本示例

### 3.1 Python 审计脚本 (`security_audit.py`)

Ops 可以使用此脚本进行安全审计：

```python
#!/usr/bin/env python3
# security_audit.py - 安全审计与 Hooks 拦截脚本

import re
import sys

# 危险命令黑名单
DANGEROUS_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"chmod\s+777",
    r"mkfs",
    r"dd\s+if=",
    r">\s*/dev/sda"
]

# 敏感信息正则（如 API Keys）
SENSITIVE_PATTERNS = [
    r"sk-[a-zA-Z0-9]{48}",  # OpenAI Key
    r"ghp_[a-zA-Z0-9]{36}", # GitHub Token
    r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}" # Slack Token
]

def pre_tool_use_hook(command):
    """
    事前拦截：检查命令是否包含危险操作。
    """
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, command):
            print(f"[Security Audit] BLOCKED: Command matches dangerous pattern '{pattern}'")
            return False
    return True

def post_tool_use_hook(output):
    """
    事后清洗：脱敏输出中的敏感信息。
    """
    cleaned_output = output
    for pattern in SENSITIVE_PATTERNS:
        cleaned_output = re.sub(pattern, "[REDACTED]", cleaned_output)
    return cleaned_output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 security_audit.py <hook_type> <input>")
        sys.exit(1)
        
    hook_type = sys.argv[1]
    input_data = sys.argv[2]
    
    if hook_type == "pre":
        if pre_tool_use_hook(input_data):
            print("[Security Audit] PASSED")
            sys.exit(0)
        else:
            sys.exit(1)
    elif hook_type == "post":
        cleaned = post_tool_use_hook(input_data)
        print(cleaned)
        sys.exit(0)
    else:
        print("Invalid hook type. Use 'pre' or 'post'.")
        sys.exit(1)
```

## 4. 协作与触发

- **触发者**：Ops（运维审计员）或底层执行引擎（自动触发）。
- **前置条件**：任何工具调用（Pre/Post）或定期的系统审计。
- **输出结果**：拦截危险操作，脱敏敏感信息，生成审计报告。
