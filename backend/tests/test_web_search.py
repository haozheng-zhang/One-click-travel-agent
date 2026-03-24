import pytest
from unittest.mock import patch, MagicMock
from backend.app.utils.web_searcher import web_search

@pytest.mark.asyncio
async def test_web_search_success():
    """测试路径 1：成功获取结果并格式化"""
    
    # 1. 构造模拟的 Tavily 响应数据
    mock_response = {
        "results": [
            {"url": "https://test1.com", "content": "这是第一个测试结果的内容"},
            {"url": "https://test2.com", "content": "这是第二个测试结果的内容"}
        ]
    }

    # 2. 使用 patch 拦截 TavilyClient 的 search 方法
    # 注意：我们需要 patch 掉工具内部实例化的那个类
    with patch("backend.app.utils.web_search.TavilyClient") as MockClient:
        # 配置模拟实例的行为
        instance = MockClient.return_value
        instance.search.return_value = mock_response

        # 3. 执行工具函数
        query = "测试查询"
        result = await web_search.ainvoke({"query":query, "search_depth":"basic"})
        # 4. 验证结果格式
        assert "[1] 来源: https://test1.com" in result
        assert "内容: 这是第一个测试结果的内容" in result
        assert "[2] 来源: https://test2.com" in result
        assert result.count("来源:") == 2  # 应该有两个结果

@pytest.mark.asyncio
async def test_web_search_no_results():
    """测试路径 2：没有搜索结果的情况"""
    
    mock_response = {"results": []}

    with patch("backend.app.utils.web_search.TavilyClient") as MockClient:
        MockClient.return_value.search.return_value = mock_response
        result = await web_search.ainvoke({"query":"不存在的东西"})
        assert "没有找到相关结果" in result

@pytest.mark.asyncio
async def test_web_search_api_error():
    """测试路径 3：API 调用发生异常的情况"""
    
    with patch("backend.app.utils.web_search.TavilyClient") as MockClient:
        # 模拟 search 方法抛出异常
        MockClient.return_value.search.side_effect = Exception("API Key 过期")
        result = await web_search.ainvoke({"query":"报错测试"})
        assert "搜索过程中发生错误: API Key 过期" in result

@pytest.mark.asyncio
async def test_web_search_missing_config():
    """测试路径 4：配置缺失的情况"""
    
    # 模拟 settings.TAVILY_API_KEY 为空
    with patch("backend.app.utils.web_search.settings") as mock_settings:
        mock_settings.TAVILY_API_KEY = None
        result = await web_search.ainvoke({"query":"配置测试"})
        assert "未检测到 TAVILY_API_KEY" in result