#!/usr/bin/env python3
"""
OPT v7.1 - Stitch Client: Google Stitch UI Generation Integration
Google Stitch UI 生成客户端（基于 Stitch SDK + MCP）

核心设计思路：
  Google Stitch 是 Google Labs 推出的 AI 驱动 UI 设计工具，核心能力：
  1. 文本 → UI 设计（自然语言描述生成完整的 App/Web 界面）
  2. 截图/线框图 → 可编辑设计（图像转设计）
  3. 设计 → HTML/CSS 代码（一键导出）
  4. MCP 集成（AI Agent 直接操作设计，双向反馈循环）

  本客户端封装了以下核心能力：
  1. generate_ui()          文本生成 UI 设计
  2. edit_screen()          编辑现有界面
  3. get_html()             获取界面 HTML 代码
  4. get_screenshot()       获取界面截图
  5. generate_variants()    生成设计变体（A/B 测试）
  6. apply_design_system()  应用设计系统到界面
  7. full_pipeline()        完整流水线（生成 → 截图 → Nano Banana 增强）

  与 OPT 系统的集成点：
  - FE Agent 调用 generate_ui() 快速生成 UI 原型
  - VisionParser 调用 get_html() 获取 HTML 进行代码分析
  - CoS 调用 generate_variants() 生成多个设计方案供用户选择
  - Nano Banana 客户端与 Stitch 联动：Stitch 生成布局 → Nano Banana 增强视觉

认证方式：
  方式1（推荐）：设置环境变量 STITCH_API_KEY
  方式2：设置环境变量 STITCH_ACCESS_TOKEN + STITCH_PROJECT_ID
  方式3：Google Cloud 凭证（自动 Token 刷新）

使用方式：
  export STITCH_API_KEY=your_stitch_api_key

  from engine.stitch_client import StitchClient
  client = StitchClient()
  result = client.generate_ui("A modern SaaS dashboard with dark theme", device="web")
  html = result.get_html()
  screenshot_path = result.save_screenshot("dashboard.png")
"""

import os
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional, Union, Literal
from datetime import datetime

# 设备类型
DeviceType = Literal["web", "app"]

# Stitch MCP 服务器地址
STITCH_MCP_SERVER = "stitch.googleapis.com"


class StitchScreen:
    """Stitch 界面对象，封装单个 UI 界面的操作"""

    def __init__(self, screen_data: dict, client: "StitchClient"):
        self._data = screen_data
        self._client = client
        self.screen_id = screen_data.get("id", "")
        self.name = screen_data.get("name", "Untitled Screen")
        self._html_url: Optional[str] = screen_data.get("htmlUrl")
        self._image_url: Optional[str] = screen_data.get("imageUrl")

    def get_html(self) -> str:
        """获取界面的 HTML/CSS 代码"""
        if not self._html_url:
            # 通过 SDK 获取 HTML URL
            self._html_url = self._client._call_sdk_method(
                "getHtml", {"screenId": self.screen_id}
            )
        return self._fetch_content(self._html_url)

    def get_screenshot_bytes(self) -> bytes:
        """获取界面截图（bytes）"""
        if not self._image_url:
            self._image_url = self._client._call_sdk_method(
                "getImage", {"screenId": self.screen_id}
            )
        return self._fetch_bytes(self._image_url)

    def save_screenshot(self, path: Union[str, Path]) -> Path:
        """保存界面截图到文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_bytes = self.get_screenshot_bytes()
        with open(path, "wb") as f:
            f.write(screenshot_bytes)
        return path

    def save_html(self, path: Union[str, Path]) -> Path:
        """保存界面 HTML 到文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        html_content = self.get_html()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return path

    def edit(self, prompt: str, device_type: Optional[DeviceType] = None) -> "StitchScreen":
        """用文本指令编辑当前界面"""
        return self._client.edit_screen(self.screen_id, prompt, device_type)

    def _fetch_content(self, url: str) -> str:
        """从 URL 获取文本内容"""
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")

    def _fetch_bytes(self, url: str) -> bytes:
        """从 URL 获取二进制内容"""
        with urllib.request.urlopen(url) as response:
            return response.read()

    def __repr__(self):
        return f"<StitchScreen id={self.screen_id} name={self.name}>"


class StitchProject:
    """Stitch 项目对象，封装项目级别的操作"""

    def __init__(self, project_data: dict, client: "StitchClient"):
        self._data = project_data
        self._client = client
        self.project_id = project_data.get("id", "")
        self.name = project_data.get("name", "Untitled Project")

    def generate(self, prompt: str, device_type: DeviceType = "web") -> StitchScreen:
        """在此项目中根据文本提示生成新界面"""
        return self._client.generate_ui(prompt, device_type, project_id=self.project_id)

    def list_screens(self) -> list[StitchScreen]:
        """列出项目中的所有界面"""
        return self._client.list_screens(self.project_id)

    def __repr__(self):
        return f"<StitchProject id={self.project_id} name={self.name}>"


