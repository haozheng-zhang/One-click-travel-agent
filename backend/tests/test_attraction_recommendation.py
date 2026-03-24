import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import date
from backend.app.utils.attraction_recommendation import (
    recommend_attractions,
    get_ticket_info,
    book_attraction_ticket,
    _search_attraction,
    _get_optimal_tickets,
    _call_recommendation_api,
    _call_ticket_api,
    _execute_recommend_attractions,
    _execute_get_ticket_info,
    _execute_book_attraction_ticket,
    AttractionTicketBookingIntent,
)


@pytest.mark.asyncio
async def test_workflow_step1_recommend_attractions_for_city():
    """
    【工作流step1】推荐指定城市的景点
    
    使用场景：用户说"我想去北京" → 推荐北京的所有景点列表
    函数调用：recommend_attractions(destination="北京")
    """
    
    # 模拟北京景点推荐API响应
    mock_response = {
        "attractions": [
            {
                "id": "forbidden_city_001",
                "name": "故宫博物院",
                "location": "北京市东城区",
                "rating": 4.8,
                "description": "中国最大的古代建筑群",
                "ticket_price": 60
            },
            {
                "id": "great_wall_001",
                "name": "长城",
                "location": "北京市延庆区",
                "rating": 4.9,
                "description": "世界文化遗产",
                "ticket_price": 40
            },
            {
                "id": "summer_palace_001",
                "name": "颐和园",
                "location": "北京市海淀区",
                "rating": 4.7,
                "description": "中国最大的皇家园林",
                "ticket_price": 30
            }
        ]
    }

    with patch("backend.app.utils.attraction_recommendation._call_recommendation_api") as mock_call:
        mock_call.return_value = mock_response

        # 调用内部执行函数
        result = await _execute_recommend_attractions(
            destination="北京",
            travel_days=3,
            budget="中等"
        )
        
        # 验证返回了所有景点
        assert "故宫博物院" in result
        assert "长城" in result
        assert "颐和园" in result
        assert "请从上面选择一个景点名称" in result  # 提示用户选择


@pytest.mark.asyncio
async def test_get_ticket_info_success():
    """获取景点的门票信息和购买链接"""
    
    mock_ticket_response = {
        "tickets": [
            {
                "description": "成人票",
                "price": 60,
                "availability": True,
                "purchase_url": "https://ticketing.example.com/order/001"
            },
            {
                "description": "学生票",
                "price": 30,
                "availability": True,
                "purchase_url": "https://ticketing.example.com/order/002"
            }
        ]
    }

    with patch("backend.app.utils.attraction_recommendation._call_ticket_api") as mock_call:
        mock_call.return_value = mock_ticket_response

        result = await _execute_get_ticket_info(
            attraction_id="forbidden_city_001",
            ticket_type="all"
        )
        
        assert "成人票" in result
        assert "学生票" in result
        assert "https://ticketing.example.com" in result


@pytest.mark.asyncio
async def test_recommend_attractions_no_results():
    """推荐城市不存在的情况"""
    
    mock_response = {"attractions": []}

    with patch("backend.app.utils.attraction_recommendation._call_recommendation_api") as mock_call:
        mock_call.return_value = mock_response
        result = await _execute_recommend_attractions(
            destination="火星",
            travel_days=1
        )
        assert "未找到关于" in result or "抱歉" in result


@pytest.mark.asyncio
async def test_get_ticket_info_no_availability():
    """门票已售罄的情况"""
    
    mock_response = {
        "tickets": [
            {
                "description": "暂无可购票",
                "availability": False
            }
        ]
    }

    with patch("backend.app.utils.attraction_recommendation._call_ticket_api") as mock_call:
        mock_call.return_value = mock_response
        result = await _execute_get_ticket_info(attraction_id="001")
        assert "已售罄" in result or "暂无" in result


@pytest.mark.asyncio
async def test_recommend_attractions_api_error():
    """推荐 API 调用发生异常"""
    
    with patch("backend.app.utils.attraction_recommendation._call_recommendation_api") as mock_call:
        mock_call.side_effect = Exception("推荐服务暂时不可用")
        result = await _execute_recommend_attractions(
            destination="西安",
            travel_days=1
        )
        assert "推荐异常" in result


@pytest.mark.asyncio
async def test_get_ticket_purchase_error():
    """门票购买 API 调用发生异常"""
    
    with patch("backend.app.utils.attraction_recommendation._call_ticket_api") as mock_call:
        mock_call.side_effect = Exception("支付服务连接失败")
        result = await _execute_get_ticket_info(attraction_id="001")
        assert "获取门票信息异常" in result


