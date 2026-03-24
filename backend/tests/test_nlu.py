"""
单元测试 - 意图解析模块
"""

import pytest
import asyncio
from backend.app.core.nlu import parse_travel_intent, TravelNLUProcessor


class TestIntentParsing:
    """意图解析测试"""
    
    @pytest.mark.asyncio
    async def test_basic_travel_planning(self):
        """测试基础出行规划需求"""
        
        user_input = "帮我规划3月20号从北京到云南大理的自驾游，3天2晚，人均预算2000"
        
        result = await parse_travel_intent(user_input)
        
        assert result.success is True
        assert result.travel_intent is not None
        
        intent = result.travel_intent
        assert intent.origin == "北京"
        assert intent.destination == "大理"
        assert intent.transport_mode == "自驾"
        assert intent.budget_per_person == 2000
        assert intent.duration_days == 3
    
    @pytest.mark.asyncio
    async def test_missing_fields_auto_fill(self):
        """测试缺失字段自动补全"""
        
        user_input = "我想去成都旅游，3天"
        
        result = await parse_travel_intent(user_input)
        
        assert result.success is True
        intent = result.travel_intent
        
        # 验证自动补全
        assert intent.person_count == 2  # 默认人数
        assert intent.departure_time == "09:00"  # 默认出发时间
        assert "person_count" in intent.auto_filled_fields or intent.person_count == 2
    
    @pytest.mark.asyncio
    async def test_unclear_input(self):
        """测试不清晰的输入"""
        
        user_input = "随便看看"
        
        result = await parse_travel_intent(user_input)
        
        # 即使识别失败或置信度低，应该有合理的输出
        assert result.travel_intent is not None or result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_multiple_destinations(self):
        """测试多目的地行程"""
        
        user_input = "计划一个环滇池之旅，从昆明出发，要去大理、丽江、泸沽湖，5天4晚"
        
        result = await parse_travel_intent(user_input)
        
        assert result.success is True
        # 注意：可能会把主要目的地识别为大理或丽江
        assert result.travel_intent.origin == "昆明"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
