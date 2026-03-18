"""
配置模块 - 系统全局配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "一键出行智能体"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = ENVIRONMENT == "development"
    
    # LLM 配置 (Kimi)
    KIMI_API_KEY: Optional[str] = os.getenv("KIMI_API_KEY")
    KIMI_MODEL: str = "kimi-2.5"  # 或其他可用的 Kimi 模型
    KIMI_BASE_URL: str = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
    
    # LangChain 配置
    LANGCHAIN_VERBOSE: bool = ENVIRONMENT == "development"
    LANGCHAIN_DEBUG: bool = ENVIRONMENT == "development"
    
    # Redis 配置 (可选，用于缓存)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 业务规则配置
    DEFAULT_PERSON_COUNT: int = 2  # 默认出行人数
    DEFAULT_DEPARTURE_TIME: str = "09:00"  # 默认出发时间
    DEFAULT_RETURN_TIME: str = "17:00"  # 默认返回时间
    MAX_ITINERARY_DAYS: int = 30  # 最长行程天数
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建全局设置实例
settings = Settings()
