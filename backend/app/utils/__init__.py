"""
工具函数模块
"""
from langchain.tools import tool
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@tool("clock")
def get_current_time() -> datetime:
    """Get the current time.
    """
    return datetime.now()

def mask_sensitive_data(data: str) -> str:
    """脱敏敏感数据（用于日志）"""
    if len(data) <= 4:
        return "***"
    return data[:2] + "***" + data[-2:]
