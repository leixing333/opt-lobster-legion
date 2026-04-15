# SKILL: opt-autodream-memory — Auto Dream 记忆巩固技能

## 1. 技能简介

本技能实现了 Claude Code 源码中的 **Auto Dream（自动做梦）** 机制，结合 Hermes Agent 的**辩证式用户建模**，在系统空闲时（每周一凌晨 2:00）自动执行记忆整理、知识提炼和用户画像更新，让系统越用越聪明。

## 2. 适用场景

- KO 执行每周记忆巩固任务。
- 从 L0 会话记忆中提炼高价值知识到 L2 全局记忆。
- 更新用户画像（辩证式：正-反-合）。
- 识别可复用的成功模式，生成新技能草稿。
- 收集 RL 训练轨迹数据。

## 3. Auto Dream 执行脚本

```python
#!/usr/bin/env python3
"""
OPT v6.0 - Auto Dream 记忆巩固脚本
每周一凌晨 2:00 由 KO 执行
"""

import os
import glob
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", Path.home() / "workspace"))
MEMORY_DIR = WORKSPACE / "memory"
SESSION_DIR = MEMORY_DIR / "session"
GLOBAL_DIR = MEMORY_DIR / "global"
PROFILE_FILE = MEMORY_DIR / "profiles" / "USER_PROFILE.md"
TRAJECTORIES_DIR = MEMORY_DIR / "trajectories"

def collect_recent_sessions(days: int = 7) -> list[dict]:
    """收集过去 N 天的会话记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    sessions = []
    
    for session_file in glob.glob(str(SESSION_DIR / "closeout_*.md")):
        mtime = datetime.fromtimestamp(os.path.getmtime(session_file))
        if mtime > cutoff:
            with open(session_file, "r", encoding="utf-8") as f:
                content = f.read()
            sessions.append({
                "file": session_file,
                "date": mtime.strftime("%Y-%m-%d"),
                "content": content
            })
    
    return sorted(sessions, key=lambda x: x["date"], reverse=True)

def extract_key_decisions(sessions: list[dict]) -> list[str]:
    """从会话记忆中提取关键决策"""
    decisions = []
    decision_pattern = re.compile(r'(?:决策|决定|选择|采用|确定)[：:]\s*(.+)', re.MULTILINE)
    
    for session in sessions:
        matches = decision_pattern.findall(session["content"])
        decisions.extend([f"[{session['date']}] {m.strip()}" for m in matches])
    
    return decisions

def extract_skill_candidates(sessions: list[dict]) -> list[dict]:
    """识别可以提炼为技能的成功模式"""
    candidates = []
    
    # 寻找 TAOR 重试后成功的模式（高价值学习）
    retry_pattern = re.compile(r'重试.*?成功|第[2-3]次.*?成功|retry.*?success', re.IGNORECASE)
    
    for session in sessions:
        if retry_pattern.search(session["content"]):
            candidates.append({
                "date": session["date"],
                "source": session["file"],
                "type": "TAOR_SUCCESS",
                "content": session["content"][:500]
            })
    
    return candidates

def update_user_profile(sessions: list[dict]) -> str:
    """辩证式更新用户画像（正-反-合）"""
    if not PROFILE_FILE.exists():
        return "用户画像文件不存在，跳过更新"
    
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        current_profile = f.read()
    
    # 收集新观察
    observations = []
    for session in sessions[:5]:  # 只看最近 5 个会话
        # 寻找用户满意/不满意的信号
        if "✅" in session["content"] or "完成" in session["content"]:
            observations.append(f"[{session['date']}] 用户对输出表示满意")
        if "修改" in session["content"] or "不对" in session["content"]:
            observations.append(f"[{session['date']}] 用户要求修改，可能偏好有变化")
    
    if not observations:
        return "本周无新的用户偏好观察，画像保持不变"
    
    # 生成辩证式更新建议
    update_note = f"""
## 本周 Auto Dream 更新建议 ({datetime.now().strftime('%Y-%m-%d')})

### 新观察（反题）
{chr(10).join(observations)}

### 建议的合题更新
请 KO 根据以上观察，使用"正-反-合"逻辑更新用户画像。
"""
    
    # 追加到画像文件末尾
    with open(PROFILE_FILE, "a", encoding="utf-8") as f:
        f.write(update_note)
    
    return f"已追加 {len(observations)} 条新观察到用户画像"

def save_rl_trajectory(sessions: list[dict]) -> str:
    """保存 RL 训练轨迹数据"""
    TRAJECTORIES_DIR.mkdir(parents=True, exist_ok=True)
    
    trajectory_file = TRAJECTORIES_DIR / f"trajectories_{datetime.now().strftime('%Y%m%d')}.jsonl"
    
    count = 0
    with open(trajectory_file, "a", encoding="utf-8") as f:
        for session in sessions:
            # 简化的轨迹格式（实际 RL 训练需要更复杂的格式）
            trajectory = {
                "timestamp": session["date"],
                "source": os.path.basename(session["file"]),
                "content_length": len(session["content"]),
                "has_success": "完成" in session["content"] or "✅" in session["content"],
                "has_escalation": "ESCALATION" in session["content"]
            }
            f.write(json.dumps(trajectory, ensure_ascii=False) + "\n")
            count += 1
    
    return f"已保存 {count} 条轨迹到 {trajectory_file}"

def generate_weekly_report(sessions, decisions, candidates, profile_result, trajectory_result) -> str:
    """生成 Auto Dream 周报"""
    report_file = GLOBAL_DIR / "weekly_reports" / f"auto_dream_{datetime.now().strftime('%Y%m%d')}.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = f"""# Auto Dream 周报 — {datetime.now().strftime('%Y-%m-%d')}

## 执行摘要
- 处理会话数量: {len(sessions)}
- 提取关键决策: {len(decisions)} 条
- 识别技能候选: {len(candidates)} 个
- 用户画像更新: {profile_result}
- RL 轨迹收集: {trajectory_result}

## 关键决策摘要
{chr(10).join(f"- {d}" for d in decisions[:10]) if decisions else "本周无重要决策记录"}

## 技能候选（需要 KO 人工确认）
{chr(10).join(f"- [{c['date']}] {c['type']}: {c['content'][:100]}..." for c in candidates) if candidates else "本周无新的技能候选"}

## 下周建议
- 继续监控 TAOR 重试模式，寻找可提炼的技能
- 检查用户画像是否需要辩证式更新
- 审查技能库，删除过时的技能条目
"""
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    return str(report_file)

def run_auto_dream():
    """执行完整的 Auto Dream 流程"""
    print(f"🌙 Auto Dream 开始执行 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 收集最近会话
    sessions = collect_recent_sessions(days=7)
    print(f"  ✓ 收集到 {len(sessions)} 个会话记忆")
    
    # 2. 提取关键决策
    decisions = extract_key_decisions(sessions)
    print(f"  ✓ 提取到 {len(decisions)} 条关键决策")
    
    # 3. 识别技能候选
    candidates = extract_skill_candidates(sessions)
    print(f"  ✓ 识别到 {len(candidates)} 个技能候选")
    
    # 4. 更新用户画像
    profile_result = update_user_profile(sessions)
    print(f"  ✓ 用户画像: {profile_result}")
    
    # 5. 保存 RL 轨迹
    trajectory_result = save_rl_trajectory(sessions)
    print(f"  ✓ RL 轨迹: {trajectory_result}")
    
    # 6. 生成周报
    report_file = generate_weekly_report(sessions, decisions, candidates, profile_result, trajectory_result)
    print(f"  ✓ 周报已生成: {report_file}")
    
    print(f"\n🌅 Auto Dream 执行完成 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_auto_dream()
```

## 4. 定时任务配置

```bash
# 添加到 crontab（每周一凌晨 2:00 执行）
crontab -e
# 添加以下行：
# 0 2 * * 1 cd /path/to/opt-v6 && python3 engine/auto_dream.py >> /tmp/auto_dream.log 2>&1
```

## 5. 错误处理

| 错误 | 原因 | 解决方案 |
|---|---|---|
| `FileNotFoundError` | 记忆目录不存在 | 运行 `./deploy.sh` 初始化目录 |
| `PermissionError` | 文件权限问题 | 检查 `memory/` 目录权限 |
| 会话数量为 0 | 本周没有使用系统 | 正常，跳过执行 |

## 6. 变更日志

- 2026-04-16: v1.0 初始版本，基于 Claude Code Auto Dream 机制设计
- 2026-04-16: v1.1 增加辩证式用户建模（Hermes Agent）
- 2026-04-16: v1.2 增加 RL 轨迹收集功能
