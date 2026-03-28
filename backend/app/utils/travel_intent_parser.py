# from anyio import create_event
import dspy
from langchain.tools import InjectedToolCallId, tool
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import date, time
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from dspy import ChainOfThought
from datetime import date

class Destination(BaseModel):
    """游玩某地的行程规划"""
    location:str=Field(default_factory=str, description="目的地，如“天津”")
    attractions:list[str]|None=Field(default=None, description="按到访时间顺序记录此地的旅游景点")
    stay:str|None=Field(default=None, description="用户居住于此的方式，如“某某酒店”，未知则留空")
    hotel_needed: bool = Field(default=False, description="是否需要预订酒店")
    ticket_needed: list[str]|None = Field(default=None, description="需要预定景点门票的景点列表")
    transportation:str|None=Field(default=None,description="详细叙述在此地的交通方式规划，包括离开此地的交通方式")
class TravelIntentReport(BaseModel):
    """出行意图结构化数据模型"""
    
    # 基础信息
    #intent_type: str = Field(..., description="意图类型: travel_planning, ticket_booking, hotel_booking等")
    confidence: float = Field(default=0, description="意图识别置信度 (0-1)")
    
    # 地址信息
    origin: str= Field(default_factory=str, description="出发地")
    destinations: list[Destination]=Field(default_factory=list, description="按时间先后顺序记录旅游地点")
    # 时间信息
    departure_date: date|None = Field(default=None, description="出发日期")
    departure_time: time|None = Field(default=None, description="出发时间")
    return_date: date|None = Field(default=None, description="返回日期")
    return_time: time|None = Field(default=None, description="返回时间")
    duration_days: int|None = Field(default=None, description="行程天数")
    
    # 出行人员
    person_count: int|None = Field(default=None, description="出行人数")
    # 出行方式
    transport_mode: str|None = Field(default=None, description="离开出发地的交通方式，如“高铁”，“自驾”")
    # 预算
    budget_per_person: int|None = Field(default=None, description="人均预算")
    
    # 额外需求
    extra_needs_and_preferences: set[str]|None = Field(default_factory=set, description="多条额外的需求和偏好")
    
    # 补全标记
    auto_filled_fields: set[str]|None = Field(default_factory=set, description="自动逻辑推断补全的字段列表")

class TravelIntentInput(BaseModel):
    query: str = Field(description="用户最近一条关于旅行意图的原始自然语言描述")

class TravelIntentExtraction(dspy.Signature):
    """
    你是一个专业的旅游意图分析专家。
    任务：将用户提供的自然语言（可能包含相对时间）解析为结构化的旅行意图报告。
    """
    current_date:date = dspy.InputField(desc="今天的日期，用于转换‘明天’、‘下周’等相对时间为绝对时间")
    current_weekday:int = dspy.InputField(desc="今天的星期，用于转换‘明天’、‘下周’等相对时间为绝对时间")
    query:str = dspy.InputField(desc="用户的原始输入文本")
    
    # 这里的 TravelIntentReport 是你定义的 Pydantic 类
    report: TravelIntentReport = dspy.OutputField(desc="生成的结构化意图报告")


class TravelParserModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # 使用 TypedPredictor 确保输出严格符合 Pydantic 定义
        # 建议使用 ChainOfThought 增加推理过程，提升日期转换的准确率
        self.predictor = ChainOfThought(TravelIntentExtraction)
    def forward(self,query,current_date=date.today(),current_weekday=date.today().strftime('%A')):
        return self.predictor(current_date=current_date, query=query,current_weekday=current_weekday)
    
@tool("get_TravelIntentReport", args_schema=TravelIntentInput)
async def get_TravelIntentReport(
    query: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
    """意图解析专家：将用户的自然语言行程需求转化为结构化的旅行意图报告。
    请在收到用户输入且分析出需要更新旅行意图报告时的第一时刻单独调用此工具，因为旅行意图报告可能作为其他工具的输入。
    """
    # 初始化
    parser = TravelParserModule()
    parser.load("training/result/retravel_parser.json")
    
    result = parser(query=query)
    content = "旅行意图报告已成功增量更新。"
    if result.report is None:
        content = "旅行意图报告未更新新内容。"
        result.report = TravelIntentReport()
    #return result.report
    return Command(
        update={
            # 更新 State 中的 travel_intent 字段，触发 merge 逻辑
            "travel_intent": result.report,
            # 必须包含 ToolMessage，否则 Meta-Agent 会因为收不到工具结果而报错
            "messages": [
                ToolMessage(
                    content=content, 
                    tool_call_id=tool_call_id
                )
            ]
        }
    )