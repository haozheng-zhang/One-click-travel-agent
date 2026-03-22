from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from datetime import date, timedelta
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

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
    """某一天的天气详情数据模型"""
    location: str
    the_date:date = Field(description="the weather on which being searched")
    temperature: float
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
model=get_llm()
weather_agent = create_agent(
    model,
    tools=[get_weather],
    system_prompt=(
        f"你是一个拥有‘地球卫星权限’的严谨天气数据分析员。当前日期是 {date.today()}。\n\n"
        "核心任务：\n"
        "1. **信息校验**：在调用工具前，必须校验地点和时间。\n"
        "   - 地点限制：仅限地球。如果用户提到火星、月球等外星地点，请幽默地拒绝。\n"
        "   - 时间限制：如果查询日期超过未来15天，请委婉拒绝并告知用户预测模型在远期可能失效。\n"
        "2. **工具调用**：校验通过后，计算 beginning_date 和 include_forecast 并调用 get_weather。\n"
        "3. **回复规范**：\n"
        "   - 若调用了工具：请回复‘已获取到原始数据：[内容]’。\n"
        "   - 若未调用工具（校验未通过）：请直接以交互性的口吻回复用户，解释原因。"
    )
)

async def get_weather_service(user_query: str) -> WeatherReport:
    agent_step = await weather_agent.ainvoke({
        "messages": [HumanMessage(content=user_query)]
    })
    messages = agent_step.get("messages", [])
    if not messages:
        raise ValueError("Weather agent returned no messages.")
        
    raw_data = messages[-1].content
    
    # 3. 结构化解析
    # 这里建议添加一些 prompt 引导，防止解析失败
    structured_llm = model.with_structured_output(WeatherReport)
    report = await structured_llm.ainvoke(
        f"请将以下天气描述转化为结构化报告。如果包含多天，请完整列出：\n{raw_data}"
    )
    
    # 4. 修正断言与防御性处理
    if report is None:
        print("⚠️ 警告：LLM 无法解析天气数据，返回空报告")
        return WeatherReport(message="LLM 无法解析天气数据，返回空报告")
    
    assert isinstance(report, WeatherReport), f"预期 WeatherReport, 实际得到 {type(report)}"
    return report

