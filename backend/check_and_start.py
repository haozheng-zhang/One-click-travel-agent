"""
应用初始化与启动脚本
"""

import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_python_version():
    """检查 Python 版本"""
    if sys.version_info < (3, 10):
        print("❌ Python 版本过低，需要 3.10 或更高")
        sys.exit(1)
    print(f"✓ Python 版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def check_env_file():
    """检查 .env 文件是否存在"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            print("📝 .env 文件不存在，请从 .env.example 复制并填入实际值：")
            print(f"   cp .env.example .env")
        else:
            print("❌ .env 文件不存在，且 .env.example 也未找到")
        return False
    
    print("✓ .env 文件已配置")
    return True


def check_kimi_api_key():
    """检查 Kimi API Key"""
    api_key = os.getenv("KIMI_API_KEY")
    
    if not api_key or api_key == "your_kimi_api_key_here":
        print("❌ KIMI_API_KEY 未配置或使用了默认值")
        print("   请修改 .env 文件，设置实际的 Kimi API Key")
        print("   获取方式: https://console.moonshot.cn")
        return False
    
    # 只显示前几个字符和后几个字符
    masked_key = api_key[:4] + "***" + api_key[-4:]
    print(f"✓ Kimi API Key 已配置: {masked_key}")
    return True


def main():
    """初始化检查"""
    print("=" * 50)
    print("一键出行智能体 - 启动前检查")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_env_file,
        check_kimi_api_key,
    ]
    
    all_passed = True
    
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ 检查异常: {str(e)}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("✅ 所有检查已通过，可以启动应用")
        print("\n启动命令: python main.py")
        return 0
    else:
        print("❌ 检查未通过，请修复上述问题后重试")
        return 1


if __name__ == "__main__":
    sys.exit(main())
