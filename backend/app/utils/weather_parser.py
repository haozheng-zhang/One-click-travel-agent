from datetime import date
import dspy
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated, Literal
from langchain_core.tools import InjectedToolCallId
from pydantic import BaseModel, Field
from backend.app.utils.web_searcher import _execute_web_search
from backend.app.core import get_llm

class WeatherDetail(BaseModel):
    """某一天的天气详情数据模型"""
    location: str
    the_date:date = Field(description="the weather on which being searched")
    max_temp: int = Field(description="the maximum temperature")
    min_temp: int = Field(description="the minimum temperature")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    condition: str = Field(description="天气状况，如：晴、雨、阴")
    suggestion: float = Field(description="在该天气的出行指数，取值范围0~1，越适合出行则数值越大")

class WeatherReport(BaseModel):
    """最终交给用户的连续多天天气的结构化报告"""
    status: bool =Field(default=False,description="是否查询成功")
    days:int = Field(default=0,description="总天数")
    repos: list[WeatherDetail] = Field(default_factory=list,description="(连续多天)天气的结构化报告")
    message:str= Field(default_factory=str,description="若查询失败则说明失败的原因，若成功则总结这份报告并给出出行建议")
    source:str= Field(default_factory=str,description="天气信息来源，若没有查询到天气则置为空字符串")

class WeatherParserSignature(dspy.Signature):
    """你是一个专业的数值气象学家。你的任务是从杂乱的网页搜索文本中提取出精确、结构化的天气报告。
    请忽略网页中的广告、无关链接和过期预报。"""
    query:str=dspy.InputField(desc="请求搜索的天气指令，包含地点和日期")
    raw_text = dspy.InputField(desc="搜索引擎返回的原始文本")
    current_date:date = dspy.InputField(desc="当前系统时间，用于校准‘明天’、‘下周’等相对时间")
    report:WeatherReport = dspy.OutputField(desc="结构化的天气报告对象")


class WeatherAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.parser = dspy.ChainOfThought(WeatherParserSignature)

    async def forward(self, query: str, current_date: date=date.today()):
        # 1. 执行副作用（I/O 搜索）
        # 注意：在 DSPy 的 forward 中，尽量保持代码同步或妥善处理异步
        raw_res = await _execute_web_search(query)
        
        # 3. 让 LLM 发挥它的“解析”才华
        prediction = self.parser(
            query=query,
            raw_text=raw_res, 
            current_date=current_date
        )
        return prediction
    
@tool("search_weather_and_parse")
async def search_weather_and_parse(query: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    从搜索引擎中获取天气并结构化为WeatherReport。
    同时自动更新系统的 weather 状态字段。
    有查询天气的需求时优先调用此工具。
    """
    parser = WeatherAgent()
    parser.load("training/result/weather_parser.json")
    result = parser(query=query)
    return Command(
        update={
            "weather": result.report,
            "messages": [ToolMessage(content="天气报告已成功结构化并存入系统。", tool_call_id=tool_call_id)]
        }
    )