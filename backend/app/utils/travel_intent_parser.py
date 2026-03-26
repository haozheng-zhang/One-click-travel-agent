# from anyio import create_event
from langchain.tools import InjectedToolCallId, tool
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Annotated, Optional,Any
from collections import OrderedDict
from datetime import date, datetime,time
from backend.app.core import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langgraph.types import Command

class Destination(BaseModel):
    """游玩某地的行程规划"""
    location:str=Field(default_factory=str, description="目的地，如“天津”")
    attractions:OrderedDict[str,datetime]=Field(default_factory=OrderedDict, description="按时间先后顺序记录旅游景点及到访时间")
    stay:str=Field(default_factory=str, description="用户居住于此的方式，如“某某酒店”，没有则填写“无”")
    hotel_needed: bool = Field(default=False, description="是否需要预订酒店")
    ticket_needed: list[str] = Field(default_factory=list, description="需要预定景点门票的景点列表")
    transportation:str=Field(default_factory=str,description="详细叙述在此地的交通方式规划，包括离开此地的交通方式")
class TravelIntentReport(BaseModel):
    """出行意图结构化数据模型"""
    
    # 基础信息
    #intent_type: str = Field(..., description="意图类型: travel_planning, ticket_booking, hotel_booking等")
    confidence: float = Field(default=0, description="意图识别置信度 (0-1)")
    
    # 地址信息
    origin: str = Field(default_factory=str, description="出发地")
    destinations: list[Destination]=Field(default_factory=list, description="按时间先后顺序记录旅游地点")
    # 时间信息
    departure_date: Optional[date] = Field(default=None, description="出发日期")
    departure_time: Optional[time] = Field(default=None, description="出发时间")
    return_date: Optional[date] = Field(default=None, description="返回日期")
    return_time: Optional[time] = Field(default=None, description="返回时间")
    duration_days: Optional[int] = Field(default=None, description="行程天数")
    
    # 出行人员
    person_count: Optional[int] = Field(default=None, description="出行人数")
    # 出行方式
    transport_mode: str = Field(default_factory=str, description="离开出发地的交通方式，如“高铁”，“自驾”")
    # 偏好和预算
    budget_per_person: Optional[float] = Field(default=None, description="人均预算")
    
    # 额外需求
    extra_needs_and_preferences: set[str]|None = Field(default_factory=set, description="多条额外的需求和偏好")
    
    # 补全标记
    auto_filled_fields: set[str] = Field(default_factory=set, description="自动逻辑推断补全的字段列表")

class TravelIntentInput(BaseModel):
    query: str = Field(description="用户最近一条关于旅行意图的原始自然语言描述")

@tool("get_TravelIntentReport", args_schema=TravelIntentInput)
async def get_TravelIntentReport(
    query: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
    """意图解析专家：将用户的自然语言行程需求转化为结构化的旅行意图报告。
    请在收到用户输入且分析出需要更新旅行意图报告时的第一时刻单独调用此工具，因为旅行意图报告可能作为其他工具的输入。
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业的旅游意图分析专家。"
            f"今天的日期是：{date.today()} (星期{date.today().strftime('%A')})。"
            "请将用户提到的相对时间（如“明天”“下周三”）翻译成绝对时间。"
            "然后从已翻译的用户输入中提取出行意图，填入TravelIntentReport的字段并返回。"
            "如果用户没提到某项信息，请保持该字段为默认值。"
            "如果你对某个字段是猜测的，请将其记录在 auto_filled_fields 中。"
        )),
        ("human", "{input}")
    ])
    
    # 2. 绑定结构化输出
    chain = prompt | get_llm().with_structured_output(TravelIntentReport)
    
    # 3. 执行
    report = await chain.ainvoke({"input": query})
    content = "旅行意图报告已成功增量更新。"
    if report is None:
        content = "旅行意图报告未更新新内容。"
        report = TravelIntentReport()

    # 2. 核心：返回 Command 对象
    return Command(
        update={
            # 更新 State 中的 travel_intent 字段，触发你定义的 merge 逻辑
            "travel_intent": report,
            # 必须包含 ToolMessage，否则 Meta-Agent 会因为收不到工具结果而报错
            "messages": [
                ToolMessage(
                    content=content, 
                    tool_call_id=tool_call_id
                )
            ]
        }
    )