from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from datetime import date, timedelta
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain.agents.structured_output import ToolStrategy

from backend.app.core.llm import get_llm

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    beginning_date:date = Field(description="the beginning date being searched")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: int = Field(
        default=0,
        description="number of following days of forecast after the beginning date"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, beginning_date:date,units: str = "celsius", include_forecast: int = 0) -> str:
    """Get weather of several days."""
    temp = 22 if units == "celsius" else 72
    lines = [f"{beginning_date}: {location}, {temp} degrees {units}, Sunny"]
    
    for i in range(1, include_forecast + 1):
        future_date = beginning_date + timedelta(days=i)
        # 模拟明天的气温稍微变一下，让 AI 好识别
        lines.append(f"{future_date}: {location}, {temp + 1} degrees {units}, Cloudy")
    
    return "\n".join(lines)

class WeatherDetail(BaseModel):
    """一天的天气详情数据模型"""
    location: str
    temperature: float
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    condition: str = Field(description="天气状况，如：晴、雨、阴")
    suggestion: float = Field(description="在该天气的出行指数，取值范围0~1，越适合出行则数值越大")

class WeatherReport(BaseModel):
    """最终交给用户的连续多天天气的结构化报告"""
    repos: Optional[List[WeatherDetail]] = None
    suggestion: str = Field(description="综合这几天的天气判断给出出行建议")

model=get_llm()
weather_agent = create_agent(
    model,
    tools=[get_weather],
    system_prompt=(
        f"你是一个严谨的天气数据采集员。当前日期是 {date.today()}。"
        "你的唯一任务是：根据用户需求，调用 get_weather 工具获取准确的原始数据。"
        "如果用户要求获取未来的或多天的数据，请确保location、beginning_date、include_forecast等参数准确"
        "获取数据后，请直接回复：'已获取到原始数据：[数据内容]'"
    )
)

async def get_weather_service(user_query : str) -> Any:
    agent_step = await weather_agent.ainvoke({
        "messages": [{"role": "user", "content": user_query}]
    })
    # 提取 agent 最终输出内容
    #final_content = agent_step["messages"][-1].content  # str
    tool_outputs = []
    for m in agent_step["messages"]:
        if isinstance(m, ToolMessage):
            content = m.content
            # 如果是字符串直接用，如果是列表则转为字符串（比如 JSON）
            content_str = content if isinstance(content, str) else str(content)
            tool_outputs.append(content_str)

    raw_data = "\n".join(tool_outputs)

    report = await model.with_structured_output(WeatherReport).ainvoke(raw_data)
    print(report)
    return report

