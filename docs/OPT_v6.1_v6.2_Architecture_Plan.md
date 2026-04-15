# OPT 龙虾军团 v6.1 & v6.2 架构演进与开发规划

## 1. 完整架构目录树 (包含 v6.1/v6.2 新增规划)

基于 v6.0 的现有架构，我们将引入记忆时间衰减、Session 增量压缩（v6.1）以及 KAIROS 追加式日志系统（v6.2）。以下是演进后的完整目录结构（带有 `[NEW]` 标记的为本次规划新增或重点修改的文件）：

```text
opt-v6/
├── .env.example
├── .gitignore
├── README.md
├── deploy.sh
├── config/
│   └── openclaw.json                 # [MODIFIED] 增加 KAIROS 和 Memory Drift 配置
├── docs/
│   ├── OpenClaw_Lobster_Legion_Guide_v6.md
│   ├── OPT_v5_vs_v6_Analysis_Report.md
│   └── OPT_v6.1_v6.2_Architecture_Plan.md  # [NEW] 本规划文档
├── agents/
│   ├── cos/SOUL.md                   # [MODIFIED] 增加 KAIROS 模式指令
│   ├── ko/SOUL.md                    # [MODIFIED] 增加记忆衰减与增量压缩职责
│   ├── cto/SOUL.md
│   ├── fe/SOUL.md
│   ├── be/SOUL.md
│   ├── qa/SOUL.md
│   ├── researcher/SOUL.md
│   └── ops/SOUL.md
├── engine/
│   ├── taor_loop.sh
│   ├── auto_dream.py                 # [MODIFIED] 增加时间衰减标签逻辑
│   ├── memory_compactor.py           # [NEW] v6.1: Session 增量压缩引擎
│   └── kairos_daemon.py              # [NEW] v6.2: KAIROS 追加式日志守护进程
├── hooks/
│   ├── pre_tool_use/
│   │   └── permission_check.py
│   └── post_tool_use/
│   │   └── audit_logger.py
├── memory/                           # [MODIFIED] 目录结构调整以支持 KAIROS
│   ├── global/
│   │   └── A2A_PROTOCOL.md
│   ├── profiles/
│   │   └── USER_PROFILE.md
│   ├── session/                      # 存放短期会话
│   ├── trajectories/                 # 存放 RL 轨迹
│   └── kairos_logs/                  # [NEW] v6.2: KAIROS 追加式日志目录
│       └── YYYY/
│           └── MM/
│               └── YYYY-MM-DD.md
└── skills/
    ├── core/
    │   ├── opt-autodream-memory/SKILL.md
    │   ├── opt-daily-report/SKILL.md
    │   ├── opt-rag-knowledge/SKILL.md
    │   ├── opt-security-audit/SKILL.md
    │   ├── opt-skill-evolution/SKILL.md
    │   ├── opt-taor-engine/SKILL.md
    │   ├── opt-web-publisher/SKILL.md
    │   └── opt-auto-backup/SKILL.md
    └── evolved/                      # Auto Dream 自动生成的技能
```

## 2. v6.1 开发规划：记忆增强系统

v6.1 的核心目标是解决长周期项目中的"记忆漂移"（Memory Drift）和"上下文爆炸"问题。

### 2.1 记忆时间衰减 (Memory Drift Caveat)
- **原理**：当 Agent 读取超过 24 小时的记忆文件时，系统自动在内容顶部注入警告标签，强制模型在采信前进行验证。
- **实现方式**：修改 `engine/auto_dream.py`，增加一个定时扫描任务，为旧文件注入 `[WARNING: STALE MEMORY - Verify against current code before asserting as fact]`。

### 2.2 Session 增量压缩 (Incremental Compaction)
- **原理**：替代 v6.0 中昂贵的 LLM 全量摘要（Closeout）。引入结构化的笔记对象，每次交互后只更新增量差异（Diff），保持 Session Memory 的大小恒定。
- **实现方式**：新增 `engine/memory_compactor.py`，提供轻量级的 JSON 状态机，记录 `resolved_issues`、`pending_tasks` 和 `current_context`。

## 3. v6.2 开发规划：KAIROS 日志系统

v6.2 的核心目标是为 CoS 引入类似 Claude Code 的 KAIROS 长会话助理模式。

### 3.1 KAIROS 追加式日志 (Append-only Logging)
- **原理**：放弃覆盖式更新（Overwrite），采用按天滚动的追加式日志（`logs/YYYY/MM/YYYY-MM-DD.md`）。这保留了完整的决策时间线，方便老板随时查阅历史上下文。
- **实现方式**：新增 `engine/kairos_daemon.py` 守护进程。拦截 CoS 的所有关键决策和状态变更，自动追加到当天的 Markdown 日志中，并生成时间戳锚点。

## 4. 下一步执行步骤

1. **Phase 3**：编写 `engine/memory_compactor.py`，实现增量压缩逻辑；修改 `engine/auto_dream.py` 加入时间衰减算法。
2. **Phase 4**：编写 `engine/kairos_daemon.py`，实现按天滚动的追加式日志；更新 `config/openclaw.json`。
3. **Phase 5**：更新 CHANGELOG，交付最终代码。
