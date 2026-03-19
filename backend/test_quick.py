"""
快速测试脚本 - 无需启动服务，直接测试意图解析
"""
import logging
import asyncio
import logging
import sys
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_intent_parsing():
    """测试意图解析模块"""
    
    print("\n" + "=" * 60)
    print("一键出行智能体 - 意图解析模块测试")
    print("=" * 60 + "\n")
    
    try:
        # 导入 NLU 模块
        from app.core.nlu import parse_travel_intent
        from app.config import settings
        
        # 检查 API Key
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_deepseek_api_key_here":
            print("❌ deepseek API Key 未配置！")
            print("   请在 .env 文件中设置 DEEPSEEK_API_KEY")
            return False
        
        # 测试样例
        test_cases = [
            {
                "name": "完整出行规划",
                "input": "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"
            },
            {
                "name": "基础信息",
                "input": "我想3月25号从上海去杭州，2天1晚"
            },
            {
                "name": "模糊需求",
                "input": "我想出去玩，考虑去西南地区"
            },
            {
                "name": "多目的地",
                "input": "规划一个云南环线：昆明→大理→丽江→泸沽湖，6天5晚，2个人，3000块钱一个人"
            },
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n【测试 {i}】{test_case['name']}")
            print(f"输入: {test_case['input']}")
            print("-" * 60)
            
            result = await parse_travel_intent(test_case["input"])
            
            if result.success:
                intent = result.travel_intent
                
                #print(f"✓ 意图识别成功")
                logging.debug("✓ 意图识别成功")
                print(f"  置信度: {intent.confidence:.0%}")
                print(f"  意图类型: {intent.intent_type}")
                print(f"\n  提取的参数:")
                print(f"    出发地: {intent.origin}")
                print(f"    目的地: {intent.destination}")
                print(f"    出发日期: {intent.departure_date}")
                print(f"    返回日期: {intent.return_date}")
                print(f"    行程天数: {intent.duration_days}")
                print(f"    人数: {intent.person_count}")
                print(f"    交通方式: {intent.transport_mode}")
                print(f"    人均预算: {intent.budget_per_person}")
                
                if intent.auto_filled_fields:
                    print(f"\n  自动补全的字段: {', '.join(intent.auto_filled_fields)}")
                
                if result.suggestions:
                    print(f"\n  建议:")
                    for suggestion in result.suggestions:
                        print(f"    {suggestion}")
                
                print(f"\n  下一步: {result.next_step}")
            else:
                print(f"✗ 意图识别失败")
                print(f"  错误: {result.error_message}")
                if result.suggestions:
                    for suggestion in result.suggestions:
                        print(f"  建议: {suggestion}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60 + "\n")
        print("提示:")
        print("  1. 如果需要启动 API 服务，运行: python main.py")
        print("  2. 然后访问: http://localhost:8000/api/docs (Swagger UI)")
        print("  3. 查看完整架构: docs/architecture.md")
        print()
        
        return True
    
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        print("   请确保已安装所有依赖: pip install -r requirements.txt")
        return False
    except ValueError as e:
        print(f"❌ 配置错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    
    # 检查当前目录
    if not Path("app").exists():
        print("❌ 请在 backend 目录下运行此脚本")
        return 1
    
    success = await test_intent_parsing()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
