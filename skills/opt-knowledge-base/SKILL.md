---
name: opt-knowledge-base
description: OPT 公司知识库管理技能。支持知识的存入、检索和更新，构建企业级 RAG 知识系统。
user-invocable: true
---

# OPT 知识库管理技能

## 功能说明

此技能帮助 AI Agent 管理 OPT 公司的知识库，实现知识的结构化存储和语义检索。

## 知识库结构

```
knowledge-base/
├── design/
│   ├── brand-guidelines.md    # 品牌规范
│   ├── ui-patterns.md         # UI 设计模式
│   ├── typography.md          # 排版规范
│   └── color-theory.md        # 色彩理论
├── tech/
│   ├── tech-stack.md          # 技术栈选型记录
│   ├── architecture-patterns.md # 架构模式
│   ├── deployment-guides.md   # 部署指南
│   └── api-integrations.md    # API 集成记录
├── business/
│   ├── pricing-strategy.md    # 定价策略
│   ├── client-management.md   # 客户管理
│   ├── project-templates.md   # 项目模板
│   └── sop.md                 # 标准作业程序
├── skills/
│   └── {技能名}.md            # 可复用技能文档
└── lessons-learned/
    └── {YYYY-MM}.md           # 月度踩坑记录
```

## 知识存入规范

当用户说"记住这个"、"保存到知识库"或完成一个新类型任务后，使用以下格式存入：

```markdown
## {知识标题}
**创建时间**：{YYYY-MM-DD}
**类型**：[原则 / 模式 / 踩坑 / SOP / 参考资料]
**标签**：[设计 / 技术 / 商业 / 流程]
**适用场景**：{一句话描述}

### 内容
{详细描述，包含具体步骤或示例}

### 注意事项
{使用时需要注意的点}

### 相关资源
{相关链接或文件路径}
```

## 知识检索规范

当用户提问时，先搜索知识库：
1. 使用 `memory_search` 工具进行语义搜索。
2. 若找到相关内容，优先基于知识库内容回答。
3. 若知识库中没有，明确告知用户，并建议是否需要调研后存入。

## 技能沉淀触发条件

当某个任务流程被成功执行 3 次以上，且每次流程基本相同时，触发技能沉淀：
1. 提炼流程为 SKILL.md 格式。
2. 存入 `skills/opt-{技能名}/SKILL.md`。
3. 通知 KO Agent 更新知识库索引。
