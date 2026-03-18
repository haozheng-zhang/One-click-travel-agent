"""
工具函数模块
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime:
    """
    解析日期字符串
    
    支持格式:
    - YYYY-MM-DD
    - YYYY/MM/DD
    - MM-DD (当年)
    - M月D日 (当年)
    """
    # TODO: 实现日期解析逻辑
    pass


def calculate_days_between(date1: str, date2: str) -> int:
    """计算两个日期之间的天数"""
    # TODO: 实现日期间隔计算
    pass


def format_time(time_str: str) -> str:
    """格式化时间为 HH:MM 格式"""
    # TODO: 实现时间格式化
    pass


def get_default_time(which: str = "departure") -> str:
    """获取默认时间"""
    from app.config import settings
    
    if which == "departure":
        return settings.DEFAULT_DEPARTURE_TIME
    elif which == "return":
        return settings.DEFAULT_RETURN_TIME
    else:
        return "09:00"


def mask_sensitive_data(data: str) -> str:
    """脱敏敏感数据（用于日志）"""
    if len(data) <= 4:
        return "***"
    return data[:2] + "***" + data[-2:]
