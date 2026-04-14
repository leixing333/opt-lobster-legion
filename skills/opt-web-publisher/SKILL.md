# OPT 网站发布技能

## 技能描述
本技能为 Builder 提供一套标准的网站发布流程，支持将静态网站部署到 GitHub Pages、Vercel 或 Netlify。

## 支持的部署平台

| 平台 | 适用场景 | 命令 |
|---|---|---|
| GitHub Pages | 开源项目展示、文档站 | `git push origin gh-pages` |
| Vercel | 前端应用、Next.js 项目 | `vercel --prod` |
| Netlify | 静态站点、表单处理 | `netlify deploy --prod` |

## 执行流程

### 1. 构建检查（Build Check）
在部署前，Builder 必须确认以下事项：
- 所有静态资源（图片、字体、CSS）已正确引用。
- 所有外部链接已更新为真实 URL（无 `your-name` 占位符）。
- 网站在本地 `python3 -m http.server 8080` 中预览无误。

### 2. GitHub Pages 部署流程
```bash
# 初始化 gh-pages 分支
git checkout --orphan gh-pages
git reset --hard
git add -A && git commit -m "deploy: 初始化 GitHub Pages"
git push origin gh-pages

# 通过 GitHub API 启用 Pages
curl -X POST -H "Authorization: token $BACKUP_GITHUB_TOKEN" \
  https://api.github.com/repos/{owner}/{repo}/pages \
  -d '{"source":{"branch":"gh-pages","path":"/"}}'
```

### 3. 验证部署
部署完成后，等待约 60 秒，访问 `https://{username}.github.io/{repo}/` 验证网站是否正常。

## 注意事项
所有部署操作需要 CoS（幕僚长）的显式确认，防止误操作覆盖生产环境。
