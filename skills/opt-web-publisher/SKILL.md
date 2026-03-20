---
name: opt-web-publisher
description: OPT 公司网站发布技能。支持将项目自动部署到 Vercel、GitHub Pages、Railway 等平台，实现一键发布。
user-invocable: true
---

# OPT 网站发布技能

## 功能说明

此技能帮助 Builder Agent 将开发完成的项目自动发布到各类托管平台。

## 支持的发布平台

| 平台 | 适用场景 | 费用 | 配置难度 |
|---|---|---|---|
| Vercel | 前端静态站、Next.js | 免费（个人）| 低 |
| GitHub Pages | 静态文档站、Portfolio | 免费 | 低 |
| Railway | 全栈应用、API 服务 | 按量计费 | 中 |
| Render | 后端服务 | 免费（有限制）| 中 |
| Cloudflare Pages | 静态站（全球加速）| 免费 | 低 |

## Vercel 发布流程

```bash
# 安装 Vercel CLI（若未安装）
npm install -g vercel

# 首次部署（交互式配置）
cd workspace/projects/{项目名}
vercel

# 生产环境部署
vercel --prod

# 设置环境变量
vercel env add {变量名}

# 查看部署状态
vercel ls
```

## GitHub Pages 发布流程

```bash
# 构建项目
pnpm build

# 部署到 GitHub Pages（使用 gh-pages 包）
pnpm add -D gh-pages

# 在 package.json 中添加脚本
# "deploy": "gh-pages -d dist"

pnpm deploy
```

## 发布前检查清单

在执行发布前，Builder 必须确认以下事项：
- [ ] `pnpm build` 无报错
- [ ] 所有环境变量已配置（`.env.example` 已更新）
- [ ] `README.md` 已更新（包含项目说明和访问地址）
- [ ] 无敏感信息（API Key、密码）硬编码在代码中
- [ ] 移动端适配已测试（响应式布局）
- [ ] 主要功能已在本地验证

## 发布后验证

```bash
# 检查网站可访问性
curl -I https://{部署URL}

# 检查关键页面响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://{部署URL}
```

发布完成后，在 `#build` 频道的 Thread 中汇报：
```
🚀 部署完成
- 平台：{Vercel / GitHub Pages / Railway}
- 访问地址：{URL}
- 部署时间：{时间}
- 构建耗时：{秒}
```
