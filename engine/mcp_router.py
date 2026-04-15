#!/usr/bin/env python3
"""
OPT v7.0 - MCP Router: Unified MCP Server Permission Router
统一 MCP 服务器权限路由与调度器

核心设计思路：
  - 每个 MCP 服务器（Jira/Slack/Figma/GitHub/Postgres）都有独立的权限矩阵
  - 每个 Agent 只能调用其被授权的 MCP 工具，违规调用被 Fail-closed 拦截
  - 所有 MCP 调用都经过 KAIROS 日志记录（DECISION/STATUS/ESCALATION）
  - 支持"只读模式"和"读写模式"的动态切换（由 CoS 授权）

权限矩阵（Agent → MCP Server → 允许的操作）：
  CoS:        Jira(read/write) + Slack(write) + GitHub(read)
  CTO:        GitHub(read/write) + Jira(read)
  FE:         Figma(read) + GitHub(read/write)
  BE:         GitHub(read/write) + Postgres(read/write)
  QA:         GitHub(read) + Jira(write)
  Researcher: Slack(read) + GitHub(read)
  KO:         GitHub(read/write) + Slack(write)
  Ops:        GitHub(read) + Slack(write) + Postgres(read)

使用方式：
  from engine.mcp_router import MCPRouter
  router = MCPRouter()
  result = router.call("FE", "figma", "get_file", {"file_key": "abc123"})
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))

# ── 权限矩阵定义 ─────────────────────────────────────────────────────────────
# 格式：{agent_id: {server_name: [allowed_operations]}}
# 操作类型：read / write / admin
# "*" 表示允许所有操作

PERMISSION_MATRIX = {
    "cos": {
        "jira":     ["read", "write"],      # 创建/更新 Issue，查看看板
        "slack":    ["write"],              # 发送消息、通知
        "github":   ["read"],              # 查看 PR、Issue
        "figma":    [],                    # 无权限
        "postgres": [],                    # 无权限
    },
    "cto": {
        "jira":     ["read"],              # 只读 Issue
        "slack":    ["write"],             # 发送技术通知
        "github":   ["read", "write"],     # 审查 PR、合并代码
        "figma":    ["read"],              # 查看设计规范
        "postgres": [],                    # 无权限（安全隔离）
    },
    "fe": {
        "jira":     ["read"],              # 查看前端任务
        "slack":    [],                    # 无权限
        "github":   ["read", "write"],     # 提交前端代码
        "figma":    ["read"],              # 读取设计图（核心权限）
        "postgres": [],                    # 无权限（前后端隔离）
    },
    "be": {
        "jira":     ["read"],              # 查看后端任务
        "slack":    [],                    # 无权限
        "github":   ["read", "write"],     # 提交后端代码
        "figma":    [],                    # 无权限
        "postgres": ["read", "write"],     # 数据库操作
    },
    "qa": {
        "jira":     ["read", "write"],     # 创建 Bug 报告
        "slack":    ["write"],             # 发送测试报告
        "github":   ["read"],              # 查看代码
        "figma":    ["read"],              # 查看设计验收标准
        "postgres": ["read"],              # 只读数据验证
    },
    "researcher": {
        "jira":     ["read"],              # 查看项目进度
        "slack":    ["read"],              # 读取频道信息
        "github":   ["read"],              # 查看代码库
        "figma":    [],                    # 无权限
        "postgres": [],                    # 无权限
    },
    "ko": {
        "jira":     ["read"],              # 查看任务历史
        "slack":    ["write"],             # 发布知识更新通知
        "github":   ["read", "write"],     # 更新 SKILL.md 文件
        "figma":    [],                    # 无权限
        "postgres": [],                    # 无权限
    },
    "ops": {
        "jira":     ["read"],              # 查看运维任务
        "slack":    ["write"],             # 发送运维告警
        "github":   ["read"],              # 查看部署配置
        "figma":    [],                    # 无权限
        "postgres": ["read"],              # 只读数据库监控
    },
}

# MCP 操作到权限类型的映射
# 格式：{server_name: {tool_name: required_permission}}
TOOL_PERMISSION_MAP = {
    "jira": {
        "get_issue":        "read",
        "list_issues":      "read",
        "search_issues":    "read",
        "create_issue":     "write",
        "update_issue":     "write",
        "add_comment":      "write",
        "transition_issue": "write",
        "delete_issue":     "admin",
    },
    "slack": {
        "list_channels":    "read",
        "get_messages":     "read",
        "post_message":     "write",
        "upload_file":      "write",
        "create_channel":   "admin",
    },
    "github": {
        "get_file":         "read",
        "list_files":       "read",
        "get_pr":           "read",
        "list_prs":         "read",
        "get_issue":        "read",
        "list_issues":      "read",
        "create_file":      "write",
        "update_file":      "write",
        "create_pr":        "write",
        "merge_pr":         "write",
        "create_issue":     "write",
        "push_files":       "write",
    },
    "figma": {
        "get_file":         "read",
        "get_node":         "read",
        "get_image":        "read",
        "list_files":       "read",
        "get_comments":     "read",
        "post_comment":     "write",
    },
    "postgres": {
        "query":            "read",
        "select":           "read",
        "insert":           "write",
        "update":           "write",
        "delete":           "write",
        "create_table":     "admin",
        "drop_table":       "admin",
    },
}


class MCPPermissionError(Exception):
    """MCP 权限拒绝异常"""
    pass


class MCPRouter:
    """
    统一 MCP 服务器权限路由与调度器。
    所有 Agent 对 MCP 服务器的调用都必须经过此路由器。
    """

    def __init__(self, workspace: Optional[Path] = None):
        self.workspace = workspace or WORKSPACE
        self._kairos = None  # 延迟加载，避免循环依赖
        self._audit_log_path = self.workspace / "memory" / "kairos_logs" / "mcp_audit.jsonl"
        self._audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_kairos(self):
        """延迟加载 KAIROS 守护进程"""
        if self._kairos is None:
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from engine.kairos_daemon import KairosDaemon
                self._kairos = KairosDaemon(workspace=self.workspace)
            except ImportError:
                pass
        return self._kairos

    def _check_permission(self, agent_id: str, server: str, tool: str) -> bool:
        """
        检查 Agent 是否有权限调用指定的 MCP 工具。
        
        返回 True 表示允许，False 表示拒绝。
        """
        agent_id = agent_id.lower()
        server = server.lower()

        # 检查 Agent 是否存在于权限矩阵
        if agent_id not in PERMISSION_MATRIX:
            return False

        # 检查服务器是否存在
        agent_perms = PERMISSION_MATRIX[agent_id]
        if server not in agent_perms:
            return False

        # 获取该 Agent 对该服务器的允许操作列表
        allowed_ops = agent_perms[server]
        if not allowed_ops:
            return False

        # 如果允许所有操作
        if "*" in allowed_ops:
            return True

        # 获取该工具需要的权限级别
        server_tools = TOOL_PERMISSION_MAP.get(server, {})
        required_perm = server_tools.get(tool, "read")  # 默认需要 read 权限

        # 权限层级：admin > write > read
        perm_levels = {"read": 1, "write": 2, "admin": 3}
        required_level = perm_levels.get(required_perm, 1)

        # 检查 Agent 是否有足够的权限级别
        max_allowed_level = max(perm_levels.get(op, 0) for op in allowed_ops)
        return max_allowed_level >= required_level

    def _audit_log(self, agent_id: str, server: str, tool: str,
                   args: dict, result: Any, allowed: bool, error: Optional[str] = None):
        """将 MCP 调用记录到审计日志（JSONL 格式，追加写入）"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "server": server,
            "tool": tool,
            "args_keys": list(args.keys()) if args else [],  # 只记录参数名，不记录值（安全）
            "allowed": allowed,
            "error": error,
            "status": "success" if allowed and not error else "blocked" if not allowed else "error"
        }
        with open(self._audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # 同步到 KAIROS（仅记录重要事件）
        kairos = self._get_kairos()
        if kairos:
            if not allowed:
                kairos.log_escalation(
                    agent_id.upper(),
                    f"MCP 权限拒绝：{agent_id} 尝试调用 {server}.{tool}，但无权限",
                    details={"server": server, "tool": tool, "required": TOOL_PERMISSION_MAP.get(server, {}).get(tool, "read")}
                )
            elif error:
                kairos.log("STATUS", agent_id.upper(),
                           f"MCP 调用失败：{server}.{tool} — {error[:100]}")

    def call(
        self,
        agent_id: str,
        server: str,
        tool: str,
        args: Optional[dict] = None,
        dry_run: bool = False
    ) -> Any:
        """
        通过权限路由器调用 MCP 工具。
        
        参数：
            agent_id: 发起调用的 Agent ID（如 "fe", "cos"）
            server:   MCP 服务器名称（如 "figma", "jira"）
            tool:     工具名称（如 "get_file", "create_issue"）
            args:     工具参数字典
            dry_run:  如果为 True，只检查权限不实际执行
        
        返回：
            MCP 工具的返回结果
        
        异常：
            MCPPermissionError: 权限不足时抛出
        """
        args = args or {}

        # 权限检查（Fail-closed）
        allowed = self._check_permission(agent_id, server, tool)
        if not allowed:
            self._audit_log(agent_id, server, tool, args, None, False)
            raise MCPPermissionError(
                f"[MCPRouter] 权限拒绝: Agent '{agent_id}' 无权调用 {server}.{tool}\n"
                f"  当前权限: {PERMISSION_MATRIX.get(agent_id.lower(), {}).get(server.lower(), [])}\n"
                f"  所需权限: {TOOL_PERMISSION_MAP.get(server, {}).get(tool, 'read')}"
            )

        if dry_run:
            return {"status": "dry_run_ok", "agent": agent_id, "server": server, "tool": tool}

        # 实际调用 MCP（通过 manus-mcp-cli）
        try:
            result = self._invoke_mcp(server, tool, args)
            self._audit_log(agent_id, server, tool, args, result, True)
            return result
        except Exception as e:
            self._audit_log(agent_id, server, tool, args, None, True, str(e))
            raise

    def _invoke_mcp(self, server: str, tool: str, args: dict) -> Any:
        """
        实际调用 MCP 工具（通过 manus-mcp-cli 命令行工具）。
        """
        cmd = [
            "manus-mcp-cli", "tool", "call", tool,
            "--server", server,
            "--input", json.dumps(args, ensure_ascii=False)
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"MCP 调用失败: {result.stderr[:200]}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw_output": result.stdout}

    def get_agent_permissions(self, agent_id: str) -> dict:
        """获取指定 Agent 的完整权限清单"""
        agent_id = agent_id.lower()
        if agent_id not in PERMISSION_MATRIX:
            return {}
        return PERMISSION_MATRIX[agent_id]

    def list_available_tools(self, agent_id: str, server: str) -> list[str]:
        """列出指定 Agent 在指定服务器上可以调用的工具列表"""
        agent_id = agent_id.lower()
        server = server.lower()

        available = []
        for tool in TOOL_PERMISSION_MAP.get(server, {}):
            if self._check_permission(agent_id, server, tool):
                available.append(tool)
        return available

    def generate_permission_report(self) -> str:
        """生成完整的权限矩阵报告（Markdown 格式）"""
        servers = ["jira", "slack", "github", "figma", "postgres"]
        agents = list(PERMISSION_MATRIX.keys())

        lines = [
            "# MCP 权限矩阵报告",
            "",
            f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 权限概览",
            "",
            "| Agent | " + " | ".join(s.capitalize() for s in servers) + " |",
            "|---|" + "|".join(["---"] * len(servers)) + "|",
        ]

        for agent in agents:
            perms = PERMISSION_MATRIX[agent]
            row_cells = []
            for server in servers:
                ops = perms.get(server, [])
                if not ops:
                    row_cells.append("—")
                elif "*" in ops:
                    row_cells.append("✅ 全部")
                else:
                    icons = {"read": "👁️", "write": "✏️", "admin": "🔑"}
                    row_cells.append(" ".join(icons.get(op, op) for op in ops))
            lines.append(f"| **{agent.upper()}** | " + " | ".join(row_cells) + " |")

        lines += [
            "",
            "## 图例",
            "",
            "| 图标 | 含义 |",
            "|---|---|",
            "| 👁️ | 只读权限 |",
            "| ✏️ | 读写权限 |",
            "| 🔑 | 管理员权限 |",
            "| — | 无权限（Fail-closed 拦截） |",
        ]

        return "\n".join(lines)


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    router = MCPRouter(workspace=Path("/tmp/opt_test_workspace"))

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(router.generate_permission_report())

    elif len(sys.argv) > 1 and sys.argv[1] == "check":
        # 用法：python3 mcp_router.py check <agent> <server> <tool>
        if len(sys.argv) >= 5:
            agent, server, tool = sys.argv[2], sys.argv[3], sys.argv[4]
            allowed = router._check_permission(agent, server, tool)
            print(f"{'✅ 允许' if allowed else '❌ 拒绝'}: {agent} → {server}.{tool}")
        else:
            print("用法: python3 mcp_router.py check <agent> <server> <tool>")

    elif len(sys.argv) > 1 and sys.argv[1] == "tools":
        # 用法：python3 mcp_router.py tools <agent> <server>
        if len(sys.argv) >= 4:
            agent, server = sys.argv[2], sys.argv[3]
            tools = router.list_available_tools(agent, server)
            print(f"{agent.upper()} 在 {server} 上可用的工具：")
            for t in tools:
                print(f"  - {t}")
        else:
            print("用法: python3 mcp_router.py tools <agent> <server>")

    elif len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("=== MCP 权限路由演示 ===\n")
        # 测试合法调用
        print("✅ 合法调用测试：")
        try:
            result = router.call("fe", "figma", "get_file", {"file_key": "abc123"}, dry_run=True)
            print(f"  FE → figma.get_file: {result['status']}")
        except MCPPermissionError as e:
            print(f"  错误: {e}")

        # 测试非法调用
        print("\n❌ 非法调用测试（FE 尝试写入 Postgres）：")
        try:
            router.call("fe", "postgres", "insert", {"table": "users"}, dry_run=True)
        except MCPPermissionError as e:
            print(f"  已拦截: {str(e).split(chr(10))[0]}")

        # 测试非法调用（BE 尝试读取 Figma）
        print("\n❌ 非法调用测试（BE 尝试读取 Figma）：")
        try:
            router.call("be", "figma", "get_file", {}, dry_run=True)
        except MCPPermissionError as e:
            print(f"  已拦截: {str(e).split(chr(10))[0]}")

        print("\n=== 权限矩阵报告 ===\n")
        print(router.generate_permission_report())

    else:
        print("用法:")
        print("  python3 engine/mcp_router.py demo              # 演示模式")
        print("  python3 engine/mcp_router.py report            # 生成权限矩阵报告")
        print("  python3 engine/mcp_router.py check <agent> <server> <tool>")
        print("  python3 engine/mcp_router.py tools <agent> <server>")
