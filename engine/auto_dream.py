#!/usr/bin/env python3
"""
OPT v6.1 - Auto Dream: Memory Consolidation Engine (with Memory Drift Caveat)
基于 Hermes Agent 的自我进化机制和 Claude Code 的 Auto Dream 系统

v6.1 新增功能：
  - Memory Drift Caveat：为超过 24h 的记忆文件自动注入时间衰减警告标签
  - 与 memory_compactor.py 协作：Auto Dream 负责周级巩固，Compactor 负责实时压缩

触发时机：每周一凌晨 2:00 自动执行（通过 cron 或 openclaw scheduler）
手动执行：python3 engine/auto_dream.py
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))
MEMORY_DIR = WORKSPACE / "memory"
SKILLS_EVOLVED_DIR = WORKSPACE / "skills" / "evolved"

# ── Memory Drift Caveat 配置 ─────────────────────────────────────────────────
DRIFT_THRESHOLDS = {
    "warn":    timedelta(hours=24),    # 超过 24h：注入 STALE 警告
    "caution": timedelta(days=7),      # 超过 7d：注入 OUTDATED 警告
    "archive": timedelta(days=30),     # 超过 30d：自动归档到 memory/archive/
}

DRIFT_TAGS = {
    "warn":    "[⚠️ STALE MEMORY — {age} old. Verify against current code before asserting as fact.]",
    "caution": "[🔴 OUTDATED MEMORY — {age} old. This information may be significantly outdated. Cross-check required.]",
    "archive": "[📦 ARCHIVED — Moved to memory/archive/ after {age}. Do not use without explicit reload.]",
}

# 需要进行时间衰减检查的目录
DRIFT_SCAN_DIRS = [
    MEMORY_DIR / "global",
    MEMORY_DIR / "profiles",
    MEMORY_DIR / "session",
]


# ── Memory Drift Caveat 核心函数 ─────────────────────────────────────────────

def compute_file_age(file_path: Path) -> timedelta:
    """计算文件的实际年龄（基于最后修改时间）"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.now() - mtime


def format_age(age: timedelta) -> str:
    """将时间差格式化为人类可读字符串"""
    total_seconds = int(age.total_seconds())
    if total_seconds < 3600:
        return f"{total_seconds // 60}m"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}h"
    else:
        return f"{age.days}d"


def inject_drift_caveat(file_path: Path, age: timedelta, level: str) -> bool:
    """
    向记忆文件头部注入时间衰减警告标签。
    如果文件已经包含该标签，则更新标签内的年龄信息。
    返回 True 表示注入成功，False 表示跳过（已是最新标签）。
    """
    tag_prefix = f"[⚠️ STALE MEMORY" if level == "warn" else \
                 f"[🔴 OUTDATED MEMORY" if level == "caution" else \
                 f"[📦 ARCHIVED"

    age_str = format_age(age)
    new_tag = DRIFT_TAGS[level].format(age=age_str)

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return False

    # 检查是否已有同级别标签
    if tag_prefix in content:
        # 更新现有标签中的年龄信息
        lines = content.split("\n")
        updated_lines = []
        for line in lines:
            if tag_prefix in line:
                updated_lines.append(new_tag)
            else:
                updated_lines.append(line)
        file_path.write_text("\n".join(updated_lines), encoding="utf-8")
        return True

    # 注入新标签到文件顶部
    updated_content = new_tag + "\n\n" + content
    file_path.write_text(updated_content, encoding="utf-8")
    return True


def archive_stale_file(file_path: Path) -> Path:
    """将过期文件归档到 memory/archive/ 目录"""
    archive_dir = MEMORY_DIR / "archive" / datetime.now().strftime("%Y/%m")
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / file_path.name
    file_path.rename(archive_path)
    return archive_path


def run_drift_caveat_scan() -> dict:
    """
    扫描所有记忆目录，根据文件年龄注入对应级别的警告标签。
    返回扫描报告。
    """
    report = {
        "scanned": 0,
        "warn_injected": 0,
        "caution_injected": 0,
        "archived": 0,
        "details": []
    }

    for scan_dir in DRIFT_SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for md_file in scan_dir.glob("**/*.md"):
            age = compute_file_age(md_file)
            report["scanned"] += 1

            if age >= DRIFT_THRESHOLDS["archive"]:
                archive_path = archive_stale_file(md_file)
                report["archived"] += 1
                report["details"].append({
                    "file": str(md_file.name),
                    "action": "archived",
                    "age": format_age(age),
                    "new_path": str(archive_path)
                })
            elif age >= DRIFT_THRESHOLDS["caution"]:
                injected = inject_drift_caveat(md_file, age, "caution")
                if injected:
                    report["caution_injected"] += 1
                    report["details"].append({
                        "file": str(md_file.name),
                        "action": "caution_tag_injected",
                        "age": format_age(age)
                    })
            elif age >= DRIFT_THRESHOLDS["warn"]:
                injected = inject_drift_caveat(md_file, age, "warn")
                if injected:
                    report["warn_injected"] += 1
                    report["details"].append({
                        "file": str(md_file.name),
                        "action": "warn_tag_injected",
                        "age": format_age(age)
                    })

    return report


# ── 原有 Auto Dream 核心函数（v6.0 保留，v6.1 增强）────────────────────────

