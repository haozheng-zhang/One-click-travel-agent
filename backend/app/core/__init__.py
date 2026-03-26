"""
LLM 配置
"""

import logging
from typing import Optional, Any
#from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from backend.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM 管理器"""
    
    _llm_instance: Optional[BaseChatModel] = None
    _agent_instance: Optional[Any] = None


    @classmethod
    def get_llm(cls, temperature: float|None = None, **kwargs) -> BaseChatModel:
        """
        获取或创建 LLM 实例
        """
        is_custom = temperature is not None or len(kwargs) > 0
        if not settings.LLM_API_KEY:
            raise ValueError(
                "LLM API Key 未配置。请在 .env 文件中设置 LLM_API_KEY"
            )
        if cls._llm_instance and not is_custom:
            return cls._llm_instance
            
        logger.info(f"正在初始化 LLM (模型: {settings.LLM_MODEL_NAME})")
            
        try:
            # 使用 LangChain 0.2.0+ 的 init_chat_model
            cls._llm_instance = init_chat_model(
                model=settings.LLM_MODEL_NAME,
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                temperature=temperature if temperature is not None else getattr(settings, 'LLM_TEMPERATURE', 0.5),
                max_tokens=2000,
                request_timeout=60
            )
            
            logger.info("✓ LLM 初始化成功")
            
        except Exception as e:
            logger.error(f"LLM 初始化失败: {str(e)}")
            raise ValueError(f"LLM 初始化失败: {str(e)}")
        
        
        return cls._llm_instance

    @classmethod
    def reset_instance(cls):
        """重置 LLM 实例 (测试用)"""
        cls._agent_instance = None
        cls._llm_instance = None
        cls.system_prompt = None
    
def get_llm() -> BaseChatModel:
    """方便函数 - 获取 agent 实例"""
    return LLMManager.get_llm()

