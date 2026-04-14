# 技能：OPT 网站发布系统

## 简介
本技能为 Builder 提供**一键网站发布**能力，支持将静态网站部署到 GitHub Pages，实现永久免费托管。它包含完整的构建、验证、推送和回滚流程，确保每次发布都是安全可靠的。

## 适用角色
**Builder**（主要）

## 触发条件
- 当 CoS 明确授权发布新版本网站时。
- 当 Builder 完成网站开发并通过本地预览验证后。
- 当需要紧急修复线上 Bug 时。

## 前置准备
- 已配置 Git 和 GitHub 账号。
- 已在 `.env` 中设置 `GITHUB_TOKEN`（需要 `repo` 权限）。
- 已在 GitHub 上创建目标仓库，并开启 GitHub Pages。

## 支持的部署平台

| 平台 | 适用场景 | 命令 |
|---|---|---|
| GitHub Pages | 开源项目展示、文档站 | `git push origin gh-pages` |
| Vercel | 前端应用、Next.js 项目 | `vercel --prod` |
| Netlify | 静态站点、表单处理 | `netlify deploy --prod` |

## 执行步骤

### 步骤 1：本地预览验证（Preview）
在发布前，必须先在本地预览确认效果：
```bash
# 启动本地服务器
cd ./workspace/builder/website
python3 -m http.server 8080
# 在浏览器中访问 http://localhost:8080 进行验证
```

### 步骤 2：构建检查（Build Check）
检查 HTML/CSS/JS 文件是否有明显错误：
```bash
# 检查关键链接是否正确（替换 your-repo 为实际仓库名）
grep -r "your-name\|your-repo\|placeholder" . --include="*.html" && \
  echo "⚠️  警告：发现未替换的占位符！" || \
  echo "✅ 链接检查通过"

# 确保 .nojekyll 文件存在（禁用 Jekyll 处理）
touch .nojekyll
echo "✅ .nojekyll 文件已添加"
```

### 步骤 3：推送到 GitHub（Push）
```bash
# 确保在正确的分支
git checkout gh-pages 2>/dev/null || git checkout -b gh-pages

# 添加所有文件
git add .

# 提交（使用有意义的提交信息）
DEPLOY_TIME=$(date +"%Y-%m-%d %H:%M")
git commit -m "deploy: 更新网站 - ${DEPLOY_TIME}"

# 推送到 GitHub
git push origin gh-pages
echo "推送完成，等待 GitHub Pages 构建（约 60 秒）..."
```

### 步骤 4：验证发布结果（Verify）
```bash
# 等待构建
sleep 60

# 检查网站是否可以访问
SITE_URL="https://leixing333.github.io/opt-lobster-legion/"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${SITE_URL}")

if [ "${HTTP_STATUS}" = "200" ]; then
  echo "✅ 发布成功！网站地址：${SITE_URL}"
else
  echo "❌ 发布失败，HTTP 状态码：${HTTP_STATUS}"
fi
```

### 步骤 5：发布报告（Report）
向 CoS 汇报发布结果：
```markdown
## 网站发布报告 - YYYY-MM-DD HH:MM

- **发布状态**：✅ 成功 / ❌ 失败
- **网站地址**：https://leixing333.github.io/opt-lobster-legion/
- **主要变更**：[简要描述本次更新的内容]
```

## 回滚流程（Rollback）
如果发布后发现问题，立即回滚到上一个版本：
```bash
# 查看最近的提交历史
git log --oneline -10

# 回滚到上一个版本
git revert HEAD
git push origin gh-pages
echo "已回滚到上一个版本"
```

## 注意事项与避坑指南
- **必须先本地验证**：在推送到 GitHub 前，必须先在本地预览确认效果，绝不盲目发布。
- **检查占位符**：在发布前，必须检查 HTML 文件中是否有未替换的占位符（如 `your-name`、`your-repo`）。
- **添加 .nojekyll**：如果网站不使用 Jekyll，必须在根目录添加 `.nojekyll` 文件，否则 GitHub Pages 会尝试用 Jekyll 处理文件。
- **等待构建**：GitHub Pages 的构建需要时间，不要在推送后立即访问，至少等待 60 秒。
- **所有部署需 CoS 授权**：防止误操作覆盖生产环境。

## 变更日志
- 2026-04-15 v4.0：深度重写，增加完整的命令示例、验证流程、回滚流程和避坑指南。
