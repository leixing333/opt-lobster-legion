#!/usr/bin/env python3
"""
OPT v6.1 - Memory Compactor: Incremental Session Compression Engine
基于 Claude Code Session Memory 机制的增量压缩引擎

核心思路：
  - 替代 v6.0 中昂贵的 LLM 全量摘要（Closeout）
  - 维护一个结构化的 JSON 状态机（SessionState），记录增量差异
  - 每次交互后只更新 Diff，保持 Session Memory 大小恒定（目标 < 2KB）
  - 与 auto_dream.py 配合：compactor 负责实时压缩，auto_dream 负责周级巩固

触发时机：
  - 由 CoS 在 /compact 命令时手动触发
  - 由 openclaw.json 中 memory.session.compactThreshold=0.8 自动触发
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))
SESSION_DIR = WORKSPACE / "memory" / "session"
STATE_FILE = SESSION_DIR / "compact_state.json"

# ── 增量状态结构（目标 < 2KB）──────────────────────────────────────────────
EMPTY_STATE: dict = {
    "schema_version": "6.1",
    "last_updated": "",
    "session_id": "",
    "resolved_issues": [],        # 已解决的问题（最多保留 10 条）
    "pending_tasks": [],          # 待处理任务（无上限，但每条 < 100 字符）
    "current_context": {
        "active_agent": "",       # 当前活跃的 Agent
        "active_task": "",        # 当前任务描述
        "key_decisions": [],      # 本轮关键决策（最多 5 条）
        "tech_stack": [],         # 当前技术栈（如 React, FastAPI）
        "open_questions": []      # 未解决的疑问（最多 3 条）
    },
    "user_preferences_delta": [], # 本 Session 发现的用户偏好变化
    "token_stats": {
        "total_turns": 0,
        "compaction_count": 0,
        "last_compact_turn": 0
    }
}


def load_state() -> dict:
    """加载现有的压缩状态，若不存在则返回空状态"""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return EMPTY_STATE.copy()


def save_state(state: dict) -> None:
    """持久化压缩状态"""
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _truncate(text: str, max_len: int = 100) -> str:
    """截断过长文本，保留语义"""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def apply_diff(state: dict, diff: dict) -> dict:
    """
    将增量差异（Diff）应用到现有状态。
    Diff 结构示例：
    {
        "resolved": ["修复了 npm build 缓存问题"],
        "add_pending": ["部署到 GitHub Pages"],
        "remove_pending": ["修复 npm build 缓存问题"],
        "active_agent": "fe",
        "active_task": "构建落地页",
        "add_decisions": ["使用 Vite 替代 CRA 以提升构建速度"],
        "add_tech": ["Vite", "React"],
        "add_questions": ["是否需要 SSR？"],
        "resolve_questions": ["是否需要 SSR？"],
        "user_pref_delta": "偏好使用 Tailwind 而非 CSS Modules"
    }
    """
    ctx = state["current_context"]

    # 1. 标记已解决的问题
    for item in diff.get("resolved", []):
        entry = {"text": _truncate(item), "resolved_at": datetime.now().isoformat()}
        state["resolved_issues"].append(entry)
    # 保留最近 10 条
    state["resolved_issues"] = state["resolved_issues"][-10:]

    # 2. 更新待处理任务
    for item in diff.get("add_pending", []):
        if item not in state["pending_tasks"]:
            state["pending_tasks"].append(_truncate(item))
    for item in diff.get("remove_pending", []):
        state["pending_tasks"] = [t for t in state["pending_tasks"] if t != item]

    # 3. 更新当前上下文
    if diff.get("active_agent"):
        ctx["active_agent"] = diff["active_agent"]
    if diff.get("active_task"):
        ctx["active_task"] = _truncate(diff["active_task"])

    # 4. 更新关键决策（最多 5 条，FIFO）
    for d in diff.get("add_decisions", []):
        ctx["key_decisions"].append(_truncate(d))
    ctx["key_decisions"] = ctx["key_decisions"][-5:]

    # 5. 更新技术栈（去重）
    for t in diff.get("add_tech", []):
        if t not in ctx["tech_stack"]:
            ctx["tech_stack"].append(t)

    # 6. 更新未解决疑问
    for q in diff.get("add_questions", []):
        if q not in ctx["open_questions"]:
            ctx["open_questions"].append(_truncate(q))
    for q in diff.get("resolve_questions", []):
        ctx["open_questions"] = [x for x in ctx["open_questions"] if x != q]
    ctx["open_questions"] = ctx["open_questions"][-3:]

    # 7. 记录用户偏好变化
    if diff.get("user_pref_delta"):
        state["user_preferences_delta"].append({
            "text": _truncate(diff["user_pref_delta"], 150),
            "observed_at": datetime.now().isoformat()
        })

    # 8. 更新统计
    state["token_stats"]["total_turns"] += 1
    state["token_stats"]["compaction_count"] += 1
    state["token_stats"]["last_compact_turn"] = state["token_stats"]["total_turns"]

    return state


def render_compact_summary(state: dict) -> str:
    """
    将压缩状态渲染为人类可读的 Markdown 摘要。
    这个摘要会被注入到新会话的系统提示头部，替代完整的历史对话。
    目标长度 < 500 tokens。
    """
    ctx = state["current_context"]
    lines = [
        f"## [COMPACT MEMORY] Session State — {state['last_updated'][:10]}",
        "",
        "### 当前上下文",
        f"- **活跃 Agent**: {ctx['active_agent'] or '无'}",
        f"- **当前任务**: {ctx['active_task'] or '无'}",
        f"- **技术栈**: {', '.join(ctx['tech_stack']) or '未确定'}",
    ]

    if ctx["key_decisions"]:
        lines.append("\n### 关键决策")
        for d in ctx["key_decisions"]:
            lines.append(f"- {d}")

    if state["pending_tasks"]:
        lines.append("\n### 待处理任务")
        for t in state["pending_tasks"]:
            lines.append(f"- [ ] {t}")

    if ctx["open_questions"]:
        lines.append("\n### 未解决疑问")
        for q in ctx["open_questions"]:
            lines.append(f"- ? {q}")

    if state["resolved_issues"]:
        lines.append("\n### 近期已解决")
        for r in state["resolved_issues"][-3:]:  # 只展示最近 3 条
            lines.append(f"- [x] {r['text']}")

    if state["user_preferences_delta"]:
        lines.append("\n### 用户偏好变化（本 Session）")
        for p in state["user_preferences_delta"][-2:]:
            lines.append(f"- {p['text']}")

    lines.append(f"\n*压缩次数: {state['token_stats']['compaction_count']} | "
                 f"总轮次: {state['token_stats']['total_turns']}*")

    return "\n".join(lines)


def compact(diff: Optional[dict] = None) -> str:
    """
    主入口：执行一次增量压缩。
    - 如果提供 diff，则先应用差异再渲染摘要
    - 如果不提供 diff，则直接渲染当前状态的摘要
    返回渲染后的 Markdown 摘要字符串。
    """
    state = load_state()

    if diff:
        state = apply_diff(state, diff)
        save_state(state)

    summary = render_compact_summary(state)
    return summary


def reset_session(session_id: str = "") -> None:
    """开始新会话时重置状态（保留用户偏好 delta，清空其他）"""
    new_state = EMPTY_STATE.copy()
    new_state["session_id"] = session_id or hashlib.md5(
        datetime.now().isoformat().encode()
    ).hexdigest()[:8]
    new_state["current_context"] = {
        "active_agent": "",
        "active_task": "",
        "key_decisions": [],
        "tech_stack": [],
        "open_questions": []
    }
    save_state(new_state)
    print(f"[MemoryCompactor] 新会话已初始化: {new_state['session_id']}")


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_session()
    elif len(sys.argv) > 1 and sys.argv[1] == "demo":
        # 演示：模拟一次增量压缩
        demo_diff = {
            "resolved": ["修复了 npm build 缓存问题"],
            "add_pending": ["部署到 GitHub Pages", "编写 README"],
            "active_agent": "fe",
            "active_task": "构建产品落地页",
            "add_decisions": ["使用 Vite 替代 CRA 以提升构建速度"],
            "add_tech": ["Vite", "React", "TailwindCSS"],
            "add_questions": ["是否需要 SSR？"],
            "user_pref_delta": "用户偏好使用 Tailwind 而非 CSS Modules"
        }
        summary = compact(demo_diff)
        print(summary)
    else:
        # 默认：渲染当前状态
        summary = compact()
        print(summary)
