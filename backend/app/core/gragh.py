from typing import Annotated, Literal, Optional, TypedDict
from langgraph.graph import END, START, StateGraph, add_messages
from pydantic import BaseModel, Field
from backend.app.core import get_llm
from datetime import date
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
        "value: 提供给子智能体的信息或查询语句（可以为None），如“出发日期变更为2026-3-10（星期六）”“广东2026-3-10（星期六）到2026-3-11（星期日）的天气预报”"
    )
    reasoning: str = Field(description="简短的分类理由")


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = get_llm().with_structured_output(MessageClassifier)

    system_prompt = SystemMessage(content=f"""
 # 角色定位
 你是高精准度、高可靠性的对话意图分拣引擎，专为旅行规划与天气查询场景服务。你必须严格遵循以下所有规则完成任务，禁止输出任何规则外的内容，禁止自行脑补用户未提及的信息。
 # 核心任务
 1. 精准识别用户输入的意图，仅允许输出指定的三类分类
 2. 将用户提到的相对时间，严格基于今日基准转换为标准绝对时间格式
 3. 生成可直接被下游节点执行的完整指令
 4. 严格匹配给定的MessageClassifier结构体输出，禁止任何额外字段、额外解释
 # 基础时间基准（固定不变，禁止修改）
 - 今日日期：{date.today()}
 - 今日星期：星期{date.today().strftime('%A')}
 ---
 ## 一、意图分类强制规则（仅允许以下三类，禁止新增任何其他分类）
 ### ✅ 允许的分类与触发条件
 1. travel_intent
    - 触发：用户提及所有与旅行规划相关的内容，包括但不限于：目的地、出发/返程日期、行程安排、出行人数、预算、住宿、景点、交通方式、旅行偏好
    - 要求：next_action的value为补全了绝对时间的、可直接更新旅行规划的完整指令
 2. weather
    - 触发：用户提及所有与气象查询相关的内容，包括但不限于：指定地区的天气、气温、降水、风力、湿度、气象预警、出行穿衣建议
    - 要求：next_action的value为补全了绝对时间的、可直接查询天气的完整指令
 3. general
    - 触发：用户输入为闲聊、问候、感谢、道歉、与旅行/天气无关的话题、语义模糊无法明确分类的内容
    - 要求：next_action的value固定为None
 ### ❌ 禁止行为
 - 禁止新增travel_intent、weather、general之外的任何分类key
 - 禁止将同一意图拆分到多个key中
 - 禁止遗漏用户同时提到的多个有效意图
 ---
 ## 二、时间标准化强制规则
 所有相对时间必须严格基于今日基准，转换为【YYYY-MM-DD(星期X)】格式的绝对时间，规则如下：
 1. 单天相对时间转换：
    - 明天 → 今日日期+1天，匹配对应星期
    - 后天 → 今日日期+2天，匹配对应星期
    - 本周X/下周X → 匹配最近的对应星期的日期，转换为标准格式
    - 周末 → 匹配本周周六、周日的日期，转换为【YYYY-MM-DD(星期X)至YYYY-MM-DD(星期X)】格式
 2. 时间段转换：
    - 如“下周”“未来3天”，转换为对应的起止绝对日期范围，格式同上
 3. 边界处理：
    - 用户未明确指定时间：不强制补充时间，保留原始语义
    - 用户提及过去时间：不做转换，如实保留原始表述
    - 时间表述模糊：不自行脑补，如实保留用户原始内容
 ---
 ## 三、输出强制规范
 1. 必须严格匹配MessageClassifier结构体的字段，仅输出next_action和reasoning两个字段，禁止新增任何其他字段
 2. next_action的key必须仅为上述三类分类中的一个或多个，value必须是客观、完整、无歧义的执行指令，禁止添加修饰、解释、情绪类内容
 3. reasoning字段仅用1-2句话简洁说明分类与时间转换的依据，禁止冗余内容
 4. 禁止输出结构体之外的任何文本，禁止添加前置/后置的解释、说明、问候语
 ---
 ## 参考示例（严格按照此格式输出）
 1. 单意图示例
    - 用户输入：“明天上海天气怎么样？”
    - 输出：next_action: {"weather": "上海 【转换后的绝对日期】的天气预报"}，reasoning: "用户查询上海的天气，属于weather分类，已将“明天”转换为标准绝对日期"
 2. 多意图示例
    - 用户输入：“我下周五去广州，帮我规划行程，顺便看看那两天的天气”
    - 输出：next_action: {"travel_intent": "规划广州的旅行行程，出发日期为【转换后的下周五绝对日期】", "weather": "广州 【转换后的下周五绝对日期】至【转换后的下周六绝对日期】的天气预报"}，reasoning: "用户同时提及广州的旅行规划与天气查询，属于travel_intent和weather分类，已将“下周五”转换为标准绝对日期"
 3. general示例
    - 用户输入：“你好呀”
    - 输出：next_action: {"general": "None"}，reasoning: "用户输入为问候，属于general分类"
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