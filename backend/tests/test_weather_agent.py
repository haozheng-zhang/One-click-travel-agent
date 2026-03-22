#测试此agent的方法： pytest test_weather_agent.py -s

import pytest
from datetime import date
from backend.app.utils.weather_forcaster import weather_agent, WeatherReport  # 替换为你的实际路径

@pytest.mark.asyncio
async def test_weather_agent_basic_flow():
    """测试基础的天气查询流程"""
    # 1. 准备输入
    test_input = "帮我查查上海今明两天的天气，用摄氏度。"
    
    # 2. 执行 Agent
    # 注意：在测试环境中，你可能需要手动注入“今天”的日期到 Prompt
    result = await weather_agent.ainvoke({
            "messages": [{"role": "user", "content": test_input}]
    })
    print(result.keys())
    for i, msg in enumerate(result["messages"]):
        print(f"\n--- Message {i+1} ({msg.__class__.__name__}) ---")
        msg.pretty_print()
    # 3. 断言校验
    
    ai_msg = result["messages"][-2]
    assert hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls
    # ToolStrategy 输出在 tool_calls[0].args
    tool_args = ai_msg.tool_calls[0]["args"]
    report = WeatherReport.model_validate(tool_args)
    assert isinstance(report, WeatherReport)

    assert report.repos is not None
    assert "上海" in report.repos[0].location
    assert report.repos[0].units == "celsius"
    assert isinstance(report.suggestion, str)
    
    # 验证是否成功转化为 WeatherReport 实例
    
    
    # 验证关键字段
    assert "上海" in report.repos[0].location and "上海" in report.repos[1].location
    assert report.repos[0].units == "celsius"
    
    print(f"\n✓ 测试通过！解析到的目的地: {report.repos[0].location}")

@pytest.mark.asyncio
async def test_weather_agent_invalid_location():
    """测试面对模糊或无效输入时的表现"""
    test_input = "查查火星的天气"
    
    result = await weather_agent.ainvoke({
            "messages": [{"role": "user", "content": test_input}]
    })
    print(result.keys())
    for i, msg in enumerate(result["messages"]):
        print(f"\n--- Message {i+1} ({msg.__class__.__name__}) ---")
        msg.pretty_print()
    # 即使地点奇怪，Agent 也应该返回结构化数据，而不是崩溃
    ai_msg = result["messages"][-2]
    assert hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls
    # ToolStrategy 输出在 tool_calls[0].args
    tool_args = ai_msg.tool_calls[0]["args"]
    report = WeatherReport.model_validate(tool_args)
    assert isinstance(report, WeatherReport)
    print(f"\n✓ 火星测试通过！")