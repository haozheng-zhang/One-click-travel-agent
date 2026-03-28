from langchain_core.messages import HumanMessage
import pytest
import asyncio
from datetime import date, timedelta
from backend.app.utils.travel_intent_parser import get_TravelIntentReport,TravelIntentReport

@pytest.mark.asyncio
async def test_travel_intent_basic():
    """测试基础意图识别"""
    query = "帮我订一张明天从上海去北京的高铁票"
    report = await get_TravelIntentReport(query)
    
    assert isinstance(report, TravelIntentReport)
    assert "上海" in report.origin
    assert "北京" in report.destinations[0].location
    assert report.transport_mode == "train"
    # 验证日期转换（今天+1天）
    assert report.departure_date == date.today() + timedelta(days=1)
    print(report.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_travel_intent_complex():
    """测试复杂多槽位填充"""
    query = "下周五我们一家三口想去三亚玩5天，人均预算5000，想要海景房"
    report = await get_TravelIntentReport(query)
    assert isinstance(report, TravelIntentReport)
    assert report.person_count == 3
    assert report.duration_days == 5
    assert "三亚" in report.destinations[0].location
    assert report.budget_per_person == 5000.0
    assert report.destinations[0].hotel_needed is True
    # 检查偏好设置是否被正确装入字典
    assert "海景房" in str(report.extra_needs_and_preferences)
    print(report.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_travel_intent_ambiguous():
    """测试模糊输入的鲁棒性"""
    query = "随便看看去哪儿玩比较好"
    report = await get_TravelIntentReport(query)
    
    # 即使信息缺失，也应返回模型实例，但字段多为 None
    assert isinstance(report, TravelIntentReport)
    assert len(report.destinations) == 0
    assert report.confidence == 0  # 模糊输入通常置信度较低
    print(report.model_dump_json(indent=2))