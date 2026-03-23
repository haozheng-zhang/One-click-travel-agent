from typing import Annotated, Literal, Optional, TypedDict
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import BaseModel, Field
from backend.app.core import get_llm
from backend.app.utils.travel_intent_parser import TravelIntentReport, get_TravelIntentReport
from backend.app.utils.weather_forecaster import WeatherReport, get_weather_service
from langchain_core.messages import SystemMessage, HumanMessage

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


class State(TypedDict):
    messages: Annotated[list, add_messages]
    travel_intent: Annotated[Optional[TravelIntentReport], merge_travel_intent]
    weather:Optional[WeatherReport]
    next_action:dict[str,str|None]

class MessageClassifier(BaseModel):
    """分析用户意图，决定更新什么业务模块"""
    next_action: dict[Literal["travel_intent", "weather", "general"],str] = Field(
        ...,
        description="key: 智能体将作出的下一步（一个或多个）行为，包括：'travel_intent' (更新出行规划), 'weather' (更新天气查询), 'general' (闲聊或无法识别的话题)" \
        "value: 提供给子智能体的信息或查询语句（可以为None），如“出发日期变更为下周五”“查询某时间（如明天、下周、3月10号）某地点的天气”"
    )
    reasoning: str = Field(description="简短的分类理由")


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = get_llm().with_structured_output(MessageClassifier)

    system_prompt = SystemMessage(content="""你是一个意图分拣专家。请分析用户的输入并分类：
        - 'travel_intent': 从用户的信息推断出应当更新出行规划
        - 'weather': 从用户的信息推断出应当更新天气查询
        - 'general': 闲聊或无法识别的话题。
        """)
    result = classifier_llm.invoke([
        system_prompt,
        HumanMessage(content=last_message.content)
    ])
    return {"next_action": result.next_action} # type: ignore



def router(state: State) -> list[str]:
    """
    根据 next_action 字典中的所有 Key，决定去往哪些节点。
    如果返回多个字符串，LangGraph 会并行执行。
    """
    actions = state.get("next_action", {})
    if not actions or "general" in actions:
        return [END] # 或去往 chat 节点
    
    # 返回所有存在的业务 Key，如 ["travel_intent", "weather"]
    return list(actions.keys())


async def travel_intent_node(state: State):
    """旅游意图处理节点"""
    user_query = state["next_action"]["travel_intent"]
    assert user_query is not None
    report = await get_TravelIntentReport(user_query)
    return {"travel_intent": report}

async def weather_node(state: State):
    """天气处理节点"""
    user_query = state["next_action"]["weather"]
    assert user_query is not None
    report = await get_weather_service(user_query)
    return {"weather": report}

graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("travel_intent", travel_intent_node)
graph_builder.add_node("weather", weather_node)

graph_builder.add_edge(START, "classifier")

graph_builder.add_conditional_edges(
    "classifier",
    router,
    {
        "travel_intent": "travel_intent",
        "weather": "weather",
        "END": END
    }
)

graph_builder.add_edge("travel_intent", END)
graph_builder.add_edge("weather", END)

graph = graph_builder.compile()