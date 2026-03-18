"""
测试初始化
"""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """为 async 测试提供事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