def load_recent_sessions(days: int = 7) -> list[dict]:
    """加载最近 N 天的会话记录"""
    sessions = []
    session_dir = MEMORY_DIR / "session"
    cutoff = datetime.now() - timedelta(days=days)

    for session_file in glob.glob(str(session_dir / "*.jsonl")):
        file_mtime = datetime.fromtimestamp(os.path.getmtime(session_file))
        if file_mtime > cutoff:
            with open(session_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        sessions.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

    return sessions


def extract_high_value_trajectories(sessions: list[dict]) -> list[dict]:
    """提取高价值的执行轨迹（成功解决复杂问题的记录）"""
    high_value = []

    for session in sessions:
        if (session.get("status") == "success" and
                session.get("retry_count", 0) > 0 and
                session.get("tool_name") in ["BashTool", "WriteFile", "EditFile"]):
            high_value.append(session)

    return high_value


def generate_skill_from_trajectory(trajectory: dict) -> tuple[str, str]:
    """从执行轨迹生成技能文档（SKILL.md 格式）"""
    skill_name = f"auto-{trajectory.get('task_name', 'unknown').replace(' ', '-').lower()}"
    timestamp = datetime.now().strftime("%Y-%m-%d")

    skill_content = f"""# SKILL: {trajectory.get('task_name', '自动提炼技能')}

## 1. 技能简介
本技能由 Auto Dream 引擎自动提炼，来源于 {timestamp} 的成功执行轨迹。

## 2. 适用场景
{trajectory.get('task_description', '待补充')}

## 3. 执行步骤
```bash
{trajectory.get('successful_command', '# 待补充')}
```

## 4. 注意事项
- 本技能经历了 {trajectory.get('retry_count', 0)} 次重试后成功，说明存在一定复杂度
- 执行前请确认环境变量已正确配置
- 如遇问题，请参考 TAOR 引擎的重试机制

## 5. 变更日志
- {timestamp}: 由 Auto Dream 自动生成 (v1.0)
"""
    return skill_name, skill_content


def dialectical_profile_update(old_profile: str, new_observations: list[str]) -> str:
    """辩证式用户画像更新（正-反-合）"""
    update_record = f"""
## Auto Dream 更新记录 ({datetime.now().strftime('%Y-%m-%d')})

### 正题（旧画像摘要）
{old_profile[:200]}...

### 反题（本周新观察）
{chr(10).join(f'- {obs}' for obs in new_observations)}

### 合题（待 KO 使用 LLM 生成辩证融合结果）
[需要 KO 使用 claude-3-7-sonnet 生成辩证融合结果]
"""
    return update_record


# ── Auto Dream 主流程（v6.1：新增 Drift Caveat 扫描步骤）──────────────────

def run_auto_dream() -> dict:
    """Auto Dream 主流程（v6.1 增强版）"""
    print(f"[Auto Dream v6.1] 开始执行 - {datetime.now().isoformat()}")

    # ── 步骤 0（v6.1 新增）：记忆时间衰减扫描 ──────────────────────────────
    print("[Auto Dream] 步骤 0: 执行 Memory Drift Caveat 扫描...")
    drift_report = run_drift_caveat_scan()
    print(f"  扫描文件: {drift_report['scanned']} | "
          f"STALE 标签: {drift_report['warn_injected']} | "
          f"OUTDATED 标签: {drift_report['caution_injected']} | "
          f"归档: {drift_report['archived']}")

    # ── 步骤 1：加载最近 7 天的会话记录 ────────────────────────────────────
    sessions = load_recent_sessions(days=7)
    print(f"[Auto Dream] 步骤 1: 加载了 {len(sessions)} 条会话记录")

    # ── 步骤 2：提取高价值轨迹 ──────────────────────────────────────────────
    trajectories = extract_high_value_trajectories(sessions)
    print(f"[Auto Dream] 步骤 2: 发现 {len(trajectories)} 条高价值轨迹")

    # ── 步骤 3：生成新技能 ──────────────────────────────────────────────────
    SKILLS_EVOLVED_DIR.mkdir(parents=True, exist_ok=True)
    for traj in trajectories:
        skill_name, skill_content = generate_skill_from_trajectory(traj)
        skill_dir = SKILLS_EVOLVED_DIR / skill_name
        skill_dir.mkdir(exist_ok=True)
        with open(skill_dir / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(skill_content)
        print(f"[Auto Dream] 步骤 3: 生成新技能: {skill_name}")

    # ── 步骤 4：保存 RL 轨迹数据 ────────────────────────────────────────────
    trajectories_dir = MEMORY_DIR / "trajectories"
    trajectories_dir.mkdir(exist_ok=True)
    traj_file = trajectories_dir / f"trajectories_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(traj_file, "a", encoding="utf-8") as f:
        for traj in trajectories:
            f.write(json.dumps(traj, ensure_ascii=False) + "\n")

    # ── 步骤 5：生成周报（v6.1：新增 drift_report 字段）────────────────────
    report = {
        "date": datetime.now().isoformat(),
        "version": "6.1",
        "sessions_analyzed": len(sessions),
        "high_value_trajectories": len(trajectories),
        "new_skills_generated": len(trajectories),
        "drift_caveat": drift_report,
        "status": "completed"
    }

    report_dir = MEMORY_DIR / "global" / "weekly_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"weekly_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"[Auto Dream v6.1] 完成！周报已保存到 {report_file}")
    return report


if __name__ == "__main__":
    run_auto_dream()
