from typing import Annotated, Literal, Optional, TypedDict
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from backend.app.core import get_llm
from datetime import date
from backend.app.utils.travel_intent_parser import TravelIntentReport, get_TravelIntentReport
from backend.app.utils.weather_parser import search_weather_and_parse, WeatherReport
from backend.app.utils.web_searcher import web_search
from backend.app.utils.attraction_recommendation import recommend_attractions, get_ticket_info, book_attraction_ticket
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage, AnyMessage

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

def get_current_turn_tools(messages):
    """工具函数：获取当前回合（最后一条 HumanMessage 之后）所有调用过的工具名"""
    # 1. 逆序查找最后一个 HumanMessage 的索引
    last_human_index = -1
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            last_human_index = i
            break
    
    if last_human_index == -1:
        return set()

    # 2. 切片获取本轮所有消息
    current_turn_messages = messages[last_human_index + 1:]
    
    # 3. 提取所有 ToolMessage 的名称
    called_tools = {
        m.name for m in current_turn_messages 
        if isinstance(m, ToolMessage)
    }
    return called_tools

class NextActions(BaseModel):
    travel_intent: bool = Field(default=False,description="是否需要更新出行规划")
    web_search: bool = Field(default=False,description="是否需要通用联网搜索")
    general:bool = Field(default=False,description="无需调用其他工具时将此变量设为True")

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    travel_intent: Annotated[Optional[TravelIntentReport], merge_travel_intent]
    weather:Optional[WeatherReport]
    next_action:NextActions


tools = [get_TravelIntentReport, web_search, search_weather_and_parse, recommend_attractions, get_ticket_info, book_attraction_ticket]

model = get_llm().bind_tools(tools)

async def model_call(state:State) :
    weather_info = "尚未获取天气信息。"
    intent_info = "尚未分析出明确行程意图。"
    if state.get("weather"):
        weather_info = f"{state['weather']}"
    if state.get("travel_intent"):
        intent_info = f"{state['travel_intent']}"

    called_tools = get_current_turn_tools(state["messages"])
    
    weather_hint = ""
    if "search_weather_and_parse" in called_tools:
        weather_hint = "【提示】你在本轮操作中已经更新了天气数据，你无需再次查询天气，但是最终给用户的回复中应该提及这个天气数据（并给出出行建议）。"
    system_prompt = SystemMessage(
        "你是一个专业的旅游助手。请根据当前的系统状态和聊天记录回答用户。"
        f"\n今天的日期是：{date.today()} (星期{date.today().strftime('%A')})。"
        "请先将用户输入中的相对时间（如明天、下周三）翻译为绝对时间，调用工具时也请只输入绝对时间（如：2026.4.1 上海天气预报）以获得更精准的输出。"
        f"\n\n--- 系统当前感知到的状态 ---"
        f"\n[当前行程意图快照]: {intent_info}"
        f"\n[实时天气数据]: {weather_info}"
        f"\n---------------------------"
        
        "\n请注意：如果你感知到的数据（如天气数据）与行程意图不匹配，可以调用工具更新；" \
        "\n如果行程意图中有信息缺失，可以追问。" \
        f"{weather_hint}"
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

# async def run_agent(user_input: str):
#     inputs:State = {
#         "messages": [HumanMessage(content=user_input)],
#         "travel_intent": None, 
#         "weather": None,
#         "next_action": NextActions()
#     }
    
#     config = {"configurable": {"thread_id": "test_user_1"}}
    
#     # 使用 astream 处理异步节点
#     async for event in graph.astream(inputs, stream_mode="values"):
#         if "messages" in event:
#             last_msg = event["messages"][-1]
#             # 打印消息
#             last_msg.pretty_print()
            
#             # 💡 华为实习面试加分点：展示状态机的实时演进
#             if event.get("travel_intent"):
#                 print(f"核心状态更新 [TravelIntent]: {event['travel_intent'].destination} | {event['travel_intent'].start_date}")

# # 运行
# import asyncio
# if __name__ == "__main__":
#     asyncio.run(run_agent("我想去北京玩，大概下周三出发"))