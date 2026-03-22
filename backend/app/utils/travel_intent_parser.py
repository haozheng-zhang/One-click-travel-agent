# from anyio import create_event
from pydantic import BaseModel, Field
from typing import Optional,List,Any
from datetime import date,time
from backend.app.core.llm import get_llm
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