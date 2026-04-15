#!/usr/bin/env python3
"""
OPT v7.0 - Vision Parser: Multimodal Design-to-Code Engine
多模态视觉解析引擎：将 Figma 设计图/截图直接转化为可执行的前端代码

核心能力：
  1. 设计图解析（Design Parsing）：
     - 接收 Figma 导出的 PNG/JPG 或 URL，调用视觉模型分析布局结构
     - 识别组件层级（Header/Nav/Card/Button/Form/Footer 等）
     - 提取颜色、字体、间距等设计 Token
  2. 代码生成（Code Generation）：
     - 基于解析结果生成 React + TailwindCSS 组件代码
     - 遵循 FE SOUL.md 中的组件开发标准（含测试文件和 README）
     - 自动检查与 DESIGN_SYSTEM.md 的一致性
  3. 迭代修正（Iterative Refinement）：
     - 支持"截图对比"模式：将实现结果与原始设计图进行视觉差异分析
     - 自动生成修正建议，触发 FE 的 TAOR 重试循环

依赖：
  - openai (with vision support) 或 anthropic claude-3-7-sonnet
  - 通过 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 环境变量配置

使用方式：
  from engine.vision_parser import VisionParser
  parser = VisionParser()
  result = parser.parse_design("path/to/design.png")
  code = parser.generate_component(result, component_name="HeroSection")
"""

import os
import base64
import json
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass, field

# ── 数据结构定义 ─────────────────────────────────────────────────────────────

@dataclass
class DesignToken:
    """从设计图中提取的设计 Token"""
    colors: list[str] = field(default_factory=list)          # 主色调列表（HEX）
    fonts: list[str] = field(default_factory=list)           # 字体族列表
    spacing: list[str] = field(default_factory=list)         # 间距值列表（px/rem）
    border_radius: list[str] = field(default_factory=list)   # 圆角值列表
    shadows: list[str] = field(default_factory=list)         # 阴影值列表


@dataclass
class ComponentSpec:
    """从设计图解析出的组件规格"""
    name: str                                                 # 组件名称
    type: str                                                 # 组件类型（layout/ui/form）
    layout: str                                               # 布局描述（flex/grid/absolute）
    children: list[str] = field(default_factory=list)        # 子组件列表
    props: dict = field(default_factory=dict)                 # 组件属性
    responsive: bool = True                                   # 是否需要响应式


@dataclass
class ParseResult:
    """视觉解析的完整结果"""
    image_path: str                                           # 原始图片路径
    description: str                                          # 整体设计描述
    components: list[ComponentSpec] = field(default_factory=list)
    tokens: DesignToken = field(default_factory=DesignToken)
    layout_structure: str = ""                                # 整体布局结构（Markdown 描述）
    accessibility_notes: list[str] = field(default_factory=list)
    raw_analysis: str = ""                                    # 视觉模型的原始分析文本


# ── 视觉解析引擎核心类 ────────────────────────────────────────────────────────

