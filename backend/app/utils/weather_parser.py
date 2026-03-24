from datetime import date
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

async def parse_weather_to_state(raw_text: str) -> WeatherReport:

    # 1. 内部调用一个轻量级、高逻辑性的模型（如 gpt-4o-mini）进行结构化
    parser_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个气象数据提取器。请从提供的文本中提取天气信息并返回 WeatherReport 结构。"),
        ("human", "{text}")
    ])
    
    # 使用 with_structured_output 确保输出符合 WeatherReport Schema
    chain = parser_prompt | get_llm().with_structured_output(WeatherReport)
    report = await chain.ainvoke({"text": raw_text})
    if report == None: return WeatherReport()
    assert isinstance(report,WeatherReport)
    return report
    
@tool("weather_search")
async def search_weather_and_parse(query: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """
    从搜索引擎中获取天气并结构化为WeatherReport。
    同时自动更新系统的 weather 状态字段。
    有查询天气的需求时优先调用此工具。
    """
    raw_res = await _execute_web_search(query)
    # 内部直接解析，不经过 Meta-Agent 的第二轮思考
    report = await parse_weather_to_state(raw_res) 
    return Command(
        update={
            "weather": report,
            "messages": [ToolMessage(content="天气报告已成功结构化并存入系统。", tool_call_id=tool_call_id)]
        }
    )