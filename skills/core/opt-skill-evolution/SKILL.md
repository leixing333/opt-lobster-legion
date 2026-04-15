# SKILL: opt-skill-evolution — 技能自进化引擎

## 1. 技能简介

本技能是 OPT v6.0 系统中最核心的自我进化机制，直接来源于 Hermes Agent 的闭环学习系统。它实现了一个正反馈循环：**创建技能 → 使用技能 → 发现改进点 → 更新技能 → 下次使用更好的版本**。

## 2. 技能生命周期

```
发现可复用模式
      ↓
创建 SKILL.md (v1.0)
      ↓
KO 索引到知识库
      ↓
Agent 使用技能
      ↓
记录使用结果（成功/失败/改进建议）
      ↓
KO 在 Auto Dream 中分析使用记录
      ↓
更新 SKILL.md (v1.1, v2.0...)
      ↓
（循环）
```

## 3. 技能创建规范

每个 `SKILL.md` 必须包含以下必填字段：

```markdown
# SKILL: {技能名称}

## 1. 技能简介
{一句话描述这个技能解决什么问题}

## 2. 适用场景
- 场景 1：{具体的触发条件}
- 场景 2：{具体的触发条件}

## 3. 执行步骤
{详细的步骤说明，包含命令示例}

## 4. 错误处理
{常见错误及解决方案}

## 5. 变更日志
- {日期}: v{版本号} {变更说明}
```

## 4. 技能质量评分脚本

```python
#!/usr/bin/env python3
"""
评估技能文件的质量，确保技能不是空壳
"""

import os
import glob
from pathlib import Path

SKILLS_DIR = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace")) / ".." / "skills"

REQUIRED_SECTIONS = [
    "## 1.",  # 技能简介
    "## 2.",  # 适用场景
    "## 3.",  # 执行步骤
    "## 4.",  # 错误处理
    "## 5.",  # 变更日志
]

MIN_LINES = 50  # 最少行数，确保内容充实

def evaluate_skill(skill_file: str) -> dict:
    """评估单个技能文件的质量"""
    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split("\n")
    score = 0
    issues = []
    
    # 检查必填章节
    for section in REQUIRED_SECTIONS:
        if section in content:
            score += 20
        else:
            issues.append(f"缺少章节: {section}")
    
    # 检查内容充实度
    if len(lines) >= MIN_LINES:
        score += 0  # 已满分
    else:
        issues.append(f"内容不足（{len(lines)} 行，最少需要 {MIN_LINES} 行）")
    
    # 检查是否有代码示例
    if "```" in content:
        score += 0  # 有代码示例是加分项
    else:
        issues.append("缺少代码示例（建议添加 ```bash 或 ```python 代码块）")
    
    return {
        "file": skill_file,
        "score": score,
        "lines": len(lines),
        "issues": issues,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C"
    }

def audit_all_skills():
    """审计所有技能文件"""
    results = []
    for skill_file in glob.glob(str(SKILLS_DIR / "**/SKILL.md"), recursive=True):
        results.append(evaluate_skill(skill_file))
    
    print(f"共审计 {len(results)} 个技能文件\n")
    for r in sorted(results, key=lambda x: x["score"]):
        grade_emoji = "✅" if r["grade"] == "A" else "⚠️" if r["grade"] == "B" else "❌"
        print(f"{grade_emoji} [{r['grade']}] {os.path.basename(os.path.dirname(r['file']))} ({r['lines']} 行)")
        for issue in r["issues"]:
            print(f"   → {issue}")

if __name__ == "__main__":
    audit_all_skills()
```

## 5. 触发技能进化的条件

以下情况必须触发技能进化：

| 触发条件 | 执行者 | 操作 |
|---|---|---|
| TAOR 循环经历 2+ 次重试后成功 | Builder/BE/FE | 创建新技能，记录成功路径 |
| 同一类型的问题第 3 次出现 | 任何 Agent | 提炼通用解决方案为技能 |
| 发现现有技能有错误或过时 | 任何 Agent | 更新技能版本，记录变更日志 |
| Auto Dream 发现高频成功模式 | KO | 自动生成技能草稿，通知相关 Agent 完善 |

## 6. 变更日志

- 2026-04-16: v1.0 初始版本，基于 Hermes Agent 闭环学习系统设计
- 2026-04-16: v1.1 增加技能质量评分脚本
