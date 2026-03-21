"""
旅行规划 API 路由
负责处理用户的出行需求
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List

from backend.app.core.nlu import parse_travel_intent, TravelIntent, NLUResult
from backend.app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 请求/响应模型 ====================

class PlanningRequest(BaseModel):
    """行程规划请求"""
    user_input: str = Field(..., description="用户的自然语言输入")
    user_id: Optional[str] = Field(None, description="用户ID")
    context: Optional[dict] = Field(None, description="对话上下文")


class PlanningResponse(BaseModel):
    """行程规划响应"""
    success: bool
    message: str
    intent: Optional[dict] = None  # TravelIntent 的字典形式
    auto_filled_fields: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    next_step: str  # 下一步操作


# ==================== 路由端点 ====================

@router.post("/parse-intent", response_model=PlanningResponse)
async def parse_user_intent(request: PlanningRequest, background_tasks: BackgroundTasks):
    """
    **第一步：意图解析与核心需求提取**
    
    通过大语言模型，精准拆解用户需求的核心参数，自动补全默认规则。
    使用 LangChain + LLM 完成。
    
    ### 示例输入：
    ```
    "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"
    ```
    
    ### 预期输出：
    - 识别意图：travel_planning
    - 提取参数：出发地(北京) → 目的地(大理) | 时间(3/20-3/22) | 交通方式(自驾) | 预算(2000)
    - 补全默认：人数(默认2) | 出发时间(默认09:00) | 返回时间(默认17:00)
    
    Args:
        request: 包含用户输入的请求体
        background_tasks: 后台任务队列
        
    Returns:
        PlanningResponse: 包含解析结果、自动补全字段列表、建议和下一步操作
    """
    
    try:
        # 记录请求
        logger.info(f"[{request.user_id or 'anonymous'}] 接收行程规划请求: {request.user_input}")
        
        # 调用 NLU 处理器
        nlu_result: NLUResult = await parse_travel_intent(request.user_input)
        
        if not nlu_result.success:
            logger.warning(f"意图解析失败: {nlu_result.error_message}")
            return PlanningResponse(
                success=False,
                message=nlu_result.error_message or "无法理解用户需求",
                next_step="请提供更清晰的出行需求描述，例如：'从北京到上海，3月20号，2人'",
                suggestions=nlu_result.suggestions
            )
        
        # 解析成功
        intent: TravelIntent = nlu_result.travel_intent
        
        logger.info(f"✓ 意图解析成功 (置信度: {intent.confidence})")
        logger.info(f"  出发地: {intent.origin}, 目的地: {intent.destination}")
        logger.info(f"  出发日期: {intent.departure_date}, 交通方式: {intent.transport_mode}")
        logger.info(f"  自动补全字段: {', '.join(intent.auto_filled_fields)}")
        
        # 确定下一步
        next_step = _determine_next_step(intent)
        
        # 返回响应
        response = PlanningResponse(
            success=True,
            message=f"✓ 意图识别成功 (置信度: {intent.confidence:.0%})",
            intent=intent.model_dump(),
            auto_filled_fields=intent.auto_filled_fields,
            suggestions=nlu_result.suggestions,
            next_step=next_step
        )
        
        # 后台任务：记录意图日志
        background_tasks.add_task(_log_intent, request.user_id, intent)
        
        return response
    
    except Exception as e:
        logger.error(f"处理行程规划请求异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="处理请求时发生错误，请稍后重试"
        )


@router.get("/test-LLM")
async def test_LLM_connection():
    """
    测试 LLM API 连接
    用于验证 LLM API Key 和网络连接是否正常
    """
    try:
        from app.core.llm import get_llm
        
        logger.info("测试 LLM 连接...")
        
        # 获取 LLM 实例（会自动初始化）
        llm = get_llm()
        
        # 发送测试请求
        test_input = "你好，请简单确认你的名字和能力。"
        response = await llm.ainvoke(test_input)
        
        logger.info("✓ LLM 连接成功")
        
        return {
            "status": "success",
            "message": "✓ LLM API 连接正常",
            "model": settings.LLM_MODEL_NAME,
            "response_preview": response.content[:100] + "..."
        }
    
    except ValueError as e:
        logger.error(f"配置错误: {str(e)}")
        return {
            "status": "error",
            "message": f"配置错误: {str(e)}",
            "hint": "请检查 .env 文件中是否设置了 LLM_API_KEY"
        }
    except Exception as e:
        logger.error(f"LLM 连接失败: {str(e)}")
        return {
            "status": "error",
            "message": f"连接失败: {str(e)}",
            "hint": "请检查网络连接或 API Key 是否正确"
        }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "travel-planning",
        "LLM_configured": bool(settings.LLM_API_KEY)
    }


# ==================== 辅助函数 ====================

def _determine_next_step(intent: TravelIntent) -> str:
    """根据提取的意图确定下一步操作"""
    
    missing_fields = []
    
    if not intent.origin:
        missing_fields.append("出发地")
    if not intent.destination:
        missing_fields.append("目的地")
    if not intent.departure_date:
        missing_fields.append("出发日期")
    
    if missing_fields:
        return f"需要补充信息: {', '.join(missing_fields)}"
    
    if intent.confidence < 0.7:
        return "意图识别置信度较低，建议用户进一步说明需求"
    
    if intent.origin and intent.destination and intent.departure_date:
        return "进入第二步: 前置信息校验与多源数据查询"
    
    return "等待用户确认或进一步说明"


async def _log_intent(user_id: Optional[str], intent: TravelIntent):
    """记录用户的出行意图（后台任务）"""
    try:
        # TODO: 实现意图日志记录
        logger.debug(f"记录意图日志 [用户: {user_id or 'anonymous'}]")
    except Exception as e:
        logger.error(f"记录意图日志失败: {str(e)}")
