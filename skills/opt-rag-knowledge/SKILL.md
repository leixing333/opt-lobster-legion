# opt-rag-knowledge: RAG 知识检索

## 1. 技能简介

`opt-rag-knowledge` 是 OPT 龙虾军团 v5.0 的知识检索技能，基于 OpenHarness 的 RAG（Retrieval-Augmented Generation）机制设计。
它允许 Agent 在遇到未知问题或需要参考历史经验时，从 `knowledge-base/` 目录中检索相关信息，并将其作为上下文注入到当前对话中。

## 2. 核心机制（Harness 层）

- **向量化（Vectorize）**：将知识库中的 Markdown 文件转换为向量表示（在实际实现中，可使用轻量级的本地向量数据库如 ChromaDB 或 FAISS）。
- **检索（Retrieve）**：根据用户的查询，计算相似度并召回最相关的知识片段。
- **注入（Inject）**：将召回的知识片段格式化后，作为上下文注入到 Agent 的 Prompt 中。

## 3. 执行脚本示例

### 3.1 Python 检索脚本 (`rag_search.py`)

KO（知识管理员）或其他 Agent 可以使用此脚本进行知识检索：

```python
#!/usr/bin/env python3
# rag_search.py - 简单的基于关键字的 RAG 检索脚本（可扩展为向量检索）

import os
import sys
import glob

KB_DIR = "knowledge-base"

def search_knowledge_base(query):
    """
    在知识库中搜索包含查询关键字的文件。
    """
    print(f"[RAG] Searching for '{query}' in {KB_DIR}...")
    
    results = []
    # 遍历知识库中的所有 Markdown 文件
    for filepath in glob.glob(f"{KB_DIR}/**/*.md", recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if query.lower() in content.lower():
                # 提取包含关键字的上下文片段（前后 100 个字符）
                index = content.lower().find(query.lower())
                start = max(0, index - 100)
                end = min(len(content), index + 100)
                snippet = content[start:end].replace('\n', ' ')
                
                results.append({
                    'file': filepath,
                    'snippet': f"...{snippet}..."
                })
                
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 rag_search.py <query>")
        sys.exit(1)
        
    query = sys.argv[1]
    results = search_knowledge_base(query)
    
    if not results:
        print(f"[RAG] No results found for '{query}'.")
    else:
        print(f"[RAG] Found {len(results)} results:")
        for res in results:
            print(f"\n- File: {res['file']}")
            print(f"  Snippet: {res['snippet']}")
```

## 4. 协作与触发

- **触发者**：任何需要参考历史经验的 Agent（如 Builder 遇到未知错误，CTO 需要参考设计原则）。
- **前置条件**：遇到未知问题，或需要确保决策符合团队规范。
- **输出结果**：相关的知识片段，作为上下文注入到当前任务中。
