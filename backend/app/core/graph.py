from typing import Annotated, Literal, Optional, TypedDict
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from backend.app.core import get_llm
from datetime import date
from backend.app.utils.travel_intent_parser import TravelIntentReport, get_TravelIntentReport
from backend.app.utils.weather_parser import search_weather_and_parse,WeatherReport
from backend.app.utils.web_searcher import web_search
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage,ToolMessage,AnyMessage

def merge_travel_intent(old: Optional[TravelIntentReport], new: TravelIntentReport) -> TravelIntentReport:
    """增量合并意图报告：保留旧信息，覆盖/更新新发现的信息"""
    if not old: return new
    # 将旧数据转为字典
    updated_data = old.model_dump()
    # 提取新数据中非空的字段（LLM 本次发现的补全）
    new_data = new.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in new_data.items():
        if isinstance(value, set):
            # set去重合并
            updated_data[key] = (updated_data.get(key) or set()) | value
        elif isinstance(value, dict):
            # 字典去重合并
            old_val = updated_data.get(key) or {}
            old_val.update(value)
            updated_data[key] = old_val
        else:
            # 普通字段直接覆盖
            updated_data[key] = value
            
    return TravelIntentReport(**updated_data)

class NextActions(BaseModel):
    travel_intent: bool = Field(default=False,description="是否需要更新出行规划")
    web_search: bool = Field(default=False,description="是否需要通用联网搜索")
    general:bool = Field(default=False,description="无需调用其他工具时将此变量设为True")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    travel_intent: Annotated[Optional[TravelIntentReport], merge_travel_intent]
    weather:Optional[WeatherReport]
    next_action:NextActions

# class MessageClassifier(BaseModel):
#     """分析用户意图，决定更新什么业务模块"""
#     next_action: NextActions = Field(description="key: 智能体将作出的下一步（一个或多个）行为")


# async def classify_message(state: State):
#     last_message = state["messages"][-1]
#     classifier_llm = get_llm().with_structured_output(MessageClassifier)

#     system_prompt = SystemMessage(content=
#         f"""
#         你是一个拥有‘时间感知能力’的智能体决策专家。

#         你的任务：
#         1. 分析用户输入的意图（travel_intent, weather, general）。
#         2. 时间归一化：如果用户提到“明天”、“下周”、“后天”等相对时间，请根据今天的日期将其转换为 YYYY-MM-DD(星期几) 格式。
#         3. 在 next_action 的 value 中，输出包含绝对日期的指令。
        
#         示例：
#         - 输入：“明天我想去上海迪士尼”
#         - 输出：将next_action.call_search和next_action.
#         """
#                                   )
#     result = classifier_llm.invoke([
#         system_prompt,
#         last_message
#     ])
#     return {"next_action": result.next_action} # type: ignore

tools = [get_TravelIntentReport,web_search,search_weather_and_parse]

model = get_llm().bind_tools(tools)

async def model_call(state:State) :
    system_prompt = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your ability."
        f"今天的日期是：{date.today()} (星期{date.today().strftime('%A')})。"
    )
    response = await model.ainvoke([system_prompt] + state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("meta_agent", model_call)
graph_builder.set_entry_point("meta_agent")

def should_continue(state: State):
    last_msg = state["messages"][-1]
    # 如果模型没有发出工具调用指令，则结束
    assert isinstance(last_msg,AIMessage)
    if not last_msg.tool_calls:
        return "end"
    return "continue"
 
graph_builder.add_conditional_edges(
    "meta_agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools",tool_node)
graph_builder.add_edge("tools", "meta_agent")

graph = graph_builder.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# print_stream(graph.astream(inputs, stream_mode="values"))

async def run_agent(user_input: str):
    inputs:State = {
        "messages": [HumanMessage(content=user_input)],
        "travel_intent": None, 
        "weather": None,
        "next_action": NextActions()
    }
    
    config = {"configurable": {"thread_id": "test_user_1"}}
    
    # 使用 astream 处理异步节点
    async for event in graph.astream(inputs, stream_mode="values"):
        if "messages" in event:
            last_msg = event["messages"][-1]
            # 打印消息
            last_msg.pretty_print()
            
            # 💡 华为实习面试加分点：展示状态机的实时演进
            if event.get("travel_intent"):
                print(f"核心状态更新 [TravelIntent]: {event['travel_intent'].destination} | {event['travel_intent'].start_date}")

# 运行
import asyncio
if __name__ == "__main__":
    asyncio.run(run_agent("我想去北京玩，大概下周三出发"))