import pytest
import os
from backend.app.utils.weather_forecaster import get_weather_service, WeatherReport


@pytest.mark.asyncio
async def test_get_weather_service_live():
    """
    真实调用 Tavily 和 LLM 的端到端测试。
    注意：这会消耗真实的 API Token。
    """
    # 1. 准备一个具体的查询词（包含相对时间，测试 Classifier 的前置效果）
    # 假设 Classifier 已经把“明天”转成了具体的日期描述
    test_query = "2026-03-24 上海的天气预报"
    
    print(f"\n[🚀 开始实战测试] 查询词: {test_query}")

    # 2. 执行真实调用
    try:
        report = await get_weather_service(test_query)
        
        # 3. 打印实时返回结果，方便观察 AI 的提取质量
        print(report.model_dump_json(indent=2))

        # 4. 核心断言
        assert isinstance(report, WeatherReport), "返回类型错误"
        assert report.status is True, f"接口返回失败: {report.message}"
        assert len(report.repos) >= 1, "未提取到任何天气详情"
        assert "上海" in report.repos[0].location, f"地点解析错误: {report.repos[0].location}"
        
    except Exception as e:
        pytest.fail(f"实战测试中发生未预期错误: {e}")

@pytest.mark.asyncio
async def test_get_weather_service_invalid_location_live():
    """
    测试极端情况：搜索一个不存在的地方
    """
    report = await get_weather_service("克卜勒-452b 行星的天气")
    
    print(f"\n[👽 极端情况测试] 消息: {report.message}")
    # 即使失败，也应该返回一个合法的 WeatherReport 对象，而不是崩溃
    assert isinstance(report, WeatherReport)
    print(report.model_dump_json(indent=2))
    # 理想情况下，AI 应该能识别出搜不到，并设置 status 为 False
    assert report.status is False