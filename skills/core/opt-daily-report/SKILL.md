# SKILL: opt-daily-report — 每日报告技能

## 1. 技能简介

本技能由 CoS 幕僚长在每天工作结束时触发，自动汇总当日所有 Agent 的工作成果，生成结构化的每日报告，并推送到 Slack 频道（如已配置）。

## 2. 适用场景

- 每日工作结束时的自动汇总。
- 追踪任务完成状态和阻塞点。
- 记录关键决策和下一步行动。
- 向 Slack 推送通知。

## 3. 报告生成脚本

```python
#!/usr/bin/env python3
"""
OPT v6.0 - 每日报告生成脚本
由 CoS 在每日工作结束时触发
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPT_WORKSPACE", Path.home() / "workspace"))
TODAY = datetime.now().strftime("%Y-%m-%d")

def collect_task_results() -> list[dict]:
    """收集今日所有任务结果"""
    results = []
    results_dir = WORKSPACE / "memory" / "workspace" / "results"
    
    for result_file in glob.glob(str(results_dir / f"*{TODAY}*.md")):
        with open(result_file, "r", encoding="utf-8") as f:
            content = f.read()
        results.append({
            "file": os.path.basename(result_file),
            "content": content[:300]
        })
    
    return results

def collect_escalations() -> list[dict]:
    """收集今日的 Escalation 记录"""
    escalations = []
    escalation_dir = WORKSPACE / "memory" / "workspace" / "escalations"
    
    for esc_file in glob.glob(str(escalation_dir / f"*{TODAY}*.md")):
        with open(esc_file, "r", encoding="utf-8") as f:
            content = f.read()
        escalations.append({
            "file": os.path.basename(esc_file),
            "content": content[:200]
        })
    
    return escalations

def generate_daily_report(results: list, escalations: list) -> str:
    """生成每日报告 Markdown"""
    report = f"""# OPT 每日报告 — {TODAY}

## 今日完成
{chr(10).join(f"- {r['file']}: {r['content'][:100]}..." for r in results) if results else "- 暂无记录"}

## 阻塞与升级
{chr(10).join(f"- ⚠️ {e['file']}: {e['content'][:100]}..." for e in escalations) if escalations else "- 无阻塞"}

## 明日计划
> 由 CoS 在对话结束前填写

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 保存报告
    report_dir = WORKSPACE / "memory" / "global" / "weekly_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / f"daily_report_{TODAY}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    return str(report_file)

def send_to_slack(report_content: str):
    """推送报告到 Slack（如已配置）"""
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL_ID")
    
    if not slack_token or not slack_channel:
        print("  ⚠️ Slack 未配置，跳过推送")
        return
    
    try:
        import urllib.request
        import urllib.parse
        
        payload = json.dumps({
            "channel": slack_channel,
            "text": f"🦞 OPT 每日报告 — {TODAY}\n```{report_content[:500]}```"
        }).encode("utf-8")
        
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=payload,
            headers={
                "Authorization": f"Bearer {slack_token}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get("ok"):
                print("  ✓ 已推送到 Slack")
            else:
                print(f"  ⚠️ Slack 推送失败: {result.get('error')}")
    except Exception as e:
        print(f"  ⚠️ Slack 推送异常: {e}")

if __name__ == "__main__":
    print(f"📊 生成每日报告 — {TODAY}")
    results = collect_task_results()
    escalations = collect_escalations()
    report_file = generate_daily_report(results, escalations)
    print(f"  ✓ 报告已生成: {report_file}")
    send_to_slack(open(report_file).read())
```

## 4. 触发方式

CoS 幕僚长在每次对话结束时，如果判断当日工作已完成，会自动调用本技能：

```
触发词：
- "今天就到这里"
- "收工"
- "明天继续"
- "生成今日报告"
```

## 5. 变更日志

- 2026-04-16: v1.0 初始版本，含 Slack 推送
