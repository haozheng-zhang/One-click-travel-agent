import pytest
from datetime import date
from rapidfuzz.fuzz import token_set_ratio, partial_ratio
# 假设你的类和函数在这些路径
from backend.app.utils.travel_intent_parser import TravelIntentReport, Destination
from training.optimizers.train_travel_intent import travel_intent_metric

# 模拟 DSPy 的 Example 对象
class MockExample:
    def __init__(self, **kwargs):
        # 模拟 DSPy 的属性访问方式
        self.report = TravelIntentReport(**kwargs)

# --- 用例 1：完全匹配 ---
def test_perfect_match():
    dest = Destination(location="北京", attractions=["故宫", "天安门"], hotel_needed=True)
    report = TravelIntentReport(
        origin="上海",
        departure_date=date(2026, 5, 1),
        destinations=[dest],
        person_count=2,
        budget_per_person=3000,
        extra_needs_and_preferences={"靠窗"},
        auto_filled_fields={"departure_date"}
    )
    
    gold = MockExample(**report.model_dump())
    pred = MockExample(**report.model_dump())
    
    score = travel_intent_metric(gold, pred)
    assert score == 1.0

# --- 用例 2：模糊匹配与容错 ---
def test_fuzzy_logic():
    gold_dest = Destination(location="西安", attractions=["兵马俑", "大雁塔"])
    gold_report = TravelIntentReport(
        origin="北京",
        departure_date=date(2026, 6, 1),
        destinations=[gold_dest],
        person_count=3,
        budget_per_person=2000
    )
    
    # 模拟模型的稍微偏差
    pred_dest = Destination(
        location="西安市", # 模糊匹配
        attractions=["秦始皇兵马俑", "大雁塔景区"], # 模糊 F1
        hotel_needed=False
    )
    pred_report = TravelIntentReport(
        origin="北京市",
        departure_date=date(2026, 6, 1),
        destinations=[pred_dest],
        person_count=3,
        budget_per_person=2010# 2% 误差内
    )
    
    gold = MockExample(**gold_report.model_dump())
    pred = MockExample(**pred_report.model_dump())
    
    score = travel_intent_metric(gold, pred)
    # 分数不应该是 0，也不应该是 1
    assert 0.7 < score < 1.0

# --- 用例 3：严重幻觉惩罚 ---
def test_hallucination_penalty():
    gold_dest = Destination(location="南京")
    gold_report = TravelIntentReport(destinations=[gold_dest], person_count=1, budget_per_person=100)
    
    # 模型胡凑了一个额外的目的地
    pred_report = TravelIntentReport(
        destinations=[Destination(location="南京"), Destination(location="幻觉城市")],
        person_count=1,
        budget_per_person=100
    )
    
    gold = MockExample(**gold_report.model_dump())
    pred = MockExample(**pred_report.model_dump())
    
    score_with_extra = travel_intent_metric(gold, pred)
    
    # 对比没有额外目的地的分数
    pred_report_clean = TravelIntentReport(destinations=[Destination(location="南京")], person_count=1, budget_per_person=100)
    score_clean = travel_intent_metric(gold, MockExample(**pred_report_clean.model_dump()))
    
    assert score_with_extra < score_clean

# --- 用例 4：空值安全性测试 ---
def test_none_safety():
    gold = MockExample(destinations=[], person_count=1, budget_per_person=100)
    assert travel_intent_metric(gold, None) == 0