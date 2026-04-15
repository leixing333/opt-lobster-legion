# CHANGELOG — OPT 龙虾军团

本文件记录 OPT 龙虾军团各版本的重要变更，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

---

## [v7.1.0] — 2026-04-16 (Google Stitch + Nano Banana 集成)

### 新增
- `engine/stitch_client.py`（601行）：Google Stitch UI 生成客户端
  - `generate_ui(prompt, device_type)`：文本生成 UI 界面（支持 web/app）
  - `edit_screen(screen_id, prompt)`：用自然语言编辑现有界面
  - `generate_variants(prompt, n)`：生成 N 个设计变体（A/B 测试）
  - `full_pipeline(prompt)`：Stitch 生成 → 截图 → Nano Banana 增强 → 保存 HTML 完整流水线
  - `StitchScreen.get_html()`：获取界面 HTML/CSS 代码
  - 支持 Stitch SDK（Node.js）和 MCP 协议双通道，自动选择最佳方式
- `engine/nano_banana_client.py`（583行）：Nano Banana 图像生成客户端（基于 Gemini API）
  - `text_to_image(prompt)`：文本生成图像（支持宽高比、分辨率、负向提示词）
  - `image_to_image(prompt, reference)`：图像编辑（基于参考图 + 文本指令）
  - `multi_turn_edit(prompt)`：多轮对话式图像编辑会话
  - `generate_ui_assets(asset_type, description)`：专为 UI 设计生成图像资产（icon/illustration/background/hero/banner/avatar）
  - `generate_from_stitch(screenshot_path)`：Stitch 截图 → Nano Banana 增强视觉质量
  - `generate_design_variants(prompt, variants)`：批量生成设计变体
  - 支持三个模型：Nano Banana 2 / Nano Banana Pro / Nano Banana
- `engine/vision_parser.py`（v7.1 新增方法）：集成 Stitch 和 Nano Banana
  - `parse_from_stitch(prompt)`：Stitch 生成 UI → VisionParser 解析（联合流水线）
  - `generate_assets_with_nano_banana(parse_result)`：基于解析结果自动生成配套图像资产
  - `full_pipeline_v71(source)`：Stitch + VisionParser + Nano Banana 三方联合完整流水线

### 更新
- `config/openclaw.json` v7.1.0：新增 `stitch` 和 `nanaBanana` 配置块
  - Stitch：认证方式、默认设备类型、Agent 权限矩阵、流水线配置
  - Nano Banana：三个模型配置、Agent 权限矩阵、Stitch 集成配置

### 安装要求
```bash
# Stitch SDK（Node.js）
npm install -g @google/stitch-sdk

# Nano Banana（Python）
pip install google-genai pillow

# 环境变量
export STITCH_API_KEY=your_stitch_api_key
export GOOGLE_API_KEY=your_google_api_key
```

---

## [v7.0.0] — 2026-04-16 (多模态视觉 + MCP 权限路由)

### 新增
- `engine/vision_parser.py`（622行）：多模态视觉解析引擎，支持 GPT-4o / Claude 3.7 两种后端
  - `parse_design()`：解析 Figma 设计图，提取组件结构、设计 Token（颜色/字体/间距）
  - `generate_component()`：基于解析结果生成 React + TailwindCSS 组件代码（含测试文件和 README）
  - `compare_with_design()`：对比设计图与实现截图，生成视觉差异分析报告
  - `design_to_code_pipeline()`：一键完整流水线（解析 → 生成代码 → 生成 DESIGN_SYSTEM.md）
- `engine/mcp_router.py`（约350行）：统一 MCP 服务器权限路由器
  - 8 Agent × 5 MCP 服务器的完整权限矩阵（Jira/Slack/GitHub/Figma/Postgres）
  - Fail-closed 拦截：未授权调用立即抛出 `MCPPermissionError` 并记录到 KAIROS
  - `generate_permission_report()`：生成 Markdown 格式的权限矩阵报告
- `agents/fe/SOUL.md` v4.0：新增多模态视觉工作流（5步流程）和 MCP 权限表
- `agents/cos/SOUL.md` v4.0：新增 KAIROS 日志使用规范和 MCP 统一授权职责
- `config/openclaw.json` 新增 `vision` 和 `mcpRouter` 配置块

