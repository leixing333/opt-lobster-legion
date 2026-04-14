# 技能：OPT RAG 知识库检索系统

## 简介
本技能为 OPT 龙虾军团提供**检索增强生成（RAG）**能力，允许 Agent 在回答问题或执行任务时，主动从 `knowledge-base/` 目录中检索相关的历史经验、设计规范和代码模式，而不是依赖模型的内置知识。

## 适用角色
**KO**（主要）、**CoS**、**CTO**、**Builder**（均可调用）

## 触发条件
- 当 Agent 需要回答关于"我们之前是怎么做 X 的？"类型的问题时。
- 当 Builder 遇到技术难题，需要查找历史解决方案时。
- 当 CoS 需要了解老板的历史偏好或项目背景时。

## 执行步骤

### 步骤 1：构建检索查询（Query Construction）
将用户的问题或任务转化为精准的检索关键词：
- **好的查询**：`"GitHub Pages 部署失败 403 权限"` → 关键词：`GitHub Pages`, `403`, `权限`
- **差的查询**：`"网站不能用了"` → 过于模糊，需要先澄清

### 步骤 2：分层检索（Layered Search）
按照以下优先级顺序检索知识库：

| 优先级 | 检索目录 | 适用场景 |
|---|---|---|
| 1（最高）| `knowledge-base/errors/` | 查找已知错误的解决方案 |
| 2 | `knowledge-base/patterns/` | 查找可复用的代码模式 |
| 3 | `knowledge-base/principles/` | 查找设计规范和原则 |
| 4 | `knowledge-base/projects/` | 查找项目历史和决策背景 |
| 5（最低）| `skills/` 目录 | 查找可直接执行的技能 |

```bash
# 在知识库中搜索关键词
grep -r "关键词" ./knowledge-base/ --include="*.md" -l
grep -r "关键词" ./knowledge-base/ --include="*.md" -n
```

### 步骤 3：相关性评估（Relevance Scoring）
对检索结果进行相关性评估，选择最相关的 1-3 个结果：
- **高相关**：标题或第一段直接包含查询关键词。
- **中相关**：内容中提到了相关概念，但不是直接答案。
- **低相关**：只是偶尔提到，不具有参考价值。

### 步骤 4：上下文注入（Context Injection）
将检索到的相关内容以 Markdown 引用块的形式注入到当前对话上下文中：
```markdown
> **[来自知识库：knowledge-base/errors/github-pages-403.md]**
> 解决方案：将 GitHub Pages 的 Source 从 `main` 分支切换到 `gh-pages` 分支，
> 并添加 `.nojekyll` 文件禁用 Jekyll 处理。
```

## 知识库目录结构
- `knowledge-base/principles/`：设计原则和架构规范。
- `knowledge-base/patterns/`：代码模式和配置模板。
- `knowledge-base/errors/`：错误记录和解决方案。
- `knowledge-base/projects/`：历史项目经验和总结。
- `knowledge-base/profiles/`：用户画像（USER_PROFILE.md）。

## 注意事项与避坑指南
- **知识库优先于模型内置知识**：当知识库中有相关内容时，必须优先使用知识库的内容。
- **标注来源**：在引用知识库内容时，必须标注来源文件路径，方便追溯和更新。
- **及时更新**：如果检索到的内容已经过时，必须在使用后通知 KO 更新对应的知识库文件。

## 变更日志
- 2026-04-15 v4.0：重写，增加分层检索优先级表、相关性评估标准和上下文注入示例。
