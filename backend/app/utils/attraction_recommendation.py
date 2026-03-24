import asyncio
from typing import Literal, Optional
from datetime import date

from pydantic import BaseModel, Field
from backend.config import settings
from langchain.tools import tool
from backend.app.utils.travel_intent_parser import AttractionTicketBookingIntent


# 1. 定义推荐景点工具的输入 Schema
class RecommendAttractionsInput(BaseModel):
    destination: str = Field(description="旅游目的地城市或地区名称（例如'北京'、'西安'）")
    travel_days: int = Field(description="旅游天数", ge=1, le=30)
    budget: Optional[str] = Field(default="中等", description="预算水平：'低', '中等', '高'")
    interests: Optional[str] = Field(default=None, description="兴趣爱好，如'文化', '自然', '美食'等")


# 2. 定义获取门票信息工具的输入 Schema
class GetTicketInput(BaseModel):
    attraction_id: str = Field(description="景点的唯一标识符")
    ticket_type: Optional[str] = Field(default="all", description="门票类型：'成人', '学生', '儿童', 'all'")
    visit_date: Optional[str] = Field(default=None, description="计划访问日期，格式: YYYY-MM-DD")


@tool("recommend_attractions", args_schema=RecommendAttractionsInput)
async def recommend_attractions(
    destination: str,
    travel_days: int,
    budget: str = "中等",
    interests: Optional[str] = None
) -> str:
    """
    workflow步骤1: 根据城市名称推荐优质景点
    
    使用场景：
    - 用户说："我想去北京" → 调用此函数 destination="北京"
    - 返回北京所有优质景点列表（故宫、长城、颐和园等）
    - 用户从列表中选择具体景点（如"故宫"）
    - 然后调用 book_attraction_ticket 进行门票预订
    """

    try:
        # 构造推荐请求
        recommendation_request = {
            "destination": destination,
            "travel_days": travel_days,
            "budget": budget,
            "interests": interests or "综合"
        }

        # 在线程池中执行 API 调用，防止阻塞异步事件循环
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _call_recommendation_api(recommendation_request)
        )

        # 数据验证和格式化
        if not response.get("attractions"):
            return f"抱歉，未找到关于 '{destination}' 的景点推荐。你可以尝试其他城市。"

        # 格式化推荐结果 - 便于用户选择
        formatted_recommendations = []
        for i, attraction in enumerate(response["attractions"], 1):
            name = attraction.get("name", "未知景点")
            attraction_id = attraction.get("id", "")
            location = attraction.get("location", "")
            rating = attraction.get("rating", 0)
            description = attraction.get("description", "")
            price = attraction.get("ticket_price", "价格待定")

            formatted_recommendations.append(
                f"[{i}] {name}(ID:{attraction_id})\n"
                f"   位置: {location}\n"
                f"   评分: {rating}★\n"
                f"   描述: {description}\n"
                f"   门票价格: ¥{price}"
            )

        return f"为您推荐的 '{destination}' 景点（请从上面选择一个景点名称，我帮你预订门票）：\n\n" + "\n\n".join(formatted_recommendations)

    except Exception as e:
        return f"推荐异常：{str(e)}"


@tool("get_ticket_info", args_schema=GetTicketInput)
async def get_ticket_info(
    attraction_id: str,
    ticket_type: str = "all",
    visit_date: Optional[str] = None
) -> str:
    """
    获取景点的门票信息并提供购买链接。
    根据景点 ID 和访问日期，获取可用的门票类型、价格和购买链接。
    帮助用户快速购票，支持多种门票类型（成人、学生、儿童等）。
    """

    if not attraction_id:
        return "错误：缺少必要参数 'attraction_id'（景点ID）"

    try:
        ticket_request = {
            "attraction_id": attraction_id,
            "ticket_type": ticket_type,
            "visit_date": visit_date
        }

        # 在线程池中执行 API 调用
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _call_ticket_api(ticket_request)
        )

        # 验证响应
        if not response.get("tickets"):
            return f"抱歉，景点ID '{attraction_id}' 暂无可购票。"

        # 格式化门票信息
        formatted_tickets = []
        for ticket in response["tickets"]:
            if not ticket.get("availability"):
                formatted_tickets.append(
                    f"❌ {ticket.get('description', '门票')}: 已售罄"
                )
            else:
                price = ticket.get("price", "价格待定")
                purchase_url = ticket.get("purchase_url", "#")
                description = ticket.get("description", "门票")

                formatted_tickets.append(
                    f"✅ {description}\n"
                    f"   价格: ¥{price}\n"
                    f"   购买链接: {purchase_url}"
                )

        return f"景点门票信息:\n\n" + "\n\n".join(formatted_tickets)

    except Exception as e:
        return f"获取门票信息异常：{str(e)}"


