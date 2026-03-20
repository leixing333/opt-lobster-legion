---
name: opt-design-system
description: OPT 设计公司品牌设计系统技能。管理品牌色彩、字体、组件规范，生成品牌视觉资产。
homepage: https://github.com/opt-company/opt-design-system
user-invocable: true
---

# OPT 设计系统技能

## 功能说明

此技能帮助 AI Agent 遵循 OPT 设计公司的品牌规范，生成符合品牌调性的视觉资产。

## 品牌规范

### 色彩系统

| 色彩名称 | HEX 值 | 使用场景 |
|---|---|---|
| Primary | `#1A1A2E` | 主色，深海蓝黑 |
| Accent | `#E94560` | 强调色，活力红 |
| Surface | `#16213E` | 背景色 |
| Text Primary | `#FFFFFF` | 主要文字 |
| Text Secondary | `#A8A8B3` | 次要文字 |
| Success | `#00B894` | 成功状态 |
| Warning | `#FDCB6E` | 警告状态 |

### 字体系统

- **标题字体**：Inter Bold（英文）/ 思源黑体 Bold（中文）
- **正文字体**：Inter Regular（英文）/ 思源宋体 Regular（中文）
- **代码字体**：JetBrains Mono

### 间距系统

基础单位：8px。所有间距均为 8 的倍数（8, 16, 24, 32, 48, 64）。

## 使用方法

当用户要求生成品牌相关的视觉资产时，严格遵循上述规范。

生成 SVG 或 CSS 时，使用以下变量：
```css
:root {
  --color-primary: #1A1A2E;
  --color-accent: #E94560;
  --color-surface: #16213E;
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #A8A8B3;
  --spacing-unit: 8px;
  --font-heading: 'Inter', 'Source Han Sans', sans-serif;
  --font-body: 'Inter', 'Source Han Serif', serif;
}
```

## 触发词

- "生成品牌资产"
- "按照品牌规范"
- "OPT 设计风格"
- "品牌色彩"