### 变更
- `config/openclaw.json` 版本号升至 `7.0.0`

---

## [v6.2.0] — 2026-04-16 (KAIROS 追加式日志系统)

### 新增
- `engine/kairos_daemon.py`：KAIROS 追加式日志守护进程，实现按天滚动的决策日志（`memory/kairos_logs/YYYY/MM/YYYY-MM-DD.md`）
- 支持 5 个日志级别：`DECISION`（决策）、`STATUS`（状态）、`ESCALATION`（升级）、`MILESTONE`（里程碑）、`NOTE`（备注）
- 每条日志记录带有时间戳锚点（`#anchor-HHMMSS`），支持精准定位
- `generate_daily_summary()` 方法：自动生成当日活动统计、里程碑和待处理升级事件摘要
- `search()` 方法：支持在最近 N 天的日志中全文搜索关键词
- `config/openclaw.json` 新增 `kairos` 配置块和 `scheduler.kairosDaily` 定时任务

### 变更
- `config/openclaw.json` 版本号升至 `6.2.0`

---

## [v6.1.0] — 2026-04-16 (记忆增强系统)

### 新增
- `engine/memory_compactor.py`：Session 增量压缩引擎，替代昂贵的 LLM 全量摘要（Closeout）
  - 维护结构化 JSON 状态机（目标 < 2KB），记录 `resolved_issues`、`pending_tasks`、`current_context`
  - `apply_diff()` 方法：每次交互后只更新增量差异，保持 Session Memory 大小恒定
  - `render_compact_summary()` 方法：渲染人类可读的 Markdown 摘要（目标 < 500 tokens），用于注入新会话头部
- `engine/auto_dream.py` 新增 Memory Drift Caveat 扫描（步骤 0）：
  - 超过 24h 的记忆文件：注入 `[⚠️ STALE MEMORY]` 警告标签
  - 超过 7d 的记忆文件：注入 `[🔴 OUTDATED MEMORY]` 警告标签
  - 超过 30d 的记忆文件：自动归档到 `memory/archive/YYYY/MM/`
- `config/openclaw.json` 新增 `memory.driftCaveat` 和 `memory.session.compactor` 配置块

### 变更
- `engine/auto_dream.py` 版本标注升至 `v6.1`，周报新增 `drift_caveat` 字段
- `config/openclaw.json` 版本号升至 `6.1.0`

---

## [v6.0.0] — 2026-04-16 (三大架构深度融合)

### 新增
- 完整的 8 Agent 架构：CoS, CTO, FE, BE, QA, Researcher, KO, Ops（从 v5.0 的 6 个 Builder 拆分）
- `engine/taor_loop.sh`：TAOR（Think-Act-Observe-Reflect）引擎，最多 3 次自动重试
- `engine/auto_dream.py`：Auto Dream 记忆巩固引擎，每周一凌晨 2:00 自动执行
- `hooks/pre_tool_use/permission_check.py`：工具调用前权限拦截器（Fail-closed）
- `hooks/post_tool_use/audit_logger.py`：工具调用后审计日志记录器（含敏感信息脱敏）
- `config/openclaw.json`：统一配置文件，含 MCP 服务器、权限矩阵、记忆配置
- 8 个核心技能（`skills/core/`）：autodream-memory, daily-report, rag-knowledge, security-audit, skill-evolution, taor-engine, web-publisher, auto-backup

### 架构基础
- **Claude Code**：TAOR 引擎 + Fail-closed 安全机制 + 上下文压缩
- **Hermes Agent**：技能自进化（Auto Dream）+ 辩证式用户建模（正-反-合）+ RL 轨迹收集
- **OpenHarness**：Hooks 机制（pre/post tool use）+ MCP 生态集成

---

## [v5.0.0] — 2026-04-15 (概念融合版)

### 主要特性
- 6 Agent 架构：CoS, CTO, Builder, Researcher, KO, Ops
- 引入 Claude Code、Hermes Agent、OpenHarness 三大架构的概念层面融合
- AGENTS.md 统一规范文件（v6.0 已内聚到各 SOUL.md）
- 基础的 Fail-closed 概念约束（v6.0 升级为代码级硬拦截）
