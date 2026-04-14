# 技能：OPT AutoDream 记忆巩固系统

## 简介
本技能基于 Claude Code 的四层记忆架构（CARROS）和 Hermes Agent 的持久化记忆机制，为 KO（知识管理员）提供**后台记忆整理与知识萃取**能力。它模拟人类睡眠时的记忆巩固过程，在空闲时自动整理、萃取和索引记忆碎片，实现知识的长期沉淀。

## 适用角色
**KO**（主要）

## 触发条件
- 每天凌晨定时任务触发（推荐 02:00 AM）。
- 当 CoS 执行 Closeout（工作日结束总结）后手动触发。
- 当 `workspace/` 目录下的日志文件超过 10 个时自动触发。

## 执行步骤

### 步骤 1：碎片收集（Gather）
读取各 Agent 的 L1 记忆文件（Closeout 摘要）：
```bash
# 读取所有 Agent 的今日工作摘要
find ./workspace -name "closeout-$(date +%Y-%m-%d).md" -type f
```
收集内容包括：项目进展、遇到的问题、解决方案、代码片段、用户反馈。

### 步骤 2：关联分析（Analyze）
对收集到的碎片进行关联分析，识别以下模式：
- **重复出现的问题**：同一类错误出现 2 次以上，说明需要固化为技能或知识点。
- **成功的解决方案**：某个方案被成功使用 3 次以上，说明可以提炼为 `SKILL.md`。
- **用户偏好信号**：老板对某类输出表示满意或不满意的反馈。

### 步骤 3：知识萃取（Extract）
将碎片化的信息提炼成结构化的知识点，写入对应目录：

| 知识类型 | 存储位置 | 示例 |
|---|---|---|
| 设计原则 | `knowledge-base/principles/` | 品牌色彩规范、排版标准 |
| 代码模式 | `knowledge-base/patterns/` | 常用的 API 调用模板 |
| 错误案例 | `knowledge-base/errors/` | 某个 npm 包的安装坑 |
| 项目历史 | `knowledge-base/projects/` | 项目里程碑和关键决策 |

### 步骤 4：技能提炼（Skill Distillation）
如果某个任务流程被成功执行 3 次以上，调用 `opt-skill-evolution` 技能，将其提炼为 `SKILL.md` 文件。

### 步骤 5：记忆索引更新（Index Update）
更新 `knowledge-base/INDEX.md` 文件，记录本次新增和修改的知识点，方便后续 RAG 检索。

## 记忆管理原则
- **观点而非事实**：记忆是观点而非事实，不保存可通过工具实时推导的信息（如代码模式、Git 历史）。
- **严格分离**：将记忆与计划/任务严格分离，避免混淆。
- **去重优化**：自动合并重复的知识点，保持知识库的精简和高效。

## 变更日志
- 2026-04-15 v4.0：基于 Claude Code CARROS 架构和 Hermes Agent 持久化记忆机制深度重写，增加知识类型分类表和技能提炼触发条件。

---

## 完整执行脚本

