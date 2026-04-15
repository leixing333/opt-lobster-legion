# Google Stitch 调研笔记

## 核心定位
- 官网：https://stitch.withgoogle.com/
- 定位：AI 驱动的 UI 设计工具（"Design at the speed of AI"）
- 功能：将自然语言 Prompt、手绘线框图、截图转化为完整可编辑的 UI 界面和生产级前端代码
- 状态：Beta 版，免费使用

## 核心能力
1. **文本生成 UI**：输入自然语言描述，自动生成 App/Web UI 设计
2. **截图转设计**：上传截图或手绘线框图，自动转化为可编辑设计
3. **多屏交互流**：支持创建多屏幕的交互式流程
4. **代码导出**：生成可运行的前端代码
5. **Figma 导出**：可将设计导出到 Figma
6. **MCP 集成**：支持 Model Context Protocol，允许 AI 编码 Agent（如 Anti-Gravity）直接连接 Stitch 设计，实现双向反馈循环

## MCP 集成详情
- Stitch 引入了 MCP 支持，允许外部 AI 编码 Agent 连接 Stitch 设计
- AI Agent 可以：查看 Stitch 设计、请求直接布局编辑、自动生成设计变体进行测试
- 无需在设计工具和代码编辑器之间手动切换上下文
- 这是一个双向反馈循环（two-way feedback loop）

## API/MCP 接口
- Stitch 提供 MCP 服务器接口
- 通过 MCP 协议与 AI Agent 通信
- 目前处于 Beta 阶段，具体 API 文档需要登录后查看

## 技术特点
- 使用 Gemini 3.0 Flash 模型（界面上有模型选择按钮）
- 支持 App（移动端）和 Web（网页端）两种设计模式
- 有预置模板：SaaS Dashboard、Health App、Entertainment App、Fashion App、Utility App

## 与 OPT 系统的集成思路
- 在 FE Agent 的工作流中，用 Stitch 替代或补充 Figma 作为设计来源
- 通过 MCP 协议让 FE Agent 直接读取/修改 Stitch 设计
- 流程：CoS 输入需求 → Stitch 生成 UI 设计 → FE 通过 MCP 读取设计 → VisionParser 解析 → 生成代码
- 可以用 Stitch 生成初版设计，再通过 Nano Banana 生成高质量图像资产注入设计
