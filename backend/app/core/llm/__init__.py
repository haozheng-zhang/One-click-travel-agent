"""
LLM 集成模块 - 模型配置
"""

import logging
from typing import Optional, Union
#from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from backend.app.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM 管理器"""
    
    _instance: Optional[BaseChatModel] = None
    
    @classmethod
    def get_llm(cls) -> BaseChatModel|None:
        """
        获取或创建 LLM 实例
        """
        if cls._instance is None:
            if not settings.LLM_API_KEY:
                raise ValueError(
                    "LLM API Key 未配置。请在 .env 文件中设置 LLM_API_KEY"
                )
            
            logger.info(f"正在初始化 LLM (模型: {settings.LLM_MODEL_NAME})")
            
            try:
                # 使用 LangChain 0.2.0+ 的 init_chat_model
                cls._instance = init_chat_model(
                    model=settings.LLM_MODEL_NAME,
                    api_key=settings.LLM_API_KEY,
                    base_url=settings.LLM_BASE_URL,
                    temperature=0.7,      # 平衡创意和准确性
                    max_tokens=2000,
                    request_timeout=60
                )
                
                logger.info("✓ LLM 初始化成功")
                
            except Exception as e:
                logger.error(f"LLM 初始化失败: {str(e)}")
                raise ValueError(f"LLM 初始化失败: {str(e)}")
        
        
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """重置 LLM 实例 (测试用)"""
        cls._instance = None


def get_llm() -> BaseChatModel|None:
    """方便函数 - 获取 LLM 实例"""
    return LLMManager.get_llm()
