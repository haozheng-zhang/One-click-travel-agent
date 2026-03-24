"""
工具函数模块
"""
import logging

logger = logging.getLogger(__name__)

def mask_sensitive_data(data: str) -> str:
    """脱敏敏感数据（用于日志）"""
    if len(data) <= 4:
        return "***"
    return data[:2] + "***" + data[-2:]
