# from anyio import create_event
from pydantic import BaseModel, Field
from typing import Optional,List,Any
from datetime import date,time
from backend.app.core import get_llm
from langchain_core.prompts import ChatPromptTemplate



class TravelIntentReport(BaseModel):
    """出行意图结构化数据模型"""
    
    # 基础信息
    #intent_type: str = Field(..., description="意图类型: travel_planning, ticket_booking, hotel_booking等")
    confidence: float = Field(default=0, description="意图识别置信度 (0-1)")
    
    # 地址信息
    origin: str = Field(default_factory=str, description="出发地")
    destination: str = Field(default_factory=str, description="目的地")
    
    # 时间信息
    departure_date: Optional[date] = Field(default=None, description="出发日期")
    departure_time: Optional[time] = Field(default=None, description="出发时间")
    return_date: Optional[date] = Field(default=None, description="返回日期")
    return_time: Optional[time] = Field(default=None, description="返回时间")
    duration_days: Optional[int] = Field(default=None, description="行程天数")
    
    # 出行人员
    person_count: Optional[int] = Field(default=None, description="出行人数")
    #travelers: [str] = Field(default_factory=list, description="出行人信息列表")
    
    # 出行方式
    transport_mode: str = Field(default_factory=str, description="交通方式: flight, train, car, bus等")
    
    # 偏好和预算
    budget_per_person: Optional[float] = Field(default=None, description="人均预算")
    
    # 额外需求
    hotel_needed: bool = Field(default=False, description="是否需要预订酒店")
    ticket_needed: bool = Field(default=False, description="是否需要景区门票")
    extra_needs_and_preferences: set[str]|None = Field(default_factory=set, description="多条额外的需求和偏好")
    
    # 补全标记
    auto_filled_fields: set[str] = Field(default_factory=set, description="自动逻辑推断补全的字段列表")


class AttractionTicketBookingIntent(BaseModel):
    """景区门票预订意图 - 结构化数据模型"""
    
    # 核心信息 - 用于调用景区查询和门票预订API
    destination: str = Field(default="", description="景区/目的地名称")
    attraction_id: Optional[str] = Field(default=None, description="景区ID（如果系统已知）")
    
    # 时间信息
    visit_date: Optional[date] = Field(default=None, description="计划访问日期")
    visit_time: Optional[time] = Field(default=None, description="计划访问时间")
    
    # 门票相关
    ticket_type: Optional[str] = Field(default=None, description="门票类型: 成人, 学生, 儿童, 老人等")
    quantity: Optional[int] = Field(default=None, description="购票数量")
    
    # 人员信息 - 用于门票分类
    adult_count: int = Field(default=0, description="成人数量")
    student_count: int = Field(default=0, description="学生数量")
    child_count: int = Field(default=0, description="儿童（6-12岁）数量")
    elderly_count: int = Field(default=0, description="老年人数量")
    
    # 预算和偏好
    max_price_per_ticket: Optional[float] = Field(default=None, description="单张票最高接受价格")
    has_special_needs: bool = Field(default=False, description="是否有特殊需求（无障碍等）")
    special_needs_description: Optional[str] = Field(default=None, description="特殊需求描述")
    
    # 购票信息
    prefer_combined_ticket: bool = Field(default=False, description="是否倾向于购买套票")
    need_transportation: bool = Field(default=False, description="是否需要景区内交通服务")
    
    # 额外信息
    visiting_with_group: bool = Field(default=False, description="是否是团体预订")
    group_size: Optional[int] = Field(default=None, description="团体人数")
    extra_preferences: Optional[str] = Field(default=None, description="其他偏好或要求")
    
    # 置信度和补全信息
    confidence: float = Field(default=0.8, description="意图识别置信度 (0-1)")
    auto_filled_fields: List[str] = Field(default_factory=list, description="自动逻辑推断补全的字段列表")


async def get_TravelIntentReport(user_query: str) -> dict[str, Any] | BaseModel:
    # 1. 构造 Prompt，注入当前日期
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业的旅游意图分析专家。"
            f"今天是 {date.today()}。请从用户输入中提取出行意图，并只能返回TravelIntentReport实例。"
            "如果用户没提到某项信息，请保持该字段为 None。"
            "如果你对某个字段是猜测的，请将其记录在 auto_filled_fields 中。"
        )),
        ("human", "{input}")
    ])
    
    # 2. 绑定结构化输出
    chain = prompt | get_llm().with_structured_output(TravelIntentReport)
    
    # 3. 执行
    report = await chain.ainvoke({"input": user_query})
    if report is None:
        # 返回一个带有原始输入的默认实例
        return TravelIntentReport()
    return report