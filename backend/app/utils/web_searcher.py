import asyncio
from typing import Literal

from pydantic import BaseModel, Field
from backend.config import settings
from langchain.tools import tool
from tavily import TavilyClient

# 1. 定义工具的输入 Schema，这能帮助 LLM 更准确地构造参数
class SearchInput(BaseModel):
    query: str = Field(description="需要搜索的查询关键词或问题")
    search_depth: Literal['basic', 'advanced', 'fast', 'ultra-fast'] = Field(
        default="basic", 
        description="搜索深度：'basic' 速度快，'advanced' 内容更深（消耗更多额度）"
    )
    
async def _execute_web_search(query: str, search_depth:Literal['basic', 'advanced', 'fast', 'ultra-fast'] = "basic") -> str:
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        return "错误：未检测到 TAVILY_API_KEY，请检查服务器配置。"

    try:
        # 3. 初始化客户端
        client = TavilyClient(api_key=api_key)
        
        # 4. 在线程池中执行同步的 SDK 调用，防止阻塞异步事件循环
        # 注意：如果 SDK 支持异步，可直接 await client.search_async
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: client.search(
                query=query, 
                search_depth=search_depth, 
                max_results=5,
            )
        )

        # 5. 数据清洗：只给 LLM 最核心的信息，节省 Token 并降低干扰
        if not response.get("results"):
            return f"搜索 '{query}' 没有找到相关结果。"

        # 格式化搜索结果
        formatted_results = []
        for i, res in enumerate(response["results"], 1):
            content = res.get("content", "")
            url = res.get("url", "")
            formatted_results.append(f"[{i}] 来源: {url}\n内容: {content}")

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"搜索过程中发生错误: {str(e)}"

@tool("web_search", args_schema=SearchInput)
async def web_search(query: str, search_depth: Literal['basic', 'advanced', 'fast', 'ultra-fast'] = "basic") -> str:
    """
    一个强大的互联网搜索引擎。
    当你需要获取最新的新闻、实时天气、景点动态、价格信息或验证事实等信息时，请调用此工具。
    """
    return await _execute_web_search(query,search_depth)
    