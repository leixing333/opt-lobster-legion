# SKILL: opt-rag-knowledge — RAG 知识库检索技能

## 1. 技能简介

本技能基于 OpenHarness 的 Memory 子系统和 Hermes Agent 的知识管理机制，实现了一套轻量级的 RAG（检索增强生成）知识库系统。核心设计哲学：**用 Markdown 文件而非向量数据库**，确保知识库对人类可读、可编辑、可审计。

## 2. 适用场景

- Agent 在执行任务前，检索相关的历史解决方案。
- KO 在执行 Auto Dream 时，检索相似的技能模板。
- CoS 在派单前，检索类似任务的历史执行轨迹。

## 3. 知识库目录结构

```
memory/
├── global/           # 全局知识（跨项目通用）
│   ├── DESIGN_PRINCIPLES.md
│   ├── TECH_DEBT.md
│   ├── ADR/          # 架构决策记录
│   └── weekly_reports/
├── profiles/         # 用户画像
│   └── USER_PROFILE.md
├── session/          # 会话记忆（L0，最近 30 天）
│   └── closeout_*.md
├── workspace/        # 工作区记忆（L1，项目级）
│   ├── tasks/
│   ├── results/
│   └── escalations/
└── trajectories/     # RL 轨迹数据（L3）
    └── trajectories_*.jsonl
```

## 4. 检索脚本（可直接执行）

```python
#!/usr/bin/env python3
"""
OPT v6.0 - RAG Knowledge Retrieval
轻量级关键词检索，无需向量数据库
"""

import os
import glob
import re
from pathlib import Path

MEMORY_DIR = Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace")) / "memory"

def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """
    在知识库中搜索相关内容
    使用 TF-IDF 风格的关键词匹配（无需外部依赖）
    """
    keywords = query.lower().split()
    results = []
    
    # 搜索所有 Markdown 文件
    for md_file in glob.glob(str(MEMORY_DIR / "**/*.md"), recursive=True):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            content_lower = content.lower()
            
            # 计算关键词匹配分数
            score = sum(content_lower.count(kw) for kw in keywords)
            
            if score > 0:
                # 提取最相关的片段（包含最多关键词的段落）
                paragraphs = content.split("\n\n")
                best_para = max(paragraphs, 
                               key=lambda p: sum(p.lower().count(kw) for kw in keywords))
                
                results.append({
                    "file": md_file,
                    "score": score,
                    "snippet": best_para[:300],
                    "relative_path": os.path.relpath(md_file, MEMORY_DIR)
                })
        except Exception:
            continue
    
    # 按分数排序，返回 top_k 结果
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def format_results(results: list[dict]) -> str:
    """格式化检索结果为 Markdown"""
    if not results:
        return "未找到相关知识。"
    
    output = ["## 知识库检索结果\n"]
    for i, result in enumerate(results, 1):
        output.append(f"### {i}. {result['relative_path']} (相关度: {result['score']})")
        output.append(f"```\n{result['snippet']}\n```\n")
    
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "TAOR 引擎"
    results = search_knowledge(query)
    print(format_results(results))
```

## 5. 使用方式

```bash
# 在命令行中检索
python3 skills/core/opt-rag-knowledge/retrieve.py "TAOR 引擎 重试"

# 在 Agent 中调用
/rag:search "用户登录 JWT 认证"
/rag:index   # 重建知识库索引
```

## 6. 知识沉淀规范

每次 Agent 完成重要任务后，必须将关键知识沉淀到知识库：

```markdown
# 知识条目模板
**日期**: {YYYY-MM-DD}
**类型**: 解决方案 / 架构决策 / 踩坑记录
**关键词**: {用于检索的关键词列表}
**问题描述**: {遇到的问题}
**解决方案**: {如何解决的}
**适用范围**: {在什么情况下可以复用}
**置信度**: ⭐⭐⭐⭐⭐ (1-5星)
**有效期**: {到期日期，超过后需重新验证}
```

## 7. 变更日志

- 2026-04-16: v1.0 初始版本，基于 OpenHarness Memory 子系统设计
- 2026-04-16: v1.1 增加 RL 轨迹数据目录支持（Hermes Agent）
