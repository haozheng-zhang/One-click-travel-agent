from typing import Annotated, List, Literal, Optional, TypedDict, Union,Dict
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import BaseModel, Field
from backend.app.core.llm import get_llm
from backend.app.utils.travel_intent_parser import TravelIntentReport, get_TravelIntentReport
from backend.app.utils.weather_forcaster import WeatherReport, get_weather_service
from langchain_core.messages import SystemMessage, HumanMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]
    travel_intent: Annotated[Optional[TravelIntentReport], merge_travel_intent]
    weather:Optional[WeatherReport]
    next_action:Dict[str,str]

class MessageClassifier(BaseModel):
    """分析用户意图，决定更新什么业务模块"""
    next_action: Dict[Literal["travel_intent", "weather", "general"],str] = Field(
        ...,
        description="key: 智能体将作出的下一步（一个或多个）行为，包括：'travel_intent' (更新出行规划), 'weather' (更新天气查询), 'general' (闲聊或无法识别的话题)" \
        "value: 提供给子智能体的查询或信息语句，如“出发日期变更为下周五”“查询明天上海的天气”"
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
    return {"message_type": result.next_action}

def router(state: State) -> Union[str, List[str]]:
    """
    根据 state 中的 message_type 决定下一个节点
    """
    target = state.get("message_type", "general")

    if isinstance(target, list):
        destinations = [t for t in target if t in ["travel_intent", "weather", "general"]]
        return destinations if destinations else "general"

    # 3. 逻辑 B：处理单意图情况
    if target == "travel_intent":
        return "travel_intent"   # 这里的字符串要对应下面 add_node 时的名字
    
    if target == "weather":
        return "weather"
    
    return "general"


async def travel_intent_node(state: State):
    """旅游意图处理节点"""
    user_query = state["next_action"]["travel_intent"]
    report = await get_TravelIntentReport(user_query)
    return {"travel_intent": report}

async def weather_node(state: State):
    """天气处理节点"""
    user_query = state["next_action"]["weather"]
    
    # 调用你写好的天气服务
    report = await get_weather_service(user_query)
    
    return {"weather": report}

graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("travel_intent", travel_intent_node)
graph_builder.add_node("weather", weather_node)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "classifier",
    lambda state: state["next_action"],
    {
        "travel_intent": "travel_intent",
        "weather": "weather",
        "general": END # 如果是闲聊，直接结束或去 chat 节点
    }
)

graph_builder.add_edge("travel_intent", END)
graph_builder.add_edge("weather", END)

graph = graph_builder.compile()