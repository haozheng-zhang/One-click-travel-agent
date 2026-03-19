"""
自然语言理解 (NLU) 模块
负责：
1. 意图识别 (识别用户想要进行的操作)
2. 参数提取 (从用户输入中提取关键信息)
3. 默认值补全 (自动补充缺失的参数)
4. 结构化数据转换 (将非结构化文本转换为结构化数据)
"""

import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.llm import get_llm
from app.config import settings

logger = logging.getLogger(__name__)


# ==================== 数据模型 ====================

class TravelIntent(BaseModel):
    """出行意图结构化数据模型"""
    
    # 基础信息
    intent_type: str = Field(..., description="意图类型: travel_planning, ticket_booking, hotel_booking等")
    confidence: float = Field(..., description="意图识别置信度 (0-1)")
    
    # 地址信息
    origin: Optional[str] = Field(None, description="出发地")
    destination: Optional[str] = Field(None, description="目的地")
    
    # 时间信息
    departure_date: Optional[str] = Field(None, description="出发日期 (格式: YYYY-MM-DD)")
    departure_time: Optional[str] = Field(None, description="出发时间 (格式: HH:MM)")
    return_date: Optional[str] = Field(None, description="返回日期 (格式: YYYY-MM-DD)")
    return_time: Optional[str] = Field(None, description="返回时间 (格式: HH:MM)")
    duration_days: Optional[int] = Field(None, description="行程天数")
    
    # 出行人员
    person_count: int = Field(default=2, description="出行人数")
    travelers: List[str] = Field(default_factory=list, description="出行人信息列表")
    
    # 出行方式
    transport_mode: Optional[str] = Field(None, description="交通方式: flight, train, car, bus等")
    
    # 偏好和预算
    budget_per_person: Optional[float] = Field(None, description="人均预算")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="其他偏好设置")
    
    # 额外需求
    hotel_needed: bool = Field(default=True, description="是否需要预订酒店")
    ticket_needed: bool = Field(default=True, description="是否需要景区门票")
    
    # 原文本
    raw_input: str = Field(..., description="用户原始输入")
    
    # 补全标记
    auto_filled_fields: List[str] = Field(default_factory=list, description="自动补全的字段列表")


class NLUResult(BaseModel):
    """NLU 处理结果"""
    success: bool
    travel_intent: Optional[TravelIntent] = None
    error_message: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list, description="后续建议")


# ==================== NLU 处理器 ====================

