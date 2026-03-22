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
    assert report.origin == "上海"
    assert report.destination == "北京"
    assert report.transport_mode == "train"
    # 验证日期转换（今天+1天）
    assert report.departure_date == date.today() + timedelta(days=1)
    assert "ticket_booking" in report.intent_type
    print(report.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_travel_intent_complex():
    """测试复杂多槽位填充"""
    query = "下周五我们一家三口想去三亚玩5天，人均预算5000，想要海景房"
    report = await get_TravelIntentReport(query)
    
    assert report.person_count == 3
    assert report.duration_days == 5
    assert report.destination == "三亚"
    assert report.budget_per_person == 5000.0
    assert report.hotel_needed is True
    # 检查偏好设置是否被正确装入字典
    assert "海景房" in str(report.preferences)
    print(report.model_dump_json(indent=2))

@pytest.mark.asyncio
async def test_travel_intent_ambiguous():
    """测试模糊输入的鲁棒性"""
    query = "随便看看去哪儿玩比较好"
    report = await get_TravelIntentReport(query)
    
    # 即使信息缺失，也应返回模型实例，但字段多为 None
    assert report.intent_type == "travel_planning"
    assert report.destination is None
    assert report.confidence < 1.0  # 模糊输入通常置信度较低
    print(report.model_dump_json(indent=2))