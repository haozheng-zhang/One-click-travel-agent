from datetime import date
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage
from backend.app.utils.travel_intent_parser import TravelIntentReport
from backend.app.utils.weather_forecaster import WeatherReport,WeatherDetail

# 导入你定义好的组件 (请根据实际路径修改)
from backend.app.core.gragh import (
    graph, 
    merge_travel_intent, 
    State, 
    MessageClassifier
)

# --- 1. 单元测试：Reducer 逻辑 ---
def test_merge_travel_intent_logic():
    """测试意图报告的增量合并功能"""
    # 初始状态：已经知道去北京
    old_report = TravelIntentReport(
        origin="上海",
        destination="北京",
        departure_date=date(2026, 5, 1),
        extra_needs_and_preferences={"旅途时间小于3小时"}
    )
    
    # 2. 新提取的意图：补充了人数和偏好
    new_report = TravelIntentReport(
        person_count=2,
        extra_needs_and_preferences={"想要靠窗位"},
    )
    
    merged = merge_travel_intent(old_report, new_report)
    
    assert merged.destination == "北京"
    assert merged.person_count == 2
    assert merged.extra_needs_and_preferences is not None
    assert "旅途时间小于3小时" in merged.extra_needs_and_preferences
    assert "想要靠窗位" in merged.extra_needs_and_preferences

@pytest.mark.asyncio
async def test_graph_e2e_live():
    """
    真实调用 LLM 的端到端测试
    注意：这会消耗真实的 Token
    """
    # 1. 准备真实的输入
    inputs: State = {
        "messages": [HumanMessage(content="我想下周从北京去上海玩三天，想看看那里的天气。")],
        "travel_intent": None,
        "weather": None,
        "next_action": {}
    }

    print("\n--- 正在调用 LLM，请稍候... ---")
    
    # 2. 运行 Graph
    # 使用 astream 可以看到每一阶段的输出，方便调试
    result = await graph.ainvoke(inputs)

    # 3. 打印真实结果方便观察
    print("\n[AI 提取的意图]:", result["travel_intent"].model_dump_json(indent=2))
    print("\n[AI 提取的动作]:")
    for key, value in result["next_action"].items():
        print(key, value)
    
    # 4. 更加鲁棒的断言
    # 真实 LLM 可能会返回 "上海" 或 "上海市"，所以用 'in' 比较稳妥
    assert result["travel_intent"] is not None
    assert "上海" in result["travel_intent"].destination
    assert "北京" in result["travel_intent"].origin
    
    # 如果你的天气节点也跑通了
    assert "weather" in result["next_action"]
    assert result["weather"] is not None
    print(f"[天气报告]: {result['weather'].model_dump_json(indent=2)}")