"""
LLM 集成模块 - Kimi 模型配置
"""

import logging
from typing import Optional
from langchain_core.language_model import BaseLLM
from langchain_community.chat_models import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class KimiLLM:
    """Kimi LLM 管理器"""
    
    _instance: Optional[BaseLLM] = None
    
    @classmethod
    def get_llm(cls) -> BaseLLM:
        """
        获取或创建 Kimi LLM 实例
        
        Kimi 兼容 OpenAI API 接口，所以使用 ChatOpenAI 初始化
        """
        if cls._instance is None:
            if not settings.KIMI_API_KEY:
                raise ValueError(
                    "Kimi API Key 未配置。请在 .env 文件中设置 KIMI_API_KEY"
                )
            
            logger.info(f"正在初始化 Kimi LLM (模型: {settings.KIMI_MODEL})")
            
            cls._instance = ChatOpenAI(
                model_name=settings.KIMI_MODEL,
                openai_api_key=settings.KIMI_API_KEY,
                openai_api_base=settings.KIMI_BASE_URL,
                temperature=0.7,  # 平衡创意和准确性
                max_tokens=2000,
                request_timeout=60,
                verbose=settings.LANGCHAIN_VERBOSE
            )
            
            logger.info("✓ Kimi LLM 初始化成功")
        
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置 LLM 实例 (测试用)"""
        cls._instance = None


def get_llm() -> BaseLLM:
    """方便函数 - 获取 LLM 实例"""
    return KimiLLM.get_llm()