class VisionParser:
    """
    多模态视觉解析引擎。
    支持 OpenAI GPT-4o 和 Anthropic Claude 3.7 Sonnet 两种后端。
    """

    # 解析提示词：指导视觉模型进行结构化分析
    PARSE_PROMPT = """你是一位资深的前端工程师，正在分析一张 UI 设计图。
请对这张设计图进行深度分析，并以严格的 JSON 格式返回以下信息：

{
  "description": "整体设计的一句话描述",
  "layout_structure": "整体布局结构的 Markdown 描述（使用树形结构）",
  "components": [
    {
      "name": "组件名称（PascalCase，如 HeroSection）",
      "type": "layout | ui | form | navigation",
      "layout": "布局方式（flex-col / flex-row / grid / absolute）",
      "children": ["子组件名称列表"],
      "props": {
        "text": "文本内容（如有）",
        "variant": "样式变体（primary/secondary/ghost）",
        "size": "尺寸（sm/md/lg）"
      },
      "responsive": true
    }
  ],
  "tokens": {
    "colors": ["#主色", "#辅色", "#背景色", "#文字色"],
    "fonts": ["字体族名称"],
    "spacing": ["主要间距值，如 16px, 24px, 48px"],
    "border_radius": ["圆角值，如 8px, 16px"],
    "shadows": ["阴影值，如 0 4px 12px rgba(0,0,0,0.1)"]
  },
  "accessibility_notes": [
    "无障碍设计建议，如：确保按钮有足够的对比度",
    "确保所有图片有 alt 属性"
  ]
}

请确保 JSON 格式严格正确，不要包含注释或多余的文字。"""

    # 代码生成提示词：基于解析结果生成 React 组件
    CODE_GEN_PROMPT = """你是一位资深的前端工程师，请基于以下设计规格生成 React + TailwindCSS 组件代码。

设计规格：
{spec}

设计 Token：
{tokens}

代码要求：
1. 使用 React 18 + TypeScript + TailwindCSS
2. 组件必须是函数式组件，使用 Props 接口定义类型
3. 样式必须使用 TailwindCSS 类名，不允许内联样式
4. 必须实现响应式布局（移动端优先）
5. 必须包含 aria 属性（无障碍支持）
6. 代码必须可以直接运行，不需要额外配置

请生成以下文件的完整内容：
1. `index.tsx` — 组件主文件
2. `{name}.test.tsx` — Vitest 单元测试文件
3. `README.md` — 组件使用说明（含 Props 文档）

请以 JSON 格式返回：
{
  "index_tsx": "完整的 index.tsx 代码",
  "test_tsx": "完整的测试文件代码",
  "readme_md": "完整的 README.md 内容"
}"""

    # 视觉差异分析提示词：对比设计图与实现截图
    DIFF_PROMPT = """你是一位资深的 UI/UX 工程师，请对比以下两张图片：
- 图片1：原始设计图（目标效果）
- 图片2：当前实现截图（实际效果）

请识别所有视觉差异，并以 JSON 格式返回修正建议：
{
  "differences": [
    {
      "element": "差异元素名称",
      "expected": "设计图中的效果",
      "actual": "实现截图中的效果",
      "fix": "具体的 TailwindCSS 修正方案"
    }
  ],
  "overall_similarity": 0.85,
  "priority_fixes": ["最重要的3个修正项"]
}"""

    def __init__(self, backend: str = "openai"):
        """
        初始化视觉解析引擎。
        
        参数：
            backend: 使用的视觉模型后端（"openai" 或 "anthropic"）
        """
        self.backend = backend
        self._client = None
        self._init_client()

    def _init_client(self):
        """初始化 API 客户端"""
        if self.backend == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
                )
                self._model = "gpt-4o"
            except ImportError:
                raise RuntimeError("请安装 openai 包：pip install openai")
        elif self.backend == "anthropic":
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=os.environ.get("ANTHROPIC_API_KEY")
                )
                self._model = "claude-3-7-sonnet-20250219"
            except ImportError:
                raise RuntimeError("请安装 anthropic 包：pip install anthropic")
        else:
            raise ValueError(f"不支持的后端：{self.backend}，请使用 'openai' 或 'anthropic'")

    def _encode_image(self, image_path: Union[str, Path]) -> tuple[str, str]:
        """将图片文件编码为 base64，返回 (base64_data, media_type)"""
        path = Path(image_path)
        suffix = path.suffix.lower()
        media_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        media_type = media_type_map.get(suffix, "image/png")
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return data, media_type

    def _call_vision_api(self, prompt: str, images: list[Union[str, Path]]) -> str:
        """
        调用视觉模型 API。
        支持本地图片路径和 URL。
        """
        if self.backend == "openai":
            content = [{"type": "text", "text": prompt}]
            for img in images:
                img_str = str(img)
                if img_str.startswith("http://") or img_str.startswith("https://"):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img_str, "detail": "high"}
                    })
                else:
                    data, media_type = self._encode_image(img)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{data}",
                            "detail": "high"
                        }
                    })
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": content}],
                max_tokens=4096,
                temperature=0.1
            )
            return response.choices[0].message.content

        elif self.backend == "anthropic":
            content = []
            for img in images:
                img_str = str(img)
                if img_str.startswith("http://") or img_str.startswith("https://"):
                    content.append({
                        "type": "image",
                        "source": {"type": "url", "url": img_str}
                    })
                else:
                    data, media_type = self._encode_image(img)
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data
                        }
                    })
            content.append({"type": "text", "text": prompt})
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": content}]
            )
            return response.content[0].text

    def _extract_json(self, text: str) -> dict:
        """从模型输出中提取 JSON（处理 markdown 代码块包裹的情况）"""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # 去掉首尾的 ``` 行
            start = 1
            end = len(lines) - 1
            for i, line in enumerate(lines):
                if line.startswith("```") and i > 0:
                    end = i
                    break
            text = "\n".join(lines[start:end])
        return json.loads(text)

    def parse_design(
        self,
        image: Union[str, Path],
        context: Optional[str] = None
    ) -> ParseResult:
        """
        解析设计图，提取组件结构和设计 Token。
        
        参数：
            image: 设计图路径（本地文件或 URL）
            context: 额外的上下文信息（如"这是一个 SaaS 产品的落地页"）
        
        返回：
            ParseResult 对象，包含完整的解析结果
        """
        prompt = self.PARSE_PROMPT
        if context:
            prompt = f"背景信息：{context}\n\n" + prompt

        print(f"[VisionParser] 正在解析设计图: {image}")
        raw_text = self._call_vision_api(prompt, [image])

        try:
            data = self._extract_json(raw_text)
        except json.JSONDecodeError:
            # 如果 JSON 解析失败，返回原始文本作为描述
            return ParseResult(
                image_path=str(image),
                description="JSON 解析失败，请查看 raw_analysis",
                raw_analysis=raw_text
            )

        # 构建 DesignToken
        tokens_data = data.get("tokens", {})
        tokens = DesignToken(
            colors=tokens_data.get("colors", []),
            fonts=tokens_data.get("fonts", []),
            spacing=tokens_data.get("spacing", []),
            border_radius=tokens_data.get("border_radius", []),
            shadows=tokens_data.get("shadows", [])
        )

        # 构建 ComponentSpec 列表
        components = []
        for comp_data in data.get("components", []):
            components.append(ComponentSpec(
                name=comp_data.get("name", "UnknownComponent"),
                type=comp_data.get("type", "ui"),
                layout=comp_data.get("layout", "flex-col"),
                children=comp_data.get("children", []),
                props=comp_data.get("props", {}),
                responsive=comp_data.get("responsive", True)
            ))

        return ParseResult(
            image_path=str(image),
            description=data.get("description", ""),
            components=components,
            tokens=tokens,
            layout_structure=data.get("layout_structure", ""),
            accessibility_notes=data.get("accessibility_notes", []),
            raw_analysis=raw_text
        )

    def generate_component(
        self,
        parse_result: ParseResult,
        component_name: str,
        output_dir: Optional[Union[str, Path]] = None
    ) -> dict[str, str]:
        """
        基于解析结果生成 React 组件代码。
        
        参数：
            parse_result: parse_design() 的返回结果
            component_name: 要生成的组件名称（PascalCase）
            output_dir: 代码输出目录（可选，若指定则自动写入文件）
        
        返回：
            包含 index_tsx、test_tsx、readme_md 的字典
        """
        # 找到对应的组件规格
        target_spec = None
        for comp in parse_result.components:
            if comp.name == component_name:
                target_spec = comp
                break

        if not target_spec:
            # 如果没找到精确匹配，使用整体描述
            spec_text = f"组件名称: {component_name}\n整体描述: {parse_result.description}\n布局: {parse_result.layout_structure}"
        else:
            spec_text = json.dumps({
                "name": target_spec.name,
                "type": target_spec.type,
                "layout": target_spec.layout,
                "children": target_spec.children,
                "props": target_spec.props,
                "responsive": target_spec.responsive
            }, ensure_ascii=False, indent=2)

        tokens_text = json.dumps({
            "colors": parse_result.tokens.colors,
            "fonts": parse_result.tokens.fonts,
            "spacing": parse_result.tokens.spacing,
            "border_radius": parse_result.tokens.border_radius,
            "shadows": parse_result.tokens.shadows
        }, ensure_ascii=False, indent=2)

        prompt = self.CODE_GEN_PROMPT.format(
            spec=spec_text,
            tokens=tokens_text,
            name=component_name
        )

        print(f"[VisionParser] 正在生成组件代码: {component_name}")
        raw_text = self._call_vision_api(prompt, [parse_result.image_path])

        try:
            code_files = self._extract_json(raw_text)
        except json.JSONDecodeError:
            code_files = {
                "index_tsx": f"// 代码生成失败，原始输出：\n// {raw_text[:200]}",
                "test_tsx": "",
                "readme_md": f"# {component_name}\n\n代码生成失败，请手动实现。"
            }

        # 如果指定了输出目录，写入文件
        if output_dir:
            out_path = Path(output_dir) / component_name
            out_path.mkdir(parents=True, exist_ok=True)
            if code_files.get("index_tsx"):
                (out_path / "index.tsx").write_text(code_files["index_tsx"], encoding="utf-8")
            if code_files.get("test_tsx"):
                (out_path / f"{component_name}.test.tsx").write_text(
                    code_files["test_tsx"], encoding="utf-8"
                )
            if code_files.get("readme_md"):
                (out_path / "README.md").write_text(code_files["readme_md"], encoding="utf-8")
            print(f"[VisionParser] 代码已写入: {out_path}")

        return code_files

    def compare_with_design(
        self,
        design_image: Union[str, Path],
        screenshot_image: Union[str, Path]
    ) -> dict:
        """
        对比设计图与实现截图，生成视觉差异分析报告。
        
        参数：
            design_image: 原始设计图路径
            screenshot_image: 当前实现的截图路径
        
        返回：
            包含 differences、overall_similarity、priority_fixes 的字典
        """
        print(f"[VisionParser] 正在对比设计图与实现截图...")
        raw_text = self._call_vision_api(
            self.DIFF_PROMPT,
            [design_image, screenshot_image]
        )

        try:
            return self._extract_json(raw_text)
        except json.JSONDecodeError:
            return {
                "differences": [],
                "overall_similarity": 0.0,
                "priority_fixes": [],
                "raw_analysis": raw_text
            }

    def design_to_code_pipeline(
        self,
        design_image: Union[str, Path],
        output_dir: Union[str, Path],
        context: Optional[str] = None
    ) -> dict:
        """
        完整的设计图转代码流水线（一键执行）。
        
        步骤：
          1. 解析设计图，提取组件结构和设计 Token
          2. 为每个顶层组件生成 React 代码
          3. 生成整体的 DESIGN_SYSTEM.md Token 文档
        
        返回：
            包含所有生成结果的字典
        """
        print(f"[VisionParser] 启动设计图转代码流水线: {design_image}")

        # 步骤 1：解析设计图
        parse_result = self.parse_design(design_image, context)
        print(f"[VisionParser] 识别到 {len(parse_result.components)} 个组件")

        # 步骤 2：为每个组件生成代码
        generated_components = {}
        for comp in parse_result.components:
            code_files = self.generate_component(
                parse_result,
                comp.name,
                output_dir=Path(output_dir) / "components"
            )
            generated_components[comp.name] = code_files

        # 步骤 3：生成 DESIGN_SYSTEM.md
        design_system_content = self._generate_design_system_doc(parse_result)
        design_system_path = Path(output_dir) / "DESIGN_SYSTEM.md"
        design_system_path.parent.mkdir(parents=True, exist_ok=True)
        design_system_path.write_text(design_system_content, encoding="utf-8")
        print(f"[VisionParser] 设计系统文档已生成: {design_system_path}")

        return {
            "parse_result": parse_result,
            "generated_components": list(generated_components.keys()),
            "design_system_path": str(design_system_path),
            "output_dir": str(output_dir)
        }

    def _generate_design_system_doc(self, parse_result: ParseResult) -> str:
        """基于解析结果生成 DESIGN_SYSTEM.md 文档"""
        tokens = parse_result.tokens
        lines = [
            "# DESIGN_SYSTEM.md",
            "",
            f"> 由 VisionParser 自动生成，来源：`{Path(parse_result.image_path).name}`",
            "",
            "## 颜色系统",
            "",
            "| Token 名称 | 颜色值 | 用途 |",
            "|---|---|---|",
        ]
        color_names = ["primary", "secondary", "background", "text", "accent", "border"]
        for i, color in enumerate(tokens.colors):
            name = color_names[i] if i < len(color_names) else f"color-{i+1}"
            lines.append(f"| `--color-{name}` | `{color}` | 待补充 |")

        lines += [
            "",
            "## 字体系统",
            "",
            "| 用途 | 字体族 |",
            "|---|---|",
        ]
        for font in tokens.fonts:
            lines.append(f"| 正文 | `{font}` |")

        lines += [
            "",
            "## 间距系统",
            "",
            f"主要间距值：`{'`, `'.join(tokens.spacing)}`",
            "",
            "## 圆角系统",
            "",
            f"圆角值：`{'`, `'.join(tokens.border_radius)}`",
            "",
            "## 阴影系统",
            "",
        ]
        for shadow in tokens.shadows:
            lines.append(f"- `{shadow}`")

        lines += [
            "",
            "## 无障碍设计规范",
            "",
        ]
        for note in parse_result.accessibility_notes:
            lines.append(f"- {note}")

        lines += [
            "",
            "---",
            "",
            f"*自动生成时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        ]

        return "\n".join(lines)


    def parse_from_stitch(self, prompt: str, device_type: str = "web",
                          project_id: Optional[str] = None) -> "ParseResult":
        """
        v7.1 新增：直接从 Stitch 生成 UI 并解析（Stitch → VisionParser 联合流水线）。

        流程：
          1. 调用 StitchClient.generate_ui(prompt) 生成 UI 截图
          2. 将截图传入 parse_design() 进行结构化解析
          3. 返回 ParseResult（含组件结构、设计 Token）

        参数：
            prompt:      UI 描述
            device_type: 设备类型（"web" 或 "app"）
            project_id:  Stitch 项目 ID

        返回：
            ParseResult 对象
        """
        try:
            from engine.stitch_client import StitchClient
        except ImportError:
            raise ImportError("StitchClient 不可用，请确认 engine/stitch_client.py 存在")

        stitch = StitchClient(project_id=project_id)
        screen = stitch.generate_ui(prompt, device_type)

        # 保存截图到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            screen.save_screenshot(tmp_path)
            context = f"This UI was generated by Google Stitch for: {prompt}"
            result = self.parse_design(tmp_path, context=context)
            result.image_path = f"stitch://{screen.screen_id}"  # 标记来源
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def generate_assets_with_nano_banana(
        self,
        parse_result: "ParseResult",
        output_dir: Union[str, Path],
        asset_types: Optional[list] = None
    ) -> dict:
        """
        v7.1 新增：基于解析结果，使用 Nano Banana 生成配套图像资产。

        根据 ParseResult 中识别到的组件类型，自动生成对应的图像资产：
        - Hero Section → 生成 hero 背景图
        - Avatar/Profile → 生成 avatar 图像
        - Banner → 生成 banner 图像
        - Illustration → 生成插图

        参数：
            parse_result: VisionParser 的解析结果
            output_dir:   图像资产保存目录
            asset_types:  指定要生成的资产类型（默认自动推断）

        返回：
            {component_name: asset_path} 的字典
        """
        try:
            from engine.nano_banana_client import NanaBananaClient
        except ImportError:
            raise ImportError("NanaBananaClient 不可用，请确认 engine/nano_banana_client.py 存在")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        nb_client = NanaBananaClient()
        generated_assets = {}

        # 组件类型 → 资产类型的映射
        component_to_asset = {
            "hero": "hero",
            "herosection": "hero",
            "banner": "banner",
            "avatar": "avatar",
            "profile": "avatar",
            "illustration": "illustration",
            "background": "background",
            "icon": "icon",
        }

        # 提取颜色方案
        color_scheme = None
        if parse_result.tokens.colors:
            primary = parse_result.tokens.colors[0] if parse_result.tokens.colors else None
            bg = parse_result.tokens.colors[-1] if len(parse_result.tokens.colors) > 1 else None
            if primary:
                color_scheme = f"{primary} primary"
                if bg:
                    color_scheme += f", {bg} background"

        for component in parse_result.components:
            comp_name_lower = component.name.lower()

            # 确定资产类型
            asset_type = None
            if asset_types:
                # 用户指定了资产类型
                for at in asset_types:
                    if at.lower() in comp_name_lower:
                        asset_type = at
                        break
            else:
                # 自动推断
                for keyword, at in component_to_asset.items():
                    if keyword in comp_name_lower:
                        asset_type = at
                        break

            if not asset_type:
                continue

            # 生成图像资产
            description = f"{component.name} for {parse_result.description}"
            asset_path = output_dir / f"{component.name.lower()}_{asset_type}.png"

            try:
                result = nb_client.generate_ui_assets(
                    asset_type=asset_type,
                    description=description,
                    color_scheme=color_scheme,
                    save_dir=output_dir
                )
                # 重命名到规范路径
                if result:
                    import shutil
                    saved_files = sorted(output_dir.glob(f"{asset_type}_*.png"))
                    if saved_files:
                        shutil.move(str(saved_files[-1]), str(asset_path))
                        generated_assets[component.name] = asset_path
            except Exception as e:
                print(f"[NanaBanana] 生成 {component.name} 资产失败: {e}")

        return generated_assets

    def full_pipeline_v71(
        self,
        source: str,
        output_dir: Union[str, Path],
        context: Optional[str] = None,
        use_stitch: bool = False,
        generate_assets: bool = True
    ) -> dict:
        """
        v7.1 完整流水线：Stitch + VisionParser + Nano Banana 三方联合。

        流程：
          [选项A] 已有设计图:
            设计图 → VisionParser 解析 → 生成 React 代码 → Nano Banana 生成图像资产

          [选项B] 从 Prompt 开始（use_stitch=True）:
            Prompt → Stitch 生成 UI → VisionParser 解析 → 生成 React 代码 → Nano Banana 生成图像资产

        参数：
            source:          设计图路径（选项A）或 UI 描述文本（选项B，需 use_stitch=True）
            output_dir:      输出目录
            context:         额外上下文信息
            use_stitch:      是否使用 Stitch 生成 UI（True=从 Prompt 开始）
            generate_assets: 是否使用 Nano Banana 生成图像资产

        返回：
            包含所有产物路径的字典
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        result = {"pipeline_version": "v7.1", "source": source}

        # Step 1: 获取设计图
        if use_stitch:
            print(f"[Step 1/4] Stitch 生成 UI: {source[:50]}...")
            parse_result = self.parse_from_stitch(source)
            result["stitch_screen_id"] = parse_result.image_path
        else:
            print(f"[Step 1/4] 解析设计图: {source}")
            parse_result = self.parse_design(source, context)

        result["parse_result"] = parse_result
        print(f"  识别到 {len(parse_result.components)} 个组件")

        # Step 2: 生成 React 代码
        print(f"[Step 2/4] 生成 React 组件代码...")
        components_dir = output_dir / "components"
        code_result = self.design_to_code_pipeline(source, str(components_dir), context)
        result["generated_components"] = code_result.get("generated_components", [])
        result["design_system_path"] = code_result.get("design_system_path")
        print(f"  生成 {len(result['generated_components'])} 个组件")

        # Step 3: Nano Banana 生成图像资产（可选）
        if generate_assets:
            print(f"[Step 3/4] Nano Banana 生成图像资产...")
            assets_dir = output_dir / "assets"
            try:
                assets = self.generate_assets_with_nano_banana(parse_result, assets_dir)
                result["generated_assets"] = {k: str(v) for k, v in assets.items()}
                print(f"  生成 {len(assets)} 个图像资产")
            except Exception as e:
                print(f"  图像资产生成失败（不影响主流程）: {e}")
                result["generated_assets"] = {}
        else:
            result["generated_assets"] = {}

        # Step 4: 生成流水线报告
        print(f"[Step 4/4] 生成流水线报告...")
        report_path = output_dir / "pipeline_report.md"
        report_content = self._generate_pipeline_report(result, source)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        result["report_path"] = str(report_path)

        print(f"\n✅ v7.1 流水线完成！所有产物保存在: {output_dir}")
        return result

    def _generate_pipeline_report(self, result: dict, source: str) -> str:
        """生成流水线执行报告（Markdown 格式）"""
        from datetime import datetime
        lines = [
            "# OPT v7.1 流水线执行报告",
            "",
            f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> 来源：{source}",
            f"> 流水线版本：{result.get('pipeline_version', 'v7.1')}",
            "",
            "## 执行摘要",
            "",
        ]

        parse_result = result.get("parse_result")
        if parse_result:
            lines += [
                f"**设计描述**：{parse_result.description}",
                "",
                f"**识别组件数**：{len(parse_result.components)}",
                "",
                "**设计 Token**：",
                f"- 主色调：{', '.join(parse_result.tokens.colors[:3]) or '未识别'}",
                f"- 字体：{', '.join(parse_result.tokens.fonts) or '未识别'}",
                "",
            ]

        components = result.get("generated_components", [])
        if components:
            lines += [
                "## 生成的 React 组件",
                "",
                "| 组件名称 | 状态 |",
                "|---|---|",
            ]
            for comp in components:
                lines.append(f"| `{comp}` | ✅ 已生成 |")
            lines.append("")

        assets = result.get("generated_assets", {})
        if assets:
            lines += [
                "## 生成的图像资产（Nano Banana）",
                "",
                "| 组件 | 资产路径 |",
                "|---|---|",
            ]
            for comp, path in assets.items():
                lines.append(f"| `{comp}` | `{path}` |")
            lines.append("")

        if result.get("design_system_path"):
            lines += [
                "## 设计系统",
                "",
                f"已生成 `DESIGN_SYSTEM.md`：`{result['design_system_path']}`",
                "",
            ]

        return "\n".join(lines)


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 engine/vision_parser.py parse <image_path> [context]")
        print("  python3 engine/vision_parser.py generate <image_path> <component_name> <output_dir>")
        print("  python3 engine/vision_parser.py pipeline <image_path> <output_dir> [context]")
        print("  python3 engine/vision_parser.py diff <design_image> <screenshot_image>")
        sys.exit(0)

    # 自动选择后端（优先 OpenAI，其次 Anthropic）
    backend = "openai" if os.environ.get("OPENAI_API_KEY") else "anthropic"
    parser = VisionParser(backend=backend)

    cmd = sys.argv[1]

    if cmd == "parse" and len(sys.argv) >= 3:
        context = sys.argv[3] if len(sys.argv) > 3 else None
        result = parser.parse_design(sys.argv[2], context)
        print(f"\n描述: {result.description}")
        print(f"识别组件数: {len(result.components)}")
        print(f"布局结构:\n{result.layout_structure}")
        print(f"\n设计 Token:")
        print(f"  颜色: {result.tokens.colors}")
        print(f"  字体: {result.tokens.fonts}")

    elif cmd == "generate" and len(sys.argv) >= 5:
        result = parser.parse_design(sys.argv[2])
        code = parser.generate_component(result, sys.argv[3], output_dir=sys.argv[4])
        print(f"\n已生成组件: {sys.argv[3]}")
        print(f"输出目录: {sys.argv[4]}")

    elif cmd == "pipeline" and len(sys.argv) >= 4:
        context = sys.argv[4] if len(sys.argv) > 4 else None
        result = parser.design_to_code_pipeline(sys.argv[2], sys.argv[3], context)
        print(f"\n流水线完成!")
        print(f"生成组件: {result['generated_components']}")
        print(f"设计系统: {result['design_system_path']}")

    elif cmd == "diff" and len(sys.argv) >= 4:
        diff = parser.compare_with_design(sys.argv[2], sys.argv[3])
        print(f"\n相似度: {diff.get('overall_similarity', 0):.0%}")
        print(f"差异数量: {len(diff.get('differences', []))}")
        print(f"优先修复:")
        for fix in diff.get("priority_fixes", []):
            print(f"  - {fix}")

    else:
        print(f"未知命令或参数不足: {cmd}")
        sys.exit(1)