@tool("book_attraction_ticket", args_schema=AttractionTicketBookingIntent)
async def book_attraction_ticket(
    destination: str,
    visit_date: Optional[date] = None,
    adult_count: int = 0,
    student_count: int = 0,
    child_count: int = 0,
    elderly_count: int = 0,
    attraction_id: Optional[str] = None,
    max_price_per_ticket: Optional[float] = None,
    prefer_combined_ticket: bool = False,
    has_special_needs: bool = False,
    special_needs_description: Optional[str] = None,
    **kwargs
) -> str:
    """
    【核心工作流函数】景区门票预订 - 从景点选择直达付款界面
    
    重要：destination 参数在此函数中是景点名称（如"故宫"），不是城市名称
    
    工作流程说明：
    1. 用户输入："我想去北京" 
       → 调用 recommend_attractions(destination="北京")  # 城市名称
       → 返回景点列表：[故宫, 长城, 颐和园, ...]
    
    2. 用户选择："我要去故宫，3个成人、1个儿童" 
       → 调用本函数 book_attraction_ticket(destination="故宫", adult_count=3, child_count=1)  # 景点名称
       → 本函数自动执行：
          a) 查询景点详情（_search_attraction）
          b) 查询最优门票方案（_get_optimal_tickets）
          c) 返回多种购票选项和直达付款界面的链接
    
    3. 最终结果：用户看到购票方案，点击"直达付款界面"即可进入支付流程
    """
    
    try:
        # 验证必填项
        if not destination:
            return "错误：缺少必要参数 'destination'（景点名称）。请从推荐列表中选择一个景点。"

        # 防守式编程：如果没有人数信息，至少有1个成人
        if adult_count + student_count + child_count + elderly_count == 0:
            adult_count = 1

        # 步骤A: 查询景点详情信息
        attraction_query_request = {
            "destination": destination,  # 景点名称，不是城市名称
            "attraction_id": attraction_id
        }
        
        loop = asyncio.get_event_loop()
        attraction_response = await loop.run_in_executor(
            None,
            lambda: _search_attraction(attraction_query_request)
        )

        if not attraction_response.get("attractions"):
            return f"抱歉，未找到景点 '{destination}' 的信息。请确认景点名称是否正确。"

        attraction = attraction_response["attractions"][0]
        attraction_id_result = attraction.get("id") or attraction_id
        attraction_name = attraction.get("name", destination)

        # 步骤B: 根据人员分类和日期查询最优门票方案
        ticket_query_request = {
            "attraction_id": attraction_id_result,
            "visit_date": visit_date.isoformat() if visit_date else None,
            "adult_count": adult_count,
            "student_count": student_count,
            "child_count": child_count,
            "elderly_count": elderly_count,
            "prefer_combined_ticket": prefer_combined_ticket,
            "max_price": max_price_per_ticket,
            "special_needs": special_needs_description if has_special_needs else None
        }

        # 步骤C: 调用门票API获取可用方案
        ticket_response = await loop.run_in_executor(
            None,
            lambda: _get_optimal_tickets(ticket_query_request)
        )

        if not ticket_response.get("ticket_options"):
            return f"抱歉，在您指定的日期和条件下，'{attraction_name}' 暂无可用门票。"

        # 步骤D: 格式化返回结果，包含直达付款界面链接
        formatted_options = [
            f"\n{'='*50}",
            f"景点：{attraction_name}",
            f"访问日期：{visit_date or '未指定'}",
            f"购票人数：成人×{adult_count} 学生×{student_count} 儿童×{child_count} 老年×{elderly_count}",
            f"{'='*50}\n"
        ]

        for i, option in enumerate(ticket_response["ticket_options"], 1):
            total_price = option.get("total_price", "待定")
            description = option.get("description", "")
            purchase_url = option.get("purchase_url", "#")
            
            formatted_options.append(
                f"\n【推荐方案 {i}】{description}"
            )
            
            # 显示每种票的明细
            for ticket_detail in option.get("tickets", []):
                count = ticket_detail.get("count", 1)
                price_per = ticket_detail.get("price_per_ticket", 0)
                subtotal = count * price_per
                formatted_options.append(
                    f"  • {ticket_detail.get('type', '门票')} × {count} @ ¥{price_per}/张 = ¥{subtotal}"
                )
            
            # 关键：提供直达付款界面的链接
            formatted_options.append(
                f"\n💳 总价：¥{total_price}"
            )
            formatted_options.append(
                f"🔗 【直达付款界面】{purchase_url}"
            )

        return "\n".join(formatted_options)

    except Exception as e:
        return f"景点门票预订异常：{str(e)}"


# ============= 辅助函数 - 调用真实API的入口 =============