@pytest.mark.asyncio
async def test_workflow_step2_book_attraction_ticket_success():
    """
    【工作流step2】景点门票预订 - 从景点选择直达付款界面
    
    使用场景：
    1. 用户从推荐列表中选择景点："故宫"
    2. 用户提供人数信息："3个成人、1个儿童"、访问日期等
    3. 系统调用本函数查询和推荐门票方案
    4. 返回多个购票选项和直达付款界面的链接
    
    重要：destination 参数在此函数中是景点名称（"故宫"），不是城市名称（"北京"）
    """
    
    # 预订意图数据（用户选择故宫、指定人数和日期）
    booking_intent_dict = {
        "destination": "故宫博物院",  # 景点名称，不是城市名称
        "visit_date": date(2024, 4, 1),
        "adult_count": 2,
        "student_count": 0,
        "child_count": 1,
        "elderly_count": 0,
        "confidence": 0.95
    }
    
    # 模拟景点查询API响应 - step2a
    mock_attraction_response = {
        "attractions": [
            {
                "id": "forbidden_city_001",
                "name": "故宫博物院",
                "location": "北京市东城区景山前街4号",
                "rating": 4.8,
                "opening_hours": "08:30-17:00"
            }
        ]
    }
    
    # 模拟门票查询API响应 - step2b/c
    # 系统应该返回多个购票方案（个票 vs 套票）
    mock_ticket_response = {
        "ticket_options": [
            {
                "description": "推荐方案1：个票组合（最灵活）",
                "total_price": 150,
                "purchase_url": "https://ticketing.example.com/checkout?order=123&direct_pay=true",
                "tickets": [
                    {"type": "成人票", "count": 2, "price_per_ticket": 60},
                    {"type": "儿童票", "count": 1, "price_per_ticket": 30}
                ]
            },
            {
                "description": "推荐方案2：家庭套票（最实惠）",
                "total_price": 140,
                "purchase_url": "https://ticketing.example.com/checkout?order=124&direct_pay=true",
                "tickets": [
                    {"type": "家庭套票(2成人+1儿童)", "count": 1, "price_per_ticket": 140}
                ]
            }
        ]
    }
    
    with patch("backend.app.utils.attraction_recommendation._search_attraction") as mock_search, \
         patch("backend.app.utils.attraction_recommendation._get_optimal_tickets") as mock_tickets:
        
        mock_search.return_value = mock_attraction_response
        mock_tickets.return_value = mock_ticket_response
        
        # 执行预订 - 使用内部执行函数
        result = await _execute_book_attraction_ticket(
            destination="故宫博物院",
            visit_date=date(2024, 4, 1),
            adult_count=2,
            child_count=1
        )
        
        # 验证结果
        assert "故宫博物院" in result  # 景点名称
        assert "成人×2" in result      # 人数信息
        assert "儿童×1" in result      # 人数信息
        assert "推荐方案 1" in result  # 多个方案
        assert "推荐方案 2" in result  # 多个方案
        assert "¥150" in result        # 总价
        assert "¥140" in result        # 总价
        assert "direct_pay=true" in result  # 直达付款参数
        # 最关键：返回直达付款界面链接
        assert "直达付款界面" in result


@pytest.mark.asyncio
async def test_book_attraction_ticket_no_destination():
    """缺少景点名称参数的错误处理"""
    
    # 空景点名称
    # 即使没有景点名称，函数也不应该调用API
    with patch("backend.app.utils.attraction_recommendation._search_attraction") as mock_search:
        result = await _execute_book_attraction_ticket(
            destination="",
            visit_date=date(2024, 4, 1),
            adult_count=1
        )
        
        # 应该返回错误信息，而不是调用API
        assert "缺少必要参数" in result or "景点名称" in result
        mock_search.assert_not_called()


@pytest.mark.asyncio
async def test_book_attraction_ticket_not_found():
    """景点未找到的错误处理"""
    
    # 景点查询API返回空结果
    mock_attraction_response = {"attractions": []}
    
    with patch("backend.app.utils.attraction_recommendation._search_attraction") as mock_search, \
         patch("backend.app.utils.attraction_recommendation._get_optimal_tickets") as mock_tickets:
        
        mock_search.return_value = mock_attraction_response
        
        result = await _execute_book_attraction_ticket(
            destination="不存在的景点XYZ",
            visit_date=date(2024, 4, 1),
            adult_count=1
        )
        
        # 应该返回景点未找到的信息
        assert "未找到" in result or "抱歉" in result
        # 由于景点未找到，不应该调用门票查询API
        mock_tickets.assert_not_called()

@pytest.mark.asyncio
async def test_book_attraction_ticket_no_destination():
    """测试路径 8：缺少景区名称的情况"""
    
    booking_intent_dict = {"destination": ""}
    result = await book_attraction_ticket.ainvoke(booking_intent_dict)
    assert "缺少必要参数" in result or "destination" in result


@pytest.mark.asyncio
async def test_book_attraction_ticket_not_found():
    """测试路径 9：景区未找到的情况"""
    
    booking_intent_dict = {
        "destination": "不存在的景区",
        "visit_date": date(2024, 4, 1)
    }
    
    mock_response = {"attractions": []}
    
    with patch("backend.app.utils.attraction_recommendation._search_attraction") as mock_search:
        mock_search.return_value = mock_response
        result = await book_attraction_ticket.ainvoke(booking_intent_dict)
        assert "未找到景区信息" in result or "未找到" in result
