# SKILL: opt-web-publisher — 网站发布技能

## 1. 技能简介

本技能实现了从代码到线上的完整发布流程，支持 GitHub Pages（静态站点）和 Vercel（全栈应用）两种发布方式。发布流程遵循 TAOR 引擎，支持自动重试和回滚。

## 2. 适用场景

- FE 完成前端开发后，发布到 GitHub Pages 进行预览。
- Ops 执行 CI/CD 流程，将应用部署到生产环境。
- 需要快速发布静态文档或展示页面。

## 3. GitHub Pages 发布流程

```bash
#!/bin/bash
# OPT v6.0 - GitHub Pages 发布脚本
# 遵循 TAOR 引擎，支持自动重试

set -euo pipefail

REPO_DIR="${1:-$(pwd)}"
BRANCH="${2:-gh-pages}"
MAX_RETRIES=3
RETRY_COUNT=0

publish_to_github_pages() {
    local dir="$1"
    local branch="$2"
    
    echo "📦 准备发布到 GitHub Pages..."
    
    # THINK: 检查环境
    if ! git -C "$dir" remote -v | grep -q "github.com"; then
        echo "❌ 未找到 GitHub 远程仓库"
        return 1
    fi
    
    # ACT: 构建（如果有 package.json）
    if [ -f "${dir}/package.json" ]; then
        echo "🔨 执行构建..."
        cd "$dir" && npm run build 2>&1
    fi
    
    # 确定发布目录
    BUILD_DIR="${dir}/dist"
    if [ ! -d "$BUILD_DIR" ]; then
        BUILD_DIR="$dir"
    fi
    
    # ACT: 创建并推送 gh-pages 分支
    cd "$BUILD_DIR"
    
    # 添加 .nojekyll 禁用 Jekyll
    touch .nojekyll
    
    # 初始化临时 git 仓库
    git init -b "$branch"
    git add -A
    git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # OBSERVE: 推送
    REMOTE_URL=$(git -C "$dir" remote get-url origin)
    git remote add origin "$REMOTE_URL"
    git push -f origin "$branch"
    
    echo "✅ 发布成功！"
    
    # 提取 GitHub Pages URL
    REPO_NAME=$(basename "$REMOTE_URL" .git)
    OWNER=$(echo "$REMOTE_URL" | sed 's/.*github.com[:/]\(.*\)\/.*/\1/')
    echo "🌐 访问地址: https://${OWNER}.github.io/${REPO_NAME}/"
}

# TAOR 重试循环
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if publish_to_github_pages "$REPO_DIR" "$BRANCH"; then
        exit 0
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⚠️ 第 $RETRY_COUNT 次发布失败，等待重试..."
        sleep $((RETRY_COUNT * 5))
    fi
done

echo "🚨 ESCALATION: 发布失败，已重试 $MAX_RETRIES 次，请 CoS 介入"
exit 1
```

## 4. 发布前检查清单

```bash
# 运行发布前检查
/publish:check

# 检查内容：
# ✅ 是否有 .nojekyll 文件（GitHub Pages）
# ✅ 是否有 index.html 入口文件
# ✅ 所有链接是否使用相对路径
# ✅ 图片是否已压缩（< 500KB）
# ✅ 是否有 robots.txt 和 sitemap.xml
```

## 5. 错误处理

| 错误 | 原因 | 解决方案 |
|---|---|---|
| `403 Forbidden` | Token 权限不足 | 确认 Token 有 `repo` 权限 |
| `404 Not Found` | 仓库不存在 | 先在 GitHub 创建仓库 |
| Pages 显示 README | Jekyll 干扰 | 添加 `.nojekyll` 文件 |
| 构建失败 | 依赖问题 | 运行 `npm ci` 而非 `npm install` |

## 6. 变更日志

- 2026-04-16: v1.0 初始版本，支持 GitHub Pages 发布
- 2026-04-16: v1.1 增加 TAOR 重试机制和 Escalation 触发
