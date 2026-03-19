"""
LLM 集成模块 - Deepseek 模型配置
"""

import logging
from typing import Optional, Any
from langchain_community.chat_models import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class DeepSeekLLM:
    """Deepseek LLM 管理器"""
    
    _instance: Optional[ChatOpenAI] = None
    
    @classmethod
    def get_llm(cls) -> ChatOpenAI:
        """
        获取或创建 Deepseek LLM 实例
        
        Deepseek 兼容 OpenAI API 接口，所以使用 ChatOpenAI 初始化
        """
        if cls._instance is None:
            if not settings.DEEPSEEK_API_KEY:
                raise ValueError(
                    "Deepseek API Key 未配置。请在 .env 文件中设置 DEEPSEEK_API_KEY"
                )
            
            logger.info(f"正在初始化 Deepseek LLM (模型: {settings.DEEPSEEK_MODEL})")
            
            cls._instance = ChatOpenAI(
                model=settings.DEEPSEEK_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.7,  # 平衡创意和准确性
                max_tokens=2000,
                request_timeout=60
            )
            
            logger.info("✓ Deepseek LLM 初始化成功")
        
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置 LLM 实例 (测试用)"""
        cls._instance = None


def get_llm() -> ChatOpenAI:
    """方便函数 - 获取 LLM 实例"""
    return DeepSeekLLM.get_llm()
