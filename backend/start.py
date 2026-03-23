#!/usr/bin/env python3
"""
一键出行智能体 - 启动脚本
支持多种启动模式
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """打印欢迎横幅"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║          一键出行智能体 - 启动助手 v0.1.0                 ║
║        聚合所有出行需求的AI智能体 (MVP版)                 ║
╚═══════════════════════════════════════════════════════════╝
    """)


def check_environment():
    """检查环境配置"""
    print("\\n📋 环境检查...\n")
    
    checks = {
        "Python 版本": check_python_version,
        ".env 文件配置": check_env_file,
        "Kimi API Key": check_kimi_api_key,
        "依赖包": check_dependencies,
    }
    
    all_passed = True
    
    for check_name, check_func in checks.items():
        try:
            result = check_func()
            if result:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_passed = False
        except Exception as e:
            print(f"  ⚠️  {check_name}: {str(e)}")
            all_passed = False
    
    return all_passed


def check_python_version():
    """检查 Python 版本"""
    if sys.version_info >= (3, 10):
        return True
    print(f"    错误: Python {sys.version_info.major}.{sys.version_info.minor} 过低，需要 3.10+")
    return False

# 可以重构为从setting中获取环境变量
def check_env_file():
    """检查 .env 文件"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        print(f"    📝 .env 文件不存在，请运行: cp .env.example .env")
        return False
    return True


def check_kimi_api_key():
    """检查 Kimi API Key"""
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    
    if not api_key or api_key == "your_kimi_api_key_here":
        print("    ⚠️  KIMI_API_KEY 未配置或使用默认值")
        print("    获取方式: https://console.moonshot.cn")
        return False
    return True


def check_dependencies():
    """检查依赖包"""
    try:
        import fastapi  # noqa
        import langchain  # noqa
        return True
    except ImportError:
        print("    运行: pip install -r requirements.txt")
        return False


def show_menu():
    """显示启动菜单"""
    print("\n🚀 选择启动模式:\n")
    print("  1. 🧪 快速测试 (推荐首选)")
    print("     - 直接测试 NLU 模块")
    print("     - 无需启动服务")
    print("     - 包含 4 个测试用例")
    print()
    print("  2. 🌐 启动完整服务")
    print("     - 启动 FastAPI 后端")
    print("     - 访问 http://localhost:8000/api/docs")
    print("     - 支持前端连接")
    print()
    print("  3. 🎨 启动前端 Web UI")
    print("     - 打开浏览器访问前端")
    print("     - 需要后端服务已启动")
    print()
    print("  4. 🔗 同时启动后端和前端")
    print("     - 一键启动完整系统")
    print("     - 需要两个终端窗口")
    print()
    print("  5. 📖 查看文档")
    print("     - 导航到文档目录")
    print()
    print("  6. ⚙️  配置向导")
    print("     - 帮助配置 Kimi API Key")
    print()
    print("  0. ❌ 退出")
    print()


def launch_quick_test():
    """启动快速测试"""
    print("\n🧪 启动快速测试...\\n")
    try:
        subprocess.run([sys.executable, "test_quick.py"], check=True)
    except FileNotFoundError:
        print("❌ test_quick.py 文件不存在")
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试失败: {e}")
    except KeyboardInterrupt:
        print("\\n⚠️  测试被中断")


def launch_server():
    """启动后端服务"""
    print("\n🌐 启动后端服务...\\n")
    print("启动信息:")
    print("  • 后端地址: http://localhost:8000")
    print("  • API 文档: http://localhost:8000/api/docs")
    print("  • 健康检查: http://localhost:8000/api/v1/health")
    print()
    print("按 Ctrl+C 停止服务\\n")
    
    try:
        subprocess.run(
            [sys.executable, "main.py"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\\n🛑 后端服务已停止")


def open_frontend():
    """打开前端页面"""
    print("\n🎨 打开前端 Web UI...\\n")
    
    frontend_path = Path("../frontend/index.html").resolve()
    
    if not frontend_path.exists():
        print(f"❌ 前端文件不存在: {frontend_path}")
        return
    
    file_url = f"file:///{frontend_path}".replace("\\\\", "/")
    
    print(f"📄 前端路径: {frontend_path}")
    print(f"🔗 访问地址: {file_url}")
    print()
    print("⚠️  确保后端服务已启动 (选项 2)")
    print()
    
    import webbrowser
    webbrowser.open(file_url)
    print("✓ 浏览器已打开前端页面")


def launch_both():
    """同时启动后端和前端"""
    print("\n⚙️  需要两个终端窗口:\n")
    print("终端 1 (后端服务):")
    print("  cd c:\\一键出行\\backend")
    print("  python main.py")
    print()
    print("终端 2 (前端页面):")
    print("  访问: file:///c:/一键出行/frontend/index.html")
    print()
    print("或者运行此脚本，选择选项 2 和 3")


def show_docs():
    """显示文档导航"""
    print("\n📖 文档导航\\n")
    
    docs = {
        "1": ("快速开始 (QUICKSTART.md)", "快速启动指南"),
        "2": ("系统架构 (architecture.md)", "详细的技术架构"),
        "3": ("API 设计 (api-design.md)", "完整的 API 文档"),
        "4": ("项目总结 (PROJECT_SUMMARY.md)", "MVP 完成总结"),
        "5": ("项目 README", "项目概述"),
    }
    
    for key, (file, desc) in docs.items():
        print(f"  {key}. {file}")
        print(f"     {desc}")
    
    print("\\n  0. 返回菜单")


def setup_wizard():
    """配置向导"""
    print("\n⚙️  Kimi API Key 配置向导\\n")
    
    api_key = input("请输入你的 Kimi API Key (或按 Enter 跳过): ").strip()
    
    if not api_key:
        print("⏭️  跳过配置")
        return
    
    env_path = Path(".env")
    
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 替换或添加 KIMI_API_KEY
        if "KIMI_API_KEY=" in content:
            content = content.replace(
                [line for line in content.split("\\n") if line.startswith("KIMI_API_KEY=")][0],
                f"KIMI_API_KEY={api_key}"
            )
        else:
            content += f"\\nKIMI_API_KEY={api_key}"
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"KIMI_API_KEY={api_key}\\nENVIRONMENT=development\\n")
    
    print("✅ .env 文件已更新")


def main():
    """主程序"""
    
    # 检查是否在 backend 目录
    if not Path("main.py").exists():
        print("❌ 请在 backend 目录下运行此脚本")
        print("   cd c:\\一键出行\\backend")
        sys.exit(1)
    
    print_banner()
    
    # 首次检查环境
    if not check_environment():
        print("\n⚠️  某些环境检查未通过，继续可能会出错")
        response = input("\\n是否继续? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)
    else:
        print("\n✅ 环境检查通过！")
    
    # 主菜单循环
    while True:
        show_menu()
        choice = input("请选择 (输入数字): ").strip()
        
        if choice == "1":
            launch_quick_test()
        elif choice == "2":
            launch_server()
        elif choice == "3":
            open_frontend()
        elif choice == "4":
            launch_both()
        elif choice == "5":
            show_docs()
        elif choice == "6":
            setup_wizard()
        elif choice == "0":
            print("\n👋 再见！")
            break
        else:
            print("❌ 无效的选择")
        
        if choice in ["2"]:  # 长时间运行的任务后
            break
        
        input("\n按 Enter 返回菜单...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\\n\n👋 程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)
