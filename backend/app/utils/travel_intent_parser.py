from anyio import create_event
from pydantic import BaseModel, Field
from typing import Optional,List,Dict,Any
from datetime import date,time
from backend.app.core.llm import get_llm
from langchain.agents.structured_output import ProviderStrategy



class TravelIntentReport(BaseModel):
    """出行意图结构化数据模型"""
    
    # 基础信息
    intent_type: str = Field(..., description="意图类型: travel_planning, ticket_booking, hotel_booking等")
    confidence: float = Field(..., description="意图识别置信度 (0-1)")
    
    # 地址信息
    origin: Optional[str] = Field(None, description="出发地")
    destination: Optional[str] = Field(None, description="目的地")
    
    # 时间信息
    departure_date: Optional[date] = Field(None, description="出发日期")
    departure_time: Optional[time] = Field(None, description="出发时间")
    return_date: Optional[date] = Field(None, description="返回日期")
    return_time: Optional[time] = Field(None, description="返回时间")
    duration_days: Optional[int] = Field(None, description="行程天数")
    
    # 出行人员
    person_count: int = Field(default=1, description="出行人数")
    travelers: List[str] = Field(default_factory=list, description="出行人信息列表")
    
    # 出行方式
    transport_mode: Optional[str] = Field(None, description="交通方式: flight, train, car, bus等")
    
    # 偏好和预算
    budget_per_person: Optional[float] = Field(None, description="人均预算")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="其他偏好设置")
    
    # 额外需求
    hotel_needed: bool = Field(default=False, description="是否需要预订酒店")
    ticket_needed: bool = Field(default=False, description="是否需要景区门票")
    
    # 原文本
    raw_input: str = Field(..., description="用户原始输入")
    
    # 补全标记
    auto_filled_fields: List[str] = Field(default_factory=list, description="自动补全的字段列表")


travel_intent_parser = create_event(
    model=get_llm(),
    # 核心：定义最终输出必须符合 WeatherReport 格式
    response_format=ProviderStrategy(TravelIntentReport), 
    system_prompt=(
        f"你是一个专业的天气助手。当前日期是 {date.today()}。" # 注入当前时间
        "1. 如果用户询问未来天气，请确保 location、date_being_searched、include_forecast 等参数正确。"
        "2. 调用 get_weather 获取数据。"
        "3. 最终生成 WeatherReport。"
    )
)