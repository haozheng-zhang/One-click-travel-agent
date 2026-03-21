"""
LLM 集成模块 - 模型配置
"""

import logging
from typing import Optional, Any
#from langchain_community.chat_models import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from backend.app.utils import get_current_time
from langchain.chat_models import init_chat_model
from backend.app.config import settings

logger = logging.getLogger(__name__)


class LLMManager:
    """LLM 管理器"""
    
    _llm_instance: Optional[BaseChatModel] = None
    _agent_instance: Optional[Any] = None
    system_prompt:str|None = None
    @classmethod
    def _setup_prompt_template(cls):
        """设置提示词模板"""
        
        cls.system_prompt = """你是一个专业的出行助手 AI。你的任务是理解用户的出行需求，并提取关键信息。

## 你的职责：
1. 识别用户的意图（如：规划行程、预订车票、查询酒店等）
2. 从用户输入中精准提取参数（出发地、目的地、时间、人数、预算等）
3. 自动补全缺失的参数（使用默认值或逻辑推断）
4. 返回结构化的 JSON 格式数据

## 重要规则：
- 日期格式必须是 YYYY-MM-DD
- 时间格式必须是 HH:MM（24小时制）
- 如果用户没有明确指定出发日期，且是合理的请求，则假设是最近的相关日期
- 置信度范围 0-1，如果用户输入不够清晰则置信度较低，但仍应尽力提取信息
- auto_filled_fields 应该包含所有被自动补全或推断的字段名列表

## 输出格式：
必须返回有效的 JSON，包含以下字段：
{{
  "intent_type": "string",
  "confidence": float,
  "origin": "string or null",
  "destination": "string or null",
  "departure_date": "YYYY-MM-DD or null",
  "departure_time": "HH:MM or null",
  "return_date": "YYYY-MM-DD or null",
  "return_time": "HH:MM or null",
  "duration_days": int or null,
  "person_count": int,
  "travelers": [],
  "transport_mode": "string or null",
  "budget_per_person": float or null,
  "preferences": {{}},
  "hotel_needed": bool,
  "ticket_needed": bool,
  "auto_filled_fields": []
}}
"""
        return cls.system_prompt


    @classmethod
    def get_llm(cls) -> BaseChatModel:
        """
        获取或创建 LLM 实例
        """
        if cls._llm_instance is None:
            if not settings.LLM_API_KEY:
                raise ValueError(
                    "LLM API Key 未配置。请在 .env 文件中设置 LLM_API_KEY"
                )
            
            logger.info(f"正在初始化 LLM (模型: {settings.LLM_MODEL_NAME})")
            
            try:
                # 使用 LangChain 0.2.0+ 的 init_chat_model
                cls._llm_instance = init_chat_model(
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
        
        
        return cls._llm_instance
    @classmethod
    def get_agent(cls) -> Any:
        if cls._agent_instance is not None:
            return cls._agent_instance
        model=cls.get_llm()
        assert model is not None, "Model must be initialized before creating agent"
        cls._agent_instance = create_agent(
            model=model,
            system_prompt=cls._setup_prompt_template(),
        )
        return cls._agent_instance

    @classmethod
    def reset_instance(cls):
        """重置 LLM 实例 (测试用)"""
        cls._agent_instance = None
        cls._llm_instance = None
        cls.system_prompt = None
    
def get_llm() -> BaseChatModel:
    """方便函数 - 获取 agent 实例"""
    return LLMManager.get_llm()

def get_agent() -> Any:
    """方便函数 - 获取 agent 实例"""
    return LLMManager.get_agent()