def _call_recommendation_api(request: dict) -> dict:
    """
    【workflow step 1】根据城市名称调用推荐API，获取该城市的景点列表
    
    此函数应该调用：
    - web_search.py 中的搜索功能查询"北京景点推荐"等关键词，获取实时数据
    - 或者本地推荐服务API（基于评分、热度、用户口碑等）
    
    返回指定城市中的所有景点列表，供用户选择。
    
    API 响应格式：
    {
        "attractions": [
            {
                "id": "forbidden_city_001",
                "name": "故宫博物院",
                "location": "北京市东城区景山前街4号",
                "rating": 4.8,
                "description": "中国最大的古代建筑群，世界文化遗产",
                "ticket_price": "60"
            },
            ...
        ]
    }
    """
    # TODO: 集成 web_search.py 进行在线搜索
    # 例如：search_web(f"{request['destination']} 景点推荐")
    # 然后解析搜索结果，转换为标准格式返回
    
    return {"attractions": []}


def _call_ticket_api(request: dict) -> dict:
    """
    调用真实的门票购买 API
    在实际应用中，这里应该调用真实的门票服务
    """
    return {"tickets": []}


# 5. 辅助函数：根据景点名称查询景点信息
def _search_attraction(request: dict) -> dict:
    """
    【workflow step 2a】根据景点名称查询景点详情信息
    
    重要区别：
    - _call_recommendation_api 接收"北京"（城市名称），返回该城市所有景点列表
    - _search_attraction 接收"故宫"（景点名称），返回该景点的详细信息
    
    此函数应该集成：
    1. 景点数据库查询（本地数据库）
    2. 支持模糊匹配（用户可能说"故宫"也可能说"故宫博物院"）
    3. 返回景点的详细信息供后续门票查询使用
    
    API参数：
    - destination: 景点名称（如"故宫"、"长城"）
    - attraction_id: 景点ID（如果已知，可直接查询）
    
    返回格式：
    {
        "attractions": [
            {
                "id": "forbidden_city_001",
                "name": "故宫博物院",
                "location": "北京市东城区景山前街4号",
                "rating": 4.8,
                "description": "中国最大的古代建筑群，世界文化遗产",
                "opening_hours": "08:30-17:00",
                "address": "北京市东城区景山廉价路4号",
                "phone": "010-6513-2255"
            }
        ]
    }
    """
    # TODO: 集成真实景点查询数据库或API
    return {"attractions": []}


# 6. 辅助函数：根据人员分类查询最优门票方案
def _get_optimal_tickets(request: dict) -> dict:
    """
    【workflow step 2b|c|d】根据人员分类和日期查询最优门票方案
    
    这是整个工作流的最后环节，直接关系到"直达付款界面"的实现。
    
    此函数应该：
    1. 查询指定日期的门票库存和价格
    2. 根据人员分类自动匹配票种（成人、学生、儿童、老年等不同折扣）
    3. 比较个票和套票的价格，推荐多个成本最优方案
    4. 基于 max_price 过滤方案（用户只看在预算范围内的）
    5. 基于 special_needs 推荐特殊票种（如无障碍票）
    6. 返回 purchase_url 应该能直接跳转到支付页面（支付宝/微信/银行卡）
    
    输入 request：
    - attraction_id: 景点ID（如"forbidden_city_001"）
    - visit_date: 访问日期 (YYYY-MM-DD)
    - adult_count: 成人数量（60元/张）
    - student_count: 学生数量（30元/张）
    - child_count: 儿童数量（15元/张）
    - elderly_count: 老年人数量（20元/张）
    - prefer_combined_ticket: 是否倾向于套票（家庭套票可能更便宜）
    - max_price: 单张票最高价格限制（例如100元）
    - special_needs: 特殊需求描述（例如"轮椅无障碍"）
    
    应返回多个方案供用户选择，每个方案包含直达付款界面的链接：
    {
        "ticket_options": [
            {
                "description": "推荐方案1：个票组合（最灵活）",
                "total_price": 165,
                "purchase_url": "https://ticketing.example.com/checkout?cart_id=123&direct_pay=true",
                "tickets": [
                    {"type": "成人票", "count": 2, "price_per_ticket": 60},
                    {"type": "儿童票", "count": 1, "price_per_ticket": 30}
                ]
            },
            {
                "description": "推荐方案2：家庭套票（最实惠）",
                "total_price": 150,
                "purchase_url": "https://ticketing.example.com/checkout?cart_id=124&direct_pay=true",
                "tickets": [{"type": "家庭套票(2成人+1儿童)", "count": 1, "price_per_ticket": 150}]
            }
        ]
    }
    
    集成关键点：
    - purchase_url 的设计必须包含 ?direct_pay=true 参数，使其能直接跳转支付界面
    - 支持多种支付方式（支付宝、微信、银行卡等）
    - 返回订单预览，用户确认后即可完成支付
    """
    # TODO: 集成真实的门票查询和优化API
    # 这个API应该对接景点的票务系统和电商平台
    return {"ticket_options": []}
