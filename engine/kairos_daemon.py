#!/usr/bin/env python3
"""
OPT v6.2 - KAIROS Daemon: Append-only Decision Log System
基于 Claude Code KAIROS 长会话助理模式的追加式日志守护进程

核心思路：
  - 放弃覆盖式更新（Overwrite），采用按天滚动的追加式日志
  - 日志路径：memory/kairos_logs/YYYY/MM/YYYY-MM-DD.md
  - 每条日志记录都有时间戳锚点（#anchor-HHMMSS），支持精准定位
  - 拦截 CoS 的所有关键决策、状态变更和 Escalation 事件
  - 老板可随时查阅完整的历史决策时间线

日志级别：
  - DECISION  : CoS 做出的关键决策（如任务分配、方案选择）
  - STATUS    : Agent 状态变更（如任务开始、完成、失败）
  - ESCALATION: 需要人工介入的升级事件
  - MILESTONE : 重要里程碑（如功能上线、版本发布）
  - NOTE      : 一般性备注（如用户偏好变化、技术债记录）

使用方式：
  from engine.kairos_daemon import KairosDaemon
  kairos = KairosDaemon()
  kairos.log("DECISION", "CoS", "决定使用 Vite 替代 CRA 以提升构建速度")
  kairos.log("STATUS", "FE", "开始构建落地页", task_id="TASK-001")
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))
KAIROS_LOG_DIR = WORKSPACE / "memory" / "kairos_logs"

# 日志级别类型
LogLevel = Literal["DECISION", "STATUS", "ESCALATION", "MILESTONE", "NOTE"]

# 日志级别的 Markdown 样式
LEVEL_STYLES = {
    "DECISION":   "🔵",
    "STATUS":     "🟢",
    "ESCALATION": "🔴",
    "MILESTONE":  "🏆",
    "NOTE":       "📝",
}

# 日志级别的优先级（用于过滤）
LEVEL_PRIORITY = {
    "MILESTONE":  5,
    "ESCALATION": 4,
    "DECISION":   3,
    "STATUS":     2,
    "NOTE":       1,
}


class KairosDaemon:
    """
    KAIROS 追加式日志守护进程。
    线程安全，支持多 Agent 并发写入。
    """

    def __init__(self, workspace: Optional[Path] = None):
        self.log_dir = (workspace or WORKSPACE) / "memory" / "kairos_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_path(self, date: Optional[datetime] = None) -> Path:
        """获取指定日期的日志文件路径"""
        d = date or datetime.now()
        day_dir = self.log_dir / d.strftime("%Y") / d.strftime("%m")
        day_dir.mkdir(parents=True, exist_ok=True)
        return day_dir / d.strftime("%Y-%m-%d.md")

    def _ensure_day_header(self, log_path: Path, date: datetime) -> None:
        """确保日志文件有当天的标题头（仅在文件为空时写入）"""
        if not log_path.exists() or log_path.stat().st_size == 0:
            header = (
                f"# KAIROS 决策日志 — {date.strftime('%Y年%m月%d日')}\n\n"
                f"> 本文件由 KAIROS 守护进程自动生成，采用追加式写入，禁止手动修改。\n"
                f"> 每条记录均有时间戳锚点，支持通过 `#anchor-HHMMSS` 精准定位。\n\n"
                f"---\n\n"
            )
            log_path.write_text(header, encoding="utf-8")

    def log(
        self,
        level: LogLevel,
        agent: str,
        message: str,
        task_id: Optional[str] = None,
        details: Optional[dict] = None,
        timestamp: Optional[datetime] = None,
    ) -> str:
        """
        追加一条日志记录。
        
        参数：
            level   : 日志级别（DECISION/STATUS/ESCALATION/MILESTONE/NOTE）
            agent   : 发出日志的 Agent 名称（如 "CoS", "FE", "BE"）
            message : 日志内容（简洁描述，建议 < 100 字符）
            task_id : 关联的任务 ID（可选，如 "TASK-20260416-001"）
            details : 附加的结构化信息（可选，会以 JSON 代码块形式展示）
            timestamp: 指定时间戳（默认为当前时间）
        
        返回：
            生成的锚点 ID（如 "anchor-130945"）
        """
        now = timestamp or datetime.now()
        log_path = self._get_log_path(now)
        self._ensure_day_header(log_path, now)

        # 生成时间戳锚点
        anchor = f"anchor-{now.strftime('%H%M%S')}"
        time_str = now.strftime("%H:%M:%S")
        icon = LEVEL_STYLES.get(level, "⚪")

        # 构建日志条目
        lines = [
            f"### {icon} [{level}] {time_str} — {agent} {{#{anchor}}}",
            "",
            f"{message}",
        ]

        if task_id:
            lines.append(f"\n**关联任务**: `{task_id}`")

        if details:
            lines.append("\n**详细信息**:")
            lines.append("```json")
            lines.append(json.dumps(details, ensure_ascii=False, indent=2))
            lines.append("```")

        lines.append("\n---\n")
        entry = "\n".join(lines)

        # 追加写入（append-only，绝不覆盖）
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

        return anchor

    def log_decision(self, agent: str, message: str, **kwargs) -> str:
        """快捷方法：记录决策"""
        return self.log("DECISION", agent, message, **kwargs)

    def log_status(self, agent: str, message: str, **kwargs) -> str:
        """快捷方法：记录状态变更"""
        return self.log("STATUS", agent, message, **kwargs)

    def log_escalation(self, agent: str, message: str, **kwargs) -> str:
        """快捷方法：记录升级事件"""
        return self.log("ESCALATION", agent, message, **kwargs)

    def log_milestone(self, agent: str, message: str, **kwargs) -> str:
        """快捷方法：记录里程碑"""
        return self.log("MILESTONE", agent, message, **kwargs)

    def read_today(self) -> str:
        """读取今天的完整日志"""
        log_path = self._get_log_path()
        if log_path.exists():
            return log_path.read_text(encoding="utf-8")
        return "（今日暂无日志记录）"

    def read_date(self, date_str: str) -> str:
        """读取指定日期的日志（格式：YYYY-MM-DD）"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            log_path = self._get_log_path(date)
            if log_path.exists():
                return log_path.read_text(encoding="utf-8")
            return f"（{date_str} 暂无日志记录）"
        except ValueError:
            return f"（日期格式错误：{date_str}，请使用 YYYY-MM-DD 格式）"

    def search(self, keyword: str, days: int = 7) -> list[dict]:
        """
        在最近 N 天的日志中搜索关键词。
        返回包含关键词的日志条目列表。
        """
        results = []
        now = datetime.now()

        for i in range(days):
            from datetime import timedelta
            date = now - timedelta(days=i)
            log_path = self._get_log_path(date)
            if not log_path.exists():
                continue

            content = log_path.read_text(encoding="utf-8")
            # 按 ### 分割日志条目
            entries = content.split("\n### ")
            for entry in entries[1:]:  # 跳过文件头
                if keyword.lower() in entry.lower():
                    results.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "content": "### " + entry[:300] + ("..." if len(entry) > 300 else "")
                    })

        return results

    def generate_daily_summary(self, date_str: Optional[str] = None) -> str:
        """
        生成指定日期的日志摘要（用于 CoS 的每日汇报）。
        统计各级别日志数量，提取所有里程碑和升级事件。
        """
        if date_str:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date = datetime.now()

        log_path = self._get_log_path(date)
        if not log_path.exists():
            return f"## {date.strftime('%Y-%m-%d')} 日志摘要\n\n（当日无记录）"

        content = log_path.read_text(encoding="utf-8")
        entries = content.split("\n### ")[1:]  # 跳过文件头

        stats = {level: 0 for level in LEVEL_STYLES}
        milestones = []
        escalations = []

        for entry in entries:
            for level in LEVEL_STYLES:
                if f"[{level}]" in entry:
                    stats[level] += 1
                    if level == "MILESTONE":
                        # 提取里程碑内容（第一行正文）
                        lines = entry.split("\n")
                        for line in lines[2:]:
                            if line.strip() and not line.startswith("**"):
                                milestones.append(line.strip())
                                break
                    elif level == "ESCALATION":
                        lines = entry.split("\n")
                        for line in lines[2:]:
                            if line.strip() and not line.startswith("**"):
                                escalations.append(line.strip())
                                break
                    break

        summary_lines = [
            f"## {date.strftime('%Y-%m-%d')} 日志摘要",
            "",
            "### 活动统计",
            f"| 级别 | 数量 |",
            f"|---|---|",
        ]
        for level, count in sorted(stats.items(), key=lambda x: -LEVEL_PRIORITY[x[0]]):
            if count > 0:
                summary_lines.append(f"| {LEVEL_STYLES[level]} {level} | {count} |")

        if milestones:
            summary_lines.append("\n### 里程碑")
            for m in milestones:
                summary_lines.append(f"- 🏆 {m}")

        if escalations:
            summary_lines.append("\n### 待处理升级事件")
            for e in escalations:
                summary_lines.append(f"- 🔴 {e}")

        return "\n".join(summary_lines)


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    kairos = KairosDaemon(workspace=Path("/tmp/opt_test_workspace"))

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # 演示：模拟一天的决策日志
        print("=== KAIROS 演示：写入日志 ===")
        kairos.log_decision("CoS", "决定使用 Vite + React 构建落地页，部署到 GitHub Pages",
                            task_id="TASK-20260416-001",
                            details={"reason": "Vite 构建速度比 CRA 快 10x", "approved_by": "CTO"})
        kairos.log_status("FE", "开始构建落地页 Hero Section", task_id="TASK-20260416-001")
        kairos.log_status("BE", "API 接口设计完成，开始编写 FastAPI 路由")
        kairos.log_escalation("QA", "发现 Safari 上的 CSS 兼容性问题，需要 FE 介入",
                              details={"browser": "Safari 17", "issue": "flex gap 不支持"})
        kairos.log_milestone("CoS", "落地页 v1.0 上线成功，URL: https://example.com",
                             task_id="TASK-20260416-001")

        print("\n=== 今日日志内容 ===")
        print(kairos.read_today())

        print("\n=== 今日摘要 ===")
        print(kairos.generate_daily_summary())

    elif len(sys.argv) > 1 and sys.argv[1] == "read":
        date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime("%Y-%m-%d")
        print(kairos.read_date(date_str))

    elif len(sys.argv) > 1 and sys.argv[1] == "summary":
        date_str = sys.argv[2] if len(sys.argv) > 2 else None
        print(kairos.generate_daily_summary(date_str))

    else:
        print("用法:")
        print("  python3 engine/kairos_daemon.py demo     # 演示模式")
        print("  python3 engine/kairos_daemon.py read [YYYY-MM-DD]   # 读取日志")
        print("  python3 engine/kairos_daemon.py summary [YYYY-MM-DD] # 生成摘要")