class TravelNLUProcessor:
    """出行需求 NLU 处理器"""
    
    def __init__(self):
        self.llm = get_llm()
        self._setup_prompt_template()
    
    def _setup_prompt_template(self):
        """设置提示词模板"""
        
        self.system_prompt = """你是一个专业的出行助手 AI。你的任务是理解用户的出行需求，并提取关键信息。

## 你的职责：
1. 识别用户的意图（如：规划行程、预订车票、查询酒店等）
2. 从用户输入中精准提取参数（出发地、目的地、时间、人数、预算等）
3. 自动补全缺失的参数（使用默认值或逻辑推断）
4. 返回结构化的 JSON 格式数据

## 重要规则：
- 日期格式必须是 YYYY-MM-DD
- 时间格式必须是 HH:MM（24小时制）
- 人数没有特别说明时，默认为 {default_person_count} 人
- 出发时间没有特别说明时，默认为 {default_departure_time}
- 返回时间没有特别说明时，默认为 {default_return_time}
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
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "用户输入: {user_input}")
        ])
    
    async def process(self, user_input: str) -> NLUResult:
        """
        处理用户输入，提取出行意图和参数
        
        Args:
            user_input: 用户的自然语言输入
            
        Returns:
            NLUResult: 处理结果，包含解析后的意图和错误信息
        """
        try:
            logger.info(f"处理用户输入: {user_input}")
            
            # 准备提示词
            formatted_prompt = self.prompt.format(
                user_input=user_input,
                default_person_count=settings.DEFAULT_PERSON_COUNT,
                default_departure_time=settings.DEFAULT_DEPARTURE_TIME,
                default_return_time=settings.DEFAULT_RETURN_TIME
            )
            
            # 调用 LLM
            logger.debug("调用 Deepseek LLM 进行意图解析...")
            response = await self.llm.ainvoke(formatted_prompt)
            
            # 解析响应
            response_text = response.content.strip()
            logger.debug(f"LLM 响应: {response_text}")
            
            # 尝试从响应中提取 JSON
            travel_intent = self._parse_llm_response(response_text, user_input)
            
            if travel_intent:
                logger.info(f"✓ 意图识别成功 (置信度: {travel_intent.confidence})")
                return NLUResult(
                    success=True,
                    travel_intent=travel_intent,
                    suggestions=self._generate_suggestions(travel_intent)
                )
            else:
                logger.warning("无法解析 LLM 响应")
                return NLUResult(
                    success=False,
                    error_message="无法理解用户需求，请提供更清晰的描述"
                )
        
        except Exception as e:
            logger.error(f"NLU 处理异常: {str(e)}")
            return NLUResult(
                success=False,
                error_message=f"处理出错: {str(e)}"
            )
    
    def _parse_llm_response(self, response_text: str, user_input: str) -> Optional[TravelIntent]:
        """
        从 LLM 响应中解析 JSON 数据
        
        Args:
            response_text: LLM 返回的文本
            user_input: 原始用户输入
            
        Returns:
            TravelIntent 对象，或 None（如果解析失败）
        """
        try:
            # 移除可能的 markdown 代码块标记
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            response_text = response_text.strip()
            
            # 解析 JSON
            data = json.loads(response_text)
            
            # 创建 TravelIntent 对象
            intent = TravelIntent(
                **data,
                raw_input=user_input
            )
            
            # 后处理：验证和补全日期
            self._post_process_dates(intent)
            
            return intent
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"创建 TravelIntent 失败: {str(e)}")
            return None
    
    def _post_process_dates(self, intent: TravelIntent):
        """后处理 - 验证和补全日期信息"""
        
        # 如果有出发日期但没有返回日期，计算返回日期
        if intent.departure_date and not intent.return_date:
            if intent.duration_days:
                dep_date = datetime.strptime(intent.departure_date, "%Y-%m-%d")
                return_date = dep_date + timedelta(days=intent.duration_days - 1)
                intent.return_date = return_date.strftime("%Y-%m-%d")
                intent.auto_filled_fields.append("return_date")
        
        # 如果有出发日期和返回日期但没有 duration_days，计算天数
        if intent.departure_date and intent.return_date and not intent.duration_days:
            dep_date = datetime.strptime(intent.departure_date, "%Y-%m-%d")
            ret_date = datetime.strptime(intent.return_date, "%Y-%m-%d")
            intent.duration_days = (ret_date - dep_date).days + 1
            intent.auto_filled_fields.append("duration_days")
    
    def _generate_suggestions(self, intent: TravelIntent) -> List[str]:
        """根据提取的意图生成后续建议"""
        suggestions = []
        
        # 检查缺失的关键字段
        if not intent.origin:
            suggestions.append("🔍 需要确认出发地")
        
        if not intent.destination:
            suggestions.append("🔍 需要确认目的地")
        
        if not intent.departure_date:
            suggestions.append("🔍 需要确认出发日期")
        
        if intent.confidence < 0.7:
            suggestions.append("⚠️  意图识别置信度较低，建议用户进一步说明")
        
        if intent.origin and intent.destination:
            suggestions.append("✓ 将查询天气、交通、酒店等信息")
        
        if not intent.budget_per_person:
            suggestions.append("💡 未指定预算，将使用通用推荐方案")
        
        return suggestions


# ==================== 便利函数 ====================

async def parse_travel_intent(user_input: str) -> NLUResult:
    """
    便利函数 - 解析用户出行意图
    
    Args:
        user_input: 用户的自然语言输入
        
    Returns:
        NLUResult: 包含解析结果的对象
        
    Usage:
        result = await parse_travel_intent("帮我规划3月20号从北京到云南大理的自驾游")
        if result.success:
            print(result.travel_intent.destination)
            print(result.travel_intent.auto_filled_fields)
    """
    processor = TravelNLUProcessor()
    return await processor.process(user_input)
