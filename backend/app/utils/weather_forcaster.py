from langchain.agents import create_agent
from pydantic import BaseModel, Field
from typing import Any, List, Literal, Optional
from datetime import date, timedelta
from langchain.tools import tool
from langchain_core.messages import ToolMessage

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
    days:int = Field(default=0,description="总天数")
    repos: Optional[List[WeatherDetail]] = None

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

async def get_weather_service(user_query : str) -> dict[str, Any]:
        agent_step = await weather_agent.ainvoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        # 提取 agent 最终输出内容
        #final_content = agent_step["messages"][-1].content  # str
        messages = agent_step["messages"]
        tool_outputs = []
        has_tool_call = False

        for m in messages:
            if isinstance(m, ToolMessage):
                has_tool_call = True
                content = m.content
                content_str = content if isinstance(content, str) else str(content)
                tool_outputs.append(content_str)

        # 3. 分支逻辑
        # 情况 A：Agent 调用了工具，说明校验通过，进入结构化解析阶段
        final_response = messages[-1].content
        if has_tool_call:
            raw_data = "\n".join(tool_outputs)
            # 调用 Parser 转化为 Pydantic 对象
            report = await model.with_structured_output(WeatherReport).ainvoke(
                f"根据以下观测事实生成天气报告，若有多天请全部列出：\n{raw_data}"
            )
            return {
                "status": "success",
                "data": report,
                "message": final_response,
                "source": "satellite_data"
            }

        # 情况 B：Agent 没调工具，说明它在进行“信息校验”或“火星拦截”
        else:
            # 拿最后一条 AIMessage 的内容，这通常是它的解释
            
            return {
                "status": "fail",
                "data": None,
                "message": final_response,
                "source": "agent_validation"
            }

