from datetime import date

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage
from backend.app.utils.travel_intent_parser import TravelIntentReport
from backend.app.utils.weather_forcaster import WeatherReport,WeatherDetail

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
    )
    
    # 2. 新提取的意图：补充了人数和偏好
    new_report = TravelIntentReport(
        person_count=2,
        extra_needs_and_preferences=["想要靠窗位"],
    )
    
    merged = merge_travel_intent(old_report, new_report)
    
    # 验证：旧的地点保留了
    assert merged.repos[0].location == "北京"
    # 验证：偏好列表合并并去重了
    assert "靠近地铁" in merged.extra_needs_and_preferences
    assert "要有早饭" in merged.extra_needs_and_preferences
    # 验证：新字段被添加了
    assert merged.person_count == 2

# --- 2. 状态机集成测试（Mock LLM） ---
@pytest.mark.asyncio
async def test_graph_routing_travel_only():
    """测试当只有旅游意图时，图是否只走 travel_intent 节点"""
    
    # 模拟分类器的返回
    mock_classifier_result = MessageClassifier(
        next_action={"travel_intent": "去上海"},
        reasoning="用户想去上海旅游"
    )
    
    # 模拟 travel_intent 节点的返回
    mock_intent_report = TravelIntentReport(
        repos=[{"location": "上海", "temperature": 22.0, "condition": "阴", "suggestion": 0.8}]
    )

    # 使用 patch 模拟 LLM 和业务函数调用
    with patch("backend.app.core.llm.get_llm") as mock_get_llm, \
         patch("backend.app.services.travel_graph.get_TravelIntentReport", new_callable=AsyncMock) as mock_get_report:
        
        # 配置 Mock 行为
        mock_llm_instance = AsyncMock()
        mock_llm_instance.with_structured_output.return_value.ainvoke.return_value = mock_classifier_result
        mock_get_llm.return_value = mock_llm_instance
        mock_get_report.return_value = mock_intent_report

        # 执行图
        inputs = {"messages": [HumanMessage(content="我想去上海")]}
        final_state = await graph.ainvoke(inputs)

        # 断言
        assert "travel_intent" in final_state
        assert final_state["travel_intent"].repos[0].location == "上海"
        # 验证 weather 节点没被触碰（保持默认值 None）
        assert final_state.get("weather") is None

@pytest.mark.asyncio
async def test_graph_parallel_execution():
    """测试多意图并行触发逻辑"""
    
    # 模拟分类器：同时触发两个意图
    mock_classifier_result = MessageClassifier(
        next_action={
            "travel_intent": "去成都",
            "weather": "成都天气"
        },
        reasoning="用户同时询问了旅游和天气"
    )

    with patch("backend.app.core.llm.get_llm") as mock_get_llm, \
         patch("backend.app.services.travel_graph.get_TravelIntentReport", new_callable=AsyncMock) as mock_get_report, \
         patch("backend.app.services.travel_graph.get_weather_service", new_callable=AsyncMock) as mock_get_weather:
        
        mock_llm_instance = AsyncMock()
        mock_llm_instance.with_structured_output.return_value.ainvoke.return_value = mock_classifier_result
        mock_get_llm.return_value = mock_llm_instance
        
        # 执行
        inputs = {"messages": [HumanMessage(content="去成都玩顺便查查天气")]}
        final_state = await graph.ainvoke(inputs)

        # 验证两个业务节点都运行了
        assert mock_get_report.called
        assert mock_get_weather.called

# --- 3. 错误处理测试 ---
@pytest.mark.asyncio
async def test_graph_general_chat_ends():
    """测试当用户闲聊时，图是否正确结束而不调用业务节点"""
    
    mock_classifier_result = MessageClassifier(
        next_action={"general": "你好"},
        reasoning="用户只是在打招呼"
    )

    with patch("backend.app.core.llm.get_llm") as mock_get_llm:
        mock_llm_instance = AsyncMock()
        mock_llm_instance.with_structured_output.return_value.ainvoke.return_value = mock_classifier_result
        mock_get_llm.return_value = mock_llm_instance
        
        inputs = {"messages": [HumanMessage(content="你好呀")]}
        final_state = await graph.ainvoke(inputs)

        # 验证状态中没有生成报告
        assert final_state.get("travel_intent") is None
        assert final_state.get("weather") is None