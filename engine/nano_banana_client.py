#!/usr/bin/env python3
"""
OPT v7.1 - Nano Banana Client: Google Gemini Image Generation Integration
Nano Banana 图像生成客户端（基于 Gemini API）

核心设计思路：
  Nano Banana 是 Google Gemini 系列的图像生成能力品牌名称，对应三个模型：
  - Nano Banana 2     → gemini-3.1-flash-image-preview（高速、高并发）
  - Nano Banana Pro   → gemini-3-pro-image-preview（专业、4K、复杂指令）
  - Nano Banana       → gemini-2.5-flash-image（速度优先、低延迟）

  本客户端封装了以下核心能力：
  1. text_to_image()       文本生成图像（支持多种宽高比和分辨率）
  2. image_to_image()      图像编辑（基于参考图 + 文本指令）
  3. multi_turn_edit()     多轮对话式图像编辑（保持上下文）
  4. generate_ui_assets()  专为 UI 设计生成图像资产（图标、插图、背景）
  5. generate_from_stitch() 将 Stitch 设计截图转化为高质量图像资产

  与 OPT 系统的集成点：
  - FE Agent 调用 generate_ui_assets() 生成 UI 图像资产
  - VisionParser 调用 generate_from_stitch() 增强 Stitch 设计图质量
  - CoS 调用 text_to_image() 快速生成概念图用于需求确认

使用方式：
  # 设置环境变量（必须）
  export GOOGLE_API_KEY=your_gemini_api_key

  from engine.nano_banana_client import NanaBananaClient
  client = NanaBananaClient()
  result = client.text_to_image("A modern SaaS dashboard with dark theme")
  result.save("dashboard_concept.png")
"""

import os
import io
import base64
import json
from pathlib import Path
from typing import Optional, Union, Literal
from datetime import datetime

# 模型常量
MODEL_NANO_BANANA_2   = "gemini-3.1-flash-image-preview"   # 高速，高并发
MODEL_NANO_BANANA_PRO = "gemini-3-pro-image-preview"        # 专业，4K，复杂指令
MODEL_NANO_BANANA     = "gemini-2.5-flash-image"            # 速度优先，低延迟

# 宽高比选项
AspectRatio = Literal["1:1", "4:3", "3:4", "16:9", "9:16", "21:9"]

# 分辨率选项（仅 Nano Banana Pro 支持 4K）
Resolution = Literal["512", "1K", "2K", "4K"]


