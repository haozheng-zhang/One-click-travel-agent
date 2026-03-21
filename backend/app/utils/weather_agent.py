from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import date
from langchain.tools import tool
from langchain.agents.structured_output import ToolStrategy

from backend.app.core.llm import get_llm

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    date_being_searched:date = Field(description="the beginning date being searched")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: int = Field(
        default=0,
        description="number of following days of forecast after the beginning date"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, date_being_searched:date,units: str = "celsius", include_forecast: int = 0) -> str:
    """Get current weather and optional forecast."""
    temp = 22 if units == "celsius" else 72
    result = f"Current weather in {location}: {temp} degrees {units[0].upper()}"
    if include_forecast:
        result += f"\nNext {include_forecast} days: Sunny"
    return result

class WeatherDetail(BaseModel):
    """一天的天气详情数据模型"""
    location: str
    temperature: float
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    condition: str = Field(description="天气状况，如：晴、雨、阴")
    suggestion: str = Field(description="针对该天气的出行建议")

class WeatherReport(BaseModel):
    """最终交给用户的连续多天天气的结构化报告"""
    repos: Optional[List[WeatherDetail]] = None
    suggestion: str = Field(description="综合这几天的天气判断给出出行建议")

weather_agent = create_agent(
    model=get_llm(),
    tools=[get_weather],
    # 核心：定义最终输出必须符合 WeatherReport 格式
    response_format=ToolStrategy(WeatherReport), 
    system_prompt=(
        f"你是一个专业的天气助手。当前日期是 {date.today()}。" # 注入当前时间
        "1. 如果用户询问未来天气，请确保 location、date_being_searched、include_forecast 等参数正确。"
        "2. 调用 get_weather 获取数据。"
        "3. 最终通过调用工具生成 WeatherReport。"
    )
)