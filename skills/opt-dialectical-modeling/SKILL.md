# opt-dialectical-modeling: 辩证式用户建模

## 1. 技能简介

`opt-dialectical-modeling` 是 OPT 龙虾军团 v5.0 的用户画像管理技能，基于 Hermes Agent 的辩证式建模（Dialectical Modeling）理念设计。
它摒弃了传统的"累加式"画像，采用黑格尔的"正-反-合"（Thesis-Antithesis-Synthesis）逻辑，动态捕捉用户偏好的演变趋势。

## 2. 核心机制（Harness 层）

- **正题（Thesis）**：当前知识库中已有的用户画像（`USER_PROFILE.md`）。
- **反题（Antithesis）**：在最近的对话或任务中观察到的新行为、新偏好或矛盾点。
- **合题（Synthesis）**：使用 LLM 将正题和反题进行辩证融合，生成一个更高维度的、包含演变趋势的新画像。

## 3. 执行脚本示例

### 3.1 Python 辩证融合脚本 (`dialectical_merge.py`)

KO（知识管理员）可以使用此脚本更新用户画像：

```python
#!/usr/bin/env python3
# dialectical_merge.py - 辩证式用户画像融合脚本

import os
import sys
import datetime

PROFILE_PATH = "knowledge-base/profiles/USER_PROFILE.md"

def read_current_profile():
    """读取当前画像（正题）"""
    if not os.path.exists(PROFILE_PATH):
        return "No existing profile."
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def generate_synthesis(thesis, antithesis):
    """
    模拟 LLM 的辩证融合过程。
    在实际应用中，这里会调用 LLM API，传入 thesis 和 antithesis，
    要求其输出 synthesis。
    """
    print("[Dialectical Modeling] Calling LLM to synthesize...")
    # 这里是一个硬编码的示例输出
    synthesis = f"""# 用户画像 (更新于 {datetime.date.today().isoformat()})

## 核心身份与演变趋势
用户原本是一位偏好快速原型开发的 Python 开发者（正题），
但最近开始频繁关注 Rust 的内存安全和性能优化（反题）。
目前正处于从脚本语言向系统级编程语言转型的阶段（合题）。

## 沟通策略
- 在提供架构建议时，优先考虑高性能和内存安全的方案（如 Rust）。
- 在需要快速验证想法时，仍可提供 Python 脚本，但需说明其性能瓶颈。
"""
    return synthesis

def update_profile(antithesis):
    """执行辩证更新流程"""
    print("[Dialectical Modeling] Starting dialectical update...")
    
    thesis = read_current_profile()
    print(f"  - Thesis (Current Profile): {len(thesis)} chars")
    print(f"  - Antithesis (New Observation): {antithesis}")
    
    synthesis = generate_synthesis(thesis, antithesis)
    
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, 'w', encoding='utf-8') as f:
        f.write(synthesis)
        
    print(f"[Dialectical Modeling] Successfully updated {PROFILE_PATH}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dialectical_merge.py <new_observation>")
        sys.exit(1)
        
    new_observation = sys.argv[1]
    update_profile(new_observation)
```

## 4. 协作与触发

- **触发者**：KO（知识管理员）。
- **前置条件**：在 Auto Dream 期间，或 CoS 明确指出了用户偏好的重大变化。
- **输出结果**：更新后的 `USER_PROFILE.md`，包含最新的演变趋势。
