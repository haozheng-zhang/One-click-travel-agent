"""
配置模块 - 系统全局配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import ConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略额外的环境变量
    )
    
    # 基础配置
    APP_NAME: str = "一键出行智能体"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # ========== LLM 通用配置 ==========
    # 用户可自由设置这些通用字段
    LLM_API_KEY: Optional[str] = None        # 通用 API Key（优先使用）
    LLM_BASE_URL: Optional[str] = None       # 通用 API 地址（优先使用）
    LLM_MODEL_NAME: str = ""                 # 通用模型名称
    TAVILY_API_KEY: Optional[str] = None
    
    # MODEL_NAME: str = "LLM-chat"  # LLM 的聊天模型
    
    # LangChain 配置
    LANGCHAIN_VERBOSE: bool = True
    LANGCHAIN_DEBUG: bool = True
    
    # Redis 配置 (可选，用于缓存)
    REDIS_URL: Optional[str] = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"


# 创建全局设置实例
settings = Settings()