```bash
#!/bin/bash
# Auto Dream 执行脚本（每天凌晨 2 点由 Ops 定时触发）
# 路径：skills/opt-autodream-memory/run.sh

DATE=$(date +%Y-%m-%d)
KB_DIR="./knowledge-base"
WORKSPACE_DIR="./workspace"
LOG_FILE="$WORKSPACE_DIR/ko/logs/autodream-$DATE.log"

echo "🌙 Auto Dream 开始 - $DATE" | tee -a "$LOG_FILE"

# === 步骤 1：碎片收集 ===
echo "📂 收集各 Agent 的 Closeout 摘要..." | tee -a "$LOG_FILE"

CLOSEOUT_FILES=$(find "$WORKSPACE_DIR" -name "closeout-$DATE.md" -type f 2>/dev/null)

if [ -z "$CLOSEOUT_FILES" ]; then
  echo "⚠️ 今日没有 Closeout 文件，跳过" | tee -a "$LOG_FILE"
  exit 0
fi

# 合并所有 Closeout 内容
COMBINED_CONTENT=""
for file in $CLOSEOUT_FILES; do
  AGENT=$(echo "$file" | awk -F'/' '{print $3}')
  echo "  - 读取 $AGENT 的 Closeout" | tee -a "$LOG_FILE"
  COMBINED_CONTENT="$COMBINED_CONTENT\n\n## $AGENT 的工作摘要\n$(cat $file)"
done

# === 步骤 2：关联分析 ===
echo "🔍 分析重复模式..." | tee -a "$LOG_FILE"

# 检查是否有重复出现的错误
REPEATED_ERRORS=$(grep -h "❌\|ERROR\|失败" $WORKSPACE_DIR/*/logs/*.log 2>/dev/null | \
  sort | uniq -c | sort -rn | head -10)

if [ -n "$REPEATED_ERRORS" ]; then
  echo "⚠️ 发现重复错误，记录到知识库..." | tee -a "$LOG_FILE"
  echo "# 重复错误记录 - $DATE" > "$KB_DIR/errors/repeated-$DATE.md"
  echo "$REPEATED_ERRORS" >> "$KB_DIR/errors/repeated-$DATE.md"
fi

# === 步骤 3：知识萃取 ===
echo "💡 萃取知识点..." | tee -a "$LOG_FILE"

# 检查是否有新的成功模式（被使用 3 次以上的命令）
SUCCESS_PATTERNS=$(grep -h "✅" $WORKSPACE_DIR/*/logs/*.log 2>/dev/null | \
  sort | uniq -c | sort -rn | awk '$1 >= 3 {print}' | head -5)

if [ -n "$SUCCESS_PATTERNS" ]; then
  echo "🌟 发现可提炼的成功模式，通知 opt-skill-evolution..." | tee -a "$LOG_FILE"
  echo "$SUCCESS_PATTERNS" > "/tmp/skill-evolution-candidates.txt"
fi

# === 步骤 4：用户画像辩证更新 ===
echo "👤 检查用户画像更新信号..." | tee -a "$LOG_FILE"

# 从 CoS 的 Closeout 中提取用户反馈信号
COS_CLOSEOUT="$WORKSPACE_DIR/cos/closeout-$DATE.md"
if [ -f "$COS_CLOSEOUT" ]; then
  FEEDBACK_SIGNALS=$(grep -i "老板.*喜欢\|老板.*不喜欢\|老板.*偏好\|用户.*反馈" "$COS_CLOSEOUT" 2>/dev/null)
  if [ -n "$FEEDBACK_SIGNALS" ]; then
    echo "🔄 发现画像更新信号，调用 opt-dialectical-modeling..." | tee -a "$LOG_FILE"
    echo "$FEEDBACK_SIGNALS" > "/tmp/profile-update-signals.txt"
  fi
fi

# === 步骤 5：更新知识库索引 ===
echo "📋 更新知识库索引..." | tee -a "$LOG_FILE"

cat > "$KB_DIR/INDEX.md" << EOF
# 知识库索引 - 最后更新：$DATE

## 设计原则
$(ls "$KB_DIR/principles/" 2>/dev/null | sed 's/^/- /')

## 代码模式
$(ls "$KB_DIR/patterns/" 2>/dev/null | sed 's/^/- /')

## 错误案例
$(ls "$KB_DIR/errors/" 2>/dev/null | sed 's/^/- /')

## 项目历史
$(ls "$KB_DIR/projects/" 2>/dev/null | sed 's/^/- /')

## 用户画像
$(ls "$KB_DIR/profiles/" 2>/dev/null | sed 's/^/- /')
EOF

echo "✅ Auto Dream 完成 - $(date)" | tee -a "$LOG_FILE"
```

---

## 辩证式画像融合示例

当 Auto Dream 发现用户偏好变化时，KO 使用以下辩证逻辑更新画像：

**场景**：老板之前主要用 Python，但最近开始问 Rust 相关问题。

```markdown
# 辩证融合过程

## 正题（Thesis）—— 现有画像
老板是一位有 5 年经验的 Python 开发者，
偏好快速原型开发，重视代码可读性。

## 反题（Antithesis）—— 新观察
最近 3 天，老板询问了 Rust 的内存安全机制、
所有权系统和 WebAssembly 编译，
并对 Python 的 GIL 限制表达了不满。

## 合题（Synthesis）—— 更新后的画像
老板是一位有 Python 背景的系统程序员，
正处于从快速原型开发向高性能系统编程的转型期。
他关注内存安全和性能，正在评估 Rust 作为未来主力语言。
在提供技术建议时，应优先考虑 Rust 方案，
但在快速原型场景下仍可推荐 Python。
```

---

## 与其他技能的协作

| 技能 | 协作方式 |
|---|---|
| `opt-skill-evolution` | 当发现成功模式被重复使用 3 次以上，触发技能沉淀 |
| `opt-dialectical-modeling` | 当发现用户偏好变化信号，触发画像辩证更新 |
| `opt-rag-knowledge` | Auto Dream 完成后，更新 RAG 知识库的索引，确保检索准确 |
| `opt-security-audit` | Auto Dream 日志会被 Ops 扫描，确保没有敏感信息泄露 |
