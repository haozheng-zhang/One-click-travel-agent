import pytest
from langchain_core.messages import HumanMessage
from backend.app.core.graph import State, graph, NextActions  # 确保路径正确

# 告诉 pytest 这是一个异步测试
@pytest.mark.asyncio
async def test_travel_agent_stream():
    """测试智能体的一键出行流转逻辑"""
    
    # 1. 准备初始状态
    inputs:State = {
        "messages": [HumanMessage(content="我想下周去北京玩，帮我看看天气，推荐景点预定门票")],
        "travel_intent": None,
        "weather": None,
        "next_action": NextActions()
    }
    
    # 2. 配置会话 ID (用于 MemorySaver)
    config = {"configurable": {"thread_id": "pytest_session_001"}}
    
    print("\n" + "="*20 + " 智能体思考开始 " + "="*20)
    
    # 3. 执行并步进打印
    # stream_mode="values" 会让你看到每一步后 State 的完整快照
    async for event in graph.astream(inputs,stream_mode="values"):
        if "messages" in event and event["messages"]:
            node_output = event["messages"][-1]
            
            # 打印当前是谁在说话/执行
            sender = "🤖 AI" if node_output.type == "ai" else "🛠️ Tool"
            print(f"\n[{sender}]:")
            node_output.pretty_print()
            
            # 打印我们最关心的业务状态
            if event.get("travel_intent") and event["travel_intent"].destinations:
                print(f"👉 [当前意图]: {event['travel_intent'].destinations}")
    
    print("\n" + "="*20 + " 测试流程结束 " + "="*20)

    # 4. 简单的断言（可选）
    assert len(inputs["messages"]) > 0