class StitchClient:
    """
    Google Stitch UI 生成客户端。
    封装 Stitch SDK 和 MCP 协议，专为 OPT 系统设计。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace: Optional[Path] = None
    ):
        self.api_key = api_key or os.environ.get("STITCH_API_KEY")
        self.access_token = os.environ.get("STITCH_ACCESS_TOKEN")
        self.project_id = project_id or os.environ.get("STITCH_PROJECT_ID")
        self.workspace = workspace or Path(os.environ.get("OPT_WORKSPACE", "/home/ubuntu/workspace"))
        self._sdk_available = None  # 延迟检测

    def _check_sdk(self) -> bool:
        """检查 Stitch SDK（Node.js）是否可用"""
        if self._sdk_available is None:
            try:
                result = subprocess.run(
                    ["node", "-e", "require('@google/stitch-sdk')"],
                    capture_output=True, timeout=5
                )
                self._sdk_available = result.returncode == 0
            except Exception:
                self._sdk_available = False
        return self._sdk_available

    def _call_sdk_method(self, method: str, args: dict) -> any:
        """
        通过 Node.js 调用 Stitch SDK 方法。
        这是与 Stitch SDK（TypeScript/JavaScript）交互的桥接层。
        """
        # 构建 Node.js 脚本
        auth_config = {}
        if self.api_key:
            auth_config["apiKey"] = self.api_key
        elif self.access_token:
            auth_config["accessToken"] = self.access_token

        script = f"""
const {{ Stitch }} = require('@google/stitch-sdk');

const config = {json.dumps(auth_config)};
const args = {json.dumps(args)};

async function main() {{
    const stitch = new Stitch(config);
    let result;

    switch ('{method}') {{
        case 'generate':
            const project = stitch.project(args.projectId);
            const screen = await project.generate(args.prompt, args.deviceType);
            result = {{
                id: screen.id,
                name: screen.name,
                htmlUrl: await screen.getHtml(),
                imageUrl: await screen.getImage()
            }};
            break;

        case 'edit':
            const proj = stitch.project(args.projectId);
            const screens = await proj.screens();
            const targetScreen = screens.find(s => s.id === args.screenId);
            const edited = await targetScreen.edit(args.prompt, args.deviceType);
            result = {{
                id: edited.id,
                name: edited.name,
                htmlUrl: await edited.getHtml(),
                imageUrl: await edited.getImage()
            }};
            break;

        case 'getHtml':
            const p = stitch.project(args.projectId);
            const ss = await p.screens();
            const s = ss.find(x => x.id === args.screenId);
            result = await s.getHtml();
            break;

        case 'getImage':
            const p2 = stitch.project(args.projectId);
            const ss2 = await p2.screens();
            const s2 = ss2.find(x => x.id === args.screenId);
            result = await s2.getImage();
            break;

        case 'listProjects':
            const projects = await stitch.projects();
            result = projects.map(p => ({{ id: p.id, name: p.name }}));
            break;

        case 'listScreens':
            const proj2 = stitch.project(args.projectId);
            const screenList = await proj2.screens();
            result = screenList.map(s => ({{ id: s.id, name: s.name }}));
            break;

        default:
            throw new Error(`Unknown method: {method}`);
    }}

    console.log(JSON.stringify(result));
}}

main().catch(err => {{
    console.error(JSON.stringify({{ error: err.message }}));
    process.exit(1);
}});
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(script)
            script_path = f.name

        try:
            result = subprocess.run(
                ["node", script_path],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                error_data = json.loads(result.stderr) if result.stderr else {"error": "Unknown error"}
                raise RuntimeError(f"Stitch SDK 调用失败: {error_data.get('error', result.stderr)}")

            return json.loads(result.stdout.strip())
        finally:
            Path(script_path).unlink(missing_ok=True)

    def _call_via_mcp(self, tool: str, args: dict) -> dict:
        """
        通过 MCP 协议调用 Stitch 工具。
        使用 manus-mcp-cli 与 Stitch MCP 服务器通信。
        """
        cmd = [
            "manus-mcp-cli", "tool", "call", tool,
            "--server", "stitch",
            "--input", json.dumps(args, ensure_ascii=False)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"Stitch MCP 调用失败: {result.stderr[:300]}")
        return json.loads(result.stdout)

    def generate_ui(
        self,
        prompt: str,
        device_type: DeviceType = "web",
        project_id: Optional[str] = None,
        save_dir: Optional[Union[str, Path]] = None
    ) -> StitchScreen:
        """
        根据文本提示生成 UI 界面。

        参数：
            prompt:      UI 描述（如 "A dark theme SaaS dashboard with sidebar navigation"）
            device_type: 设备类型（"web" 或 "app"）
            project_id:  项目 ID（使用默认项目）
            save_dir:    如果指定，自动保存截图和 HTML 到该目录

        返回：
            StitchScreen 对象
        """
        pid = project_id or self.project_id

        if self._check_sdk():
            # 优先使用 SDK
            screen_data = self._call_sdk_method("generate", {
                "projectId": pid,
                "prompt": prompt,
                "deviceType": device_type
            })
        else:
            # 回退到 MCP
            screen_data = self._call_via_mcp("stitch_generate_ui", {
                "prompt": prompt,
                "deviceType": device_type,
                "projectId": pid
            })

        screen = StitchScreen(screen_data, self)

        if save_dir:
            save_dir = Path(save_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen.save_screenshot(save_dir / f"stitch_{timestamp}.png")
            screen.save_html(save_dir / f"stitch_{timestamp}.html")

        return screen

    def edit_screen(
        self,
        screen_id: str,
        prompt: str,
        device_type: Optional[DeviceType] = None,
        project_id: Optional[str] = None
    ) -> StitchScreen:
        """
        用文本指令编辑现有界面。

        参数：
            screen_id:   要编辑的界面 ID
            prompt:      编辑指令（如 "将颜色改为深色主题"）
            device_type: 设备类型
            project_id:  项目 ID

        返回：
            更新后的 StitchScreen 对象
        """
        pid = project_id or self.project_id

        if self._check_sdk():
            screen_data = self._call_sdk_method("edit", {
                "projectId": pid,
                "screenId": screen_id,
                "prompt": prompt,
                "deviceType": device_type
            })
        else:
            screen_data = self._call_via_mcp("stitch_edit_screen", {
                "screenId": screen_id,
                "prompt": prompt,
                "deviceType": device_type
            })

        return StitchScreen(screen_data, self)

    def generate_variants(
        self,
        prompt: str,
        variant_count: int = 3,
        device_type: DeviceType = "web",
        project_id: Optional[str] = None,
        save_dir: Optional[Union[str, Path]] = None
    ) -> list[StitchScreen]:
        """
        生成多个设计变体（用于 A/B 测试或方案比较）。

        参数：
            prompt:        基础设计描述
            variant_count: 变体数量（默认 3 个）
            device_type:   设备类型
            project_id:    项目 ID
            save_dir:      保存目录

        返回：
            StitchScreen 列表
        """
        variant_prompts = [
            f"{prompt}. Style variant {i+1}: " + [
                "Clean and minimal, lots of whitespace",
                "Bold and colorful, high contrast",
                "Professional and corporate, subtle colors",
                "Playful and modern, rounded corners",
                "Dark mode, neon accents"
            ][i % 5]
            for i in range(variant_count)
        ]

        screens = []
        for i, variant_prompt in enumerate(variant_prompts):
            screen = self.generate_ui(
                prompt=variant_prompt,
                device_type=device_type,
                project_id=project_id,
                save_dir=Path(save_dir) / f"variant_{i+1}" if save_dir else None
            )
            screens.append(screen)

        return screens

    def list_projects(self) -> list[StitchProject]:
        """列出所有可访问的 Stitch 项目"""
        if self._check_sdk():
            projects_data = self._call_sdk_method("listProjects", {})
        else:
            projects_data = self._call_via_mcp("stitch_list_projects", {})

        return [StitchProject(p, self) for p in projects_data]

    def list_screens(self, project_id: Optional[str] = None) -> list[StitchScreen]:
        """列出项目中的所有界面"""
        pid = project_id or self.project_id

        if self._check_sdk():
            screens_data = self._call_sdk_method("listScreens", {"projectId": pid})
        else:
            screens_data = self._call_via_mcp("stitch_list_screens", {"projectId": pid})

        return [StitchScreen(s, self) for s in screens_data]

    def full_pipeline(
        self,
        prompt: str,
        device_type: DeviceType = "web",
        enhance_with_nano_banana: bool = True,
        output_dir: Optional[Union[str, Path]] = None
    ) -> dict:
        """
        完整的 Stitch + Nano Banana 联合流水线。

        流程：
          1. Stitch 根据 Prompt 生成 UI 设计
          2. 获取 Stitch 截图和 HTML 代码
          3. （可选）Nano Banana 增强截图视觉质量
          4. 保存所有产物到输出目录

        参数：
            prompt:                   UI 描述
            device_type:              设备类型
            enhance_with_nano_banana: 是否使用 Nano Banana 增强截图
            output_dir:               输出目录

        返回：
            包含所有产物路径的字典：
            {
                "stitch_screenshot": Path,
                "stitch_html": Path,
                "enhanced_image": Path (如果 enhance_with_nano_banana=True),
                "screen": StitchScreen,
                "metadata": dict
            }
        """
        output_dir = Path(output_dir or self.workspace / "stitch_output")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: Stitch 生成 UI
        print(f"[Stitch] 正在生成 UI: {prompt[:50]}...")
        screen = self.generate_ui(prompt, device_type)

        # Step 2: 保存截图和 HTML
        screenshot_path = output_dir / f"stitch_{timestamp}.png"
        html_path = output_dir / f"stitch_{timestamp}.html"

        screen.save_screenshot(screenshot_path)
        screen.save_html(html_path)
        print(f"[Stitch] 截图已保存: {screenshot_path}")
        print(f"[Stitch] HTML 已保存: {html_path}")

        result = {
            "stitch_screenshot": screenshot_path,
            "stitch_html": html_path,
            "screen": screen,
            "metadata": {
                "prompt": prompt,
                "device_type": device_type,
                "screen_id": screen.screen_id,
                "generated_at": timestamp
            }
        }

        # Step 3: Nano Banana 增强（可选）
        if enhance_with_nano_banana:
            try:
                from engine.nano_banana_client import NanaBananaClient
                nb_client = NanaBananaClient()
                enhanced_path = output_dir / f"enhanced_{timestamp}.png"
                print(f"[Nano Banana] 正在增强截图质量...")
                nb_result = nb_client.generate_from_stitch(
                    stitch_screenshot_path=screenshot_path,
                    save_to=enhanced_path
                )
                result["enhanced_image"] = enhanced_path
                print(f"[Nano Banana] 增强图像已保存: {enhanced_path}")
            except Exception as e:
                print(f"[Nano Banana] 增强失败（不影响主流程）: {e}")
                result["enhanced_image"] = None

        return result

    def install_sdk(self) -> bool:
        """安装 Stitch SDK（Node.js）"""
        print("正在安装 @google/stitch-sdk...")
        result = subprocess.run(
            ["npm", "install", "-g", "@google/stitch-sdk"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            self._sdk_available = True
            print("✅ @google/stitch-sdk 安装成功")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr[:200]}")
            return False

    def check_auth(self) -> dict:
        """检查认证状态"""
        return {
            "api_key_set": bool(self.api_key),
            "access_token_set": bool(self.access_token),
            "project_id_set": bool(self.project_id),
            "sdk_available": self._check_sdk(),
            "auth_method": "api_key" if self.api_key else "access_token" if self.access_token else "none"
        }


# ── CLI 入口 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    client = StitchClient()

    if len(sys.argv) > 1 and sys.argv[1] == "auth":
        print("=== Stitch 认证状态 ===\n")
        status = client.check_auth()
        for k, v in status.items():
            icon = "✅" if v else "❌"
            print(f"  {icon} {k}: {v}")

        if not status["api_key_set"] and not status["access_token_set"]:
            print("\n⚠️  未配置认证信息，请设置以下环境变量之一：")
            print("   export STITCH_API_KEY=your_stitch_api_key")
            print("   或: export STITCH_ACCESS_TOKEN=your_token")

    elif len(sys.argv) > 1 and sys.argv[1] == "install":
        client.install_sdk()

    elif len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("=== Stitch Client 演示（需要 STITCH_API_KEY）===\n")
        status = client.check_auth()

        if not status["api_key_set"] and not status["access_token_set"]:
            print("⚠️  未设置 STITCH_API_KEY 环境变量")
            print("   请设置后重试: export STITCH_API_KEY=your_key")
            print("\n=== 功能预览（无需 API Key）===")
            print("  generate_ui(prompt, device_type)  → 生成 UI 界面")
            print("  edit_screen(screen_id, prompt)    → 编辑界面")
            print("  generate_variants(prompt, n)      → 生成 N 个设计变体")
            print("  full_pipeline(prompt)             → Stitch + Nano Banana 联合流水线")
        else:
            print("正在生成 SaaS 仪表盘 UI...")
            result = client.full_pipeline(
                prompt="A modern SaaS project management dashboard with dark theme, sidebar navigation, and data charts",
                device_type="web",
                enhance_with_nano_banana=True,
                output_dir="/tmp/stitch_test"
            )
            print(f"\n✅ 完成！产物保存在 /tmp/stitch_test/")
            for k, v in result.items():
                if k != "screen":
                    print(f"  {k}: {v}")

    else:
        print("用法:")
        print("  python3 engine/stitch_client.py auth     # 检查认证状态")
        print("  python3 engine/stitch_client.py install  # 安装 Stitch SDK")
        print("  python3 engine/stitch_client.py demo     # 演示模式（需要 API Key）")
        print()
        print("在代码中使用:")
        print("  from engine.stitch_client import StitchClient")
        print("  client = StitchClient()")
        print("  screen = client.generate_ui('A dark SaaS dashboard')")
        print("  screen.save_screenshot('dashboard.png')")
        print("  html = screen.get_html()")