class NanaBananaResult:
    """Nano Banana 生成结果封装类"""

    def __init__(self, image_data: bytes, mime_type: str = "image/png",
                 text: Optional[str] = None, model: str = ""):
        self.image_data = image_data
        self.mime_type = mime_type
        self.text = text          # 模型同时生成的文字说明（如果有）
        self.model = model
        self.generated_at = datetime.now().isoformat()

    def save(self, path: Union[str, Path]) -> Path:
        """保存图像到文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(self.image_data)
        return path

    def to_base64(self) -> str:
        """返回 base64 编码的图像数据"""
        return base64.b64encode(self.image_data).decode("utf-8")

    def to_pil(self):
        """返回 PIL Image 对象（需要 Pillow）"""
        try:
            from PIL import Image
            return Image.open(io.BytesIO(self.image_data))
        except ImportError:
            raise ImportError("需要安装 Pillow: pip install Pillow")

    def __repr__(self):
        size_kb = len(self.image_data) / 1024
        return f"<NanaBananaResult model={self.model} size={size_kb:.1f}KB text={bool(self.text)}>"


class NanaBananaClient:
    """
    Nano Banana 图像生成客户端。
    封装 Google Gemini API 的图像生成能力，专为 OPT 系统设计。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = MODEL_NANO_BANANA_2,
        workspace: Optional[Path] = None
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.default_model = default_model
        self.workspace = workspace or Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))
        self._client = None
        self._chat_session = None

    def _get_client(self):
        """延迟初始化 Gemini 客户端"""
        if self._client is None:
            try:
                from google import genai
                if self.api_key:
                    self._client = genai.Client(api_key=self.api_key)
                else:
                    # 尝试使用环境变量（google.genai 会自动读取 GOOGLE_API_KEY）
                    self._client = genai.Client()
            except ImportError:
                raise ImportError(
                    "需要安装 google-genai SDK:\n"
                    "  pip install google-genai\n"
                    "  或: pip install google-generativeai"
                )
        return self._client

    def text_to_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: AspectRatio = "16:9",
        resolution: Optional[Resolution] = None,
        negative_prompt: Optional[str] = None,
        save_to: Optional[Union[str, Path]] = None
    ) -> NanaBananaResult:
        """
        文本生成图像（Text-to-Image）。

        参数：
            prompt:          图像描述文本
            model:           使用的模型（默认 gemini-3.1-flash-image-preview）
            aspect_ratio:    宽高比（"1:1", "4:3", "16:9" 等）
            resolution:      分辨率（仅 Nano Banana Pro 支持 "4K"）
            negative_prompt: 负向提示词（描述不希望出现的内容）
            save_to:         如果指定，自动保存到该路径

        返回：
            NanaBananaResult 对象
        """
        from google.genai import types

        model = model or self.default_model
        client = self._get_client()

        # 构建完整提示词（加入负向提示词）
        full_prompt = prompt
        if negative_prompt:
            full_prompt += f"\n\nAvoid: {negative_prompt}"

        # 构建图像配置
        image_config_kwargs = {"aspect_ratio": aspect_ratio}
        if resolution and model == MODEL_NANO_BANANA_PRO:
            image_config_kwargs["image_size"] = resolution

        response = client.models.generate_content(
            model=model,
            contents=[full_prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(**image_config_kwargs)
            )
        )

        return self._parse_response(response, model, save_to)

    def image_to_image(
        self,
        prompt: str,
        reference_image: Union[str, Path, bytes],
        model: Optional[str] = None,
        aspect_ratio: AspectRatio = "1:1",
        save_to: Optional[Union[str, Path]] = None
    ) -> NanaBananaResult:
        """
        图像编辑（Image-to-Image）。
        基于参考图像和文本指令生成新图像。

        参数：
            prompt:          编辑指令（如 "将背景改为深色主题"）
            reference_image: 参考图像（文件路径、URL 或 bytes）
            model:           使用的模型
            aspect_ratio:    输出宽高比
            save_to:         如果指定，自动保存到该路径

        返回：
            NanaBananaResult 对象
        """
        from google.genai import types
        from PIL import Image as PILImage

        model = model or self.default_model
        client = self._get_client()

        # 加载参考图像
        if isinstance(reference_image, (str, Path)):
            ref_path = Path(reference_image)
            if ref_path.exists():
                image = PILImage.open(ref_path)
            else:
                raise FileNotFoundError(f"参考图像不存在: {reference_image}")
        elif isinstance(reference_image, bytes):
            image = PILImage.open(io.BytesIO(reference_image))
        else:
            raise ValueError("reference_image 必须是文件路径、URL 或 bytes")

        response = client.models.generate_content(
            model=model,
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio)
            )
        )

        return self._parse_response(response, model, save_to)

    def multi_turn_edit(
        self,
        initial_prompt: str,
        model: Optional[str] = None,
        aspect_ratio: AspectRatio = "16:9"
    ):
        """
        创建多轮对话式图像编辑会话。
        返回一个 MultiTurnSession 对象，可以持续编辑同一张图像。

        使用示例：
            session = client.multi_turn_edit("生成一个 SaaS 仪表盘")
            result1 = session.send("将颜色改为深色主题")
            result2 = session.send("添加一个侧边栏导航")
        """
        model = model or self.default_model
        return MultiTurnSession(self._get_client(), model, initial_prompt, aspect_ratio)

    def generate_ui_assets(
        self,
        asset_type: Literal["icon", "illustration", "background", "hero", "banner", "avatar"],
        description: str,
        style: str = "modern, clean, flat design",
        color_scheme: Optional[str] = None,
        model: Optional[str] = None,
        save_dir: Optional[Union[str, Path]] = None
    ) -> NanaBananaResult:
        """
        专为 UI 设计生成图像资产。
        FE Agent 的核心工具，用于生成图标、插图、背景等 UI 元素。

        参数：
            asset_type:    资产类型（icon/illustration/background/hero/banner/avatar）
            description:   资产描述
            style:         视觉风格（默认：现代简洁扁平设计）
            color_scheme:  配色方案（如 "blue and white, #1E40AF primary"）
            model:         使用的模型
            save_dir:      保存目录（文件名自动生成）

        返回：
            NanaBananaResult 对象
        """
        # 根据资产类型构建专业提示词
        asset_prompts = {
            "icon": f"A clean, minimal {description} icon. {style}. Transparent background. Vector-style. No text.",
            "illustration": f"A professional {description} illustration for a web application. {style}. High quality.",
            "background": f"A subtle, professional background for a {description} web application. {style}. Low contrast, suitable for text overlay.",
            "hero": f"A stunning hero section image for a {description} product. {style}. Wide format, suitable for a landing page.",
            "banner": f"A professional banner image for {description}. {style}. Horizontal format.",
            "avatar": f"A professional avatar/profile picture for {description}. {style}. Square format, centered subject.",
        }

        aspect_ratios = {
            "icon": "1:1",
            "illustration": "4:3",
            "background": "16:9",
            "hero": "21:9",
            "banner": "16:9",
            "avatar": "1:1",
        }

        prompt = asset_prompts.get(asset_type, description)
        if color_scheme:
            prompt += f" Color scheme: {color_scheme}."

        aspect_ratio = aspect_ratios.get(asset_type, "16:9")

        # 确定保存路径
        save_to = None
        if save_dir:
            save_dir = Path(save_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{asset_type}_{timestamp}.png"
            save_to = save_dir / filename

        return self.text_to_image(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            save_to=save_to
        )

    def generate_from_stitch(
        self,
        stitch_screenshot_path: Union[str, Path],
        enhancement_prompt: str = "Enhance the visual quality, make it more polished and professional",
        model: Optional[str] = None,
        save_to: Optional[Union[str, Path]] = None
    ) -> NanaBananaResult:
        """
        将 Stitch 设计截图转化为高质量图像资产。
        结合 Google Stitch 生成的 UI 截图和 Nano Banana 的图像增强能力。

        工作流：
          Stitch 生成 UI 截图 → Nano Banana 增强视觉质量 → 高质量图像资产

        参数：
            stitch_screenshot_path: Stitch 截图路径
            enhancement_prompt:     增强指令（默认：提升视觉质量和专业感）
            model:                  使用的模型（默认使用 Pro 版本以获得最佳质量）
            save_to:                保存路径

        返回：
            NanaBananaResult 对象
        """
        # 对于 Stitch 截图增强，优先使用 Pro 版本
        model = model or MODEL_NANO_BANANA_PRO

        full_prompt = (
            f"This is a UI design screenshot from Google Stitch. "
            f"{enhancement_prompt}. "
            f"Maintain the original layout and structure, but enhance the visual quality. "
            f"Make it look like a high-fidelity design mockup."
        )

        return self.image_to_image(
            prompt=full_prompt,
            reference_image=stitch_screenshot_path,
            model=model,
            save_to=save_to
        )

    def generate_design_variants(
        self,
        base_prompt: str,
        variant_descriptions: list[str],
        model: Optional[str] = None,
        save_dir: Optional[Union[str, Path]] = None
    ) -> list[NanaBananaResult]:
        """
        批量生成设计变体（用于 A/B 测试或设计方案比较）。

        参数：
            base_prompt:          基础设计描述
            variant_descriptions: 每个变体的差异描述列表
            model:                使用的模型
            save_dir:             保存目录

        返回：
            NanaBananaResult 列表
        """
        results = []
        for i, variant_desc in enumerate(variant_descriptions):
            full_prompt = f"{base_prompt}. Variant: {variant_desc}"

            save_to = None
            if save_dir:
                save_dir_path = Path(save_dir)
                save_to = save_dir_path / f"variant_{i+1}.png"

            result = self.text_to_image(
                prompt=full_prompt,
                model=model,
                save_to=save_to
            )
            results.append(result)

        return results

    def _parse_response(self, response, model: str,
                        save_to: Optional[Union[str, Path]] = None) -> NanaBananaResult:
        """解析 Gemini API 响应，提取图像数据"""
        image_data = None
        mime_type = "image/png"
        text_content = None

        for part in response.parts:
            if hasattr(part, 'text') and part.text:
                text_content = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/png"

        if image_data is None:
            # 尝试通过 as_image() 方法获取
            for part in response.parts:
                try:
                    img = part.as_image()
                    if img:
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        image_data = buf.getvalue()
                        break
                except Exception:
                    continue

        if image_data is None:
            raise RuntimeError(
                f"Nano Banana API 未返回图像数据。"
                f"文本响应: {text_content or '无'}"
            )

        result = NanaBananaResult(
            image_data=image_data,
            mime_type=mime_type,
            text=text_content,
            model=model
        )

        if save_to:
            result.save(save_to)

        return result

    def list_models(self) -> list[dict]:
        """返回可用的 Nano Banana 模型列表"""
        return [
            {
                "id": MODEL_NANO_BANANA_2,
                "name": "Nano Banana 2",
                "description": "高速、高并发，适合批量生成",
                "max_resolution": "2K",
                "supports_4k": False,
                "recommended_for": ["UI 资产批量生成", "快速原型", "设计变体"]
            },
            {
                "id": MODEL_NANO_BANANA_PRO,
                "name": "Nano Banana Pro",
                "description": "专业级，支持 4K，复杂指令，文字渲染精准",
                "max_resolution": "4K",
                "supports_4k": True,
                "recommended_for": ["高质量资产", "含文字的图像", "品牌素材"]
            },
            {
                "id": MODEL_NANO_BANANA,
                "name": "Nano Banana",
                "description": "速度优先，低延迟，适合实时预览",
                "max_resolution": "1K",
                "supports_4k": False,
                "recommended_for": ["实时预览", "快速验证", "低延迟场景"]
            }
        ]


class MultiTurnSession:
    """多轮对话式图像编辑会话"""

    def __init__(self, client, model: str, initial_prompt: str, aspect_ratio: str):
        from google.genai import types

        self._client = client
        self._model = model
        self._aspect_ratio = aspect_ratio
        self._history = []

        # 创建聊天会话
        self._chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio)
            )
        )

        # 发送初始提示
        self._initial_result = self._send_message(initial_prompt)

    def send(self, edit_prompt: str,
             save_to: Optional[Union[str, Path]] = None) -> NanaBananaResult:
        """发送编辑指令，继续编辑当前图像"""
        return self._send_message(edit_prompt, save_to)

    def _send_message(self, prompt: str,
                      save_to: Optional[Union[str, Path]] = None) -> NanaBananaResult:
        """发送消息并解析响应"""
        response = self._chat.send_message(prompt)

        image_data = None
        mime_type = "image/png"
        text_content = None

        for part in response.parts:
            if hasattr(part, 'text') and part.text:
                text_content = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/png"
            else:
                try:
                    img = part.as_image()
                    if img:
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        image_data = buf.getvalue()
                except Exception:
                    pass

        if image_data is None:
            raise RuntimeError(f"未收到图像数据。文本: {text_content}")

        result = NanaBananaResult(
            image_data=image_data,
            mime_type=mime_type,
            text=text_content,
            model=self._model
        )

        self._history.append({"prompt": prompt, "result": result})

        if save_to:
            result.save(save_to)

        return result

    @property
    def initial_result(self) -> NanaBananaResult:
        return self._initial_result

    def get_history(self) -> list[dict]:
        return self._history


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    client = NanaBananaClient()

    if len(sys.argv) > 1 and sys.argv[1] == "models":
        print("=== 可用 Nano Banana 模型 ===\n")
        for m in client.list_models():
            print(f"  {m['name']} ({m['id']})")
            print(f"    描述: {m['description']}")
            print(f"    最大分辨率: {m['max_resolution']}")
            print(f"    适用场景: {', '.join(m['recommended_for'])}")
            print()

    elif len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("=== Nano Banana Client 演示（需要 GOOGLE_API_KEY）===\n")

        if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
            print("⚠️  未设置 GOOGLE_API_KEY 或 GEMINI_API_KEY 环境变量")
            print("   请设置后重试: export GOOGLE_API_KEY=your_key")
            print("\n=== 模型列表（无需 API Key）===")
            for m in client.list_models():
                print(f"  {m['name']}: {m['description']}")
        else:
            print("正在生成 UI Hero 图像...")
            result = client.generate_ui_assets(
                asset_type="hero",
                description="SaaS project management dashboard",
                style="modern, dark theme, blue accent colors",
                color_scheme="#1E40AF primary, #0F172A background",
                save_dir="/tmp/nano_banana_test"
            )
            print(f"✅ 生成成功: {result}")
            print(f"   已保存到: /tmp/nano_banana_test/")

    else:
        print("用法:")
        print("  python3 engine/nano_banana_client.py models    # 列出可用模型")
        print("  python3 engine/nano_banana_client.py demo      # 演示模式（需要 API Key）")
        print()
        print("在代码中使用:")
        print("  from engine.nano_banana_client import NanaBananaClient")
        print("  client = NanaBananaClient()")
        print("  result = client.text_to_image('A modern dashboard')")
        print("  result.save('output.png')")
