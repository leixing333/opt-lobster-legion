# opt-skill-evolution: 技能自进化引擎

## 1. 技能简介

`opt-skill-evolution` 是 OPT 龙虾军团 v5.0 的核心进化机制，基于 Hermes Agent 的自我改进（Self-Improvement）架构设计。
它允许 Agent 在执行任务的过程中，发现重复的成功模式，并将其自动提炼为新的 `SKILL.md` 文件，从而实现系统能力的持续增长。

## 2. 核心机制（Harness 层）

- **发现（Discover）**：在执行任务时，如果某个复杂的命令组合或代码片段被成功执行多次，Agent 应意识到这是一个"可复用模式"。
- **提炼（Distill）**：使用 LLM 将该模式抽象化，提取参数，编写标准化的执行步骤。
- **生成（Generate）**：按照 `agentskills.io` 的标准格式，生成新的 `SKILL.md` 文件。
- **注册（Register）**：将新技能注册到知识库索引中，供其他 Agent 调用。

## 3. 执行脚本示例

### 3.1 Python 技能生成器 (`skill_generator.py`)

Builder 或 KO 可以使用此脚本将成功模式转化为标准技能文件：

```python
#!/usr/bin/env python3
# skill_generator.py - 技能自进化生成器

import os
import sys
import datetime

SKILLS_DIR = "skills"

def generate_skill_md(skill_name, description, trigger, steps, example_code):
    """
    生成标准化的 SKILL.md 文件。
    """
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    
    filepath = os.path.join(skill_dir, "SKILL.md")
    
    content = f"""# {skill_name}

## 1. 技能简介
{description}

## 2. 触发条件
{trigger}

## 3. 执行步骤
{steps}

## 4. 执行脚本示例
```bash
{example_code}
```

## 5. 变更日志
- {datetime.date.today().isoformat()} v1.0: 由 opt-skill-evolution 自动生成。
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"[Skill Evolution] Successfully generated new skill: {filepath}")
    return filepath

if __name__ == "__main__":
    # 示例用法（在实际中，这些参数由 LLM 提炼生成）
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        generate_skill_md(
            skill_name="opt-demo-skill",
            description="这是一个自动生成的演示技能。",
            trigger="当需要演示技能进化时触发。",
            steps="1. 运行脚本\n2. 观察输出",
            example_code="echo 'Hello, Evolution!'"
        )
    else:
        print("Usage: python3 skill_generator.py --demo")
```

## 4. 协作与触发

- **触发者**：Builder（发现代码模式）、KO（在 Auto Dream 期间发现重复模式）。
- **前置条件**：某个复杂操作被成功执行 3 次以上，且具有通用性。
- **输出结果**：在 `skills/` 目录下生成新的技能文件夹和 `SKILL.md`。
