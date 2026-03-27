from datetime import date
import re
import dspy
from dspy.teleprompt import BootstrapFewShot
from backend.app.utils.travel_intent_parser import TravelIntentReport, TravelParserModule
from training.data.data import trainset
from backend.config import settings

def normalize_loc(text):
    """去掉行政区划后缀"""
    if not text: return ""
    return re.sub(r'(市|省|自治区|特别行政区|特区)$', '', text.strip())

def travel_intent_metric(gold, pred, trace=None):
    """评估函数，用于评估结果的正确性"""
    gold = gold.report
    pred = pred.report
    score = 0
    max_score = 0
    
    # 1. 基础字段校验 (Origin, Person Count, Budget)
    # 权重设定
    base_weight = 2.0
    max_score += base_weight
    
    # 简单的模糊匹配或等值匹配
    if gold.origin is None and pred.origin is None or gold.origin == pred.origin:
        score += base_weight * 0.5
    if gold.person_count is None and pred.person_count is None or gold.person_count == pred.person_count:
        score += base_weight * 0.5
        
    # 2. 时间逻辑校验
    date_weight = 3.0
    max_score += date_weight
    if pred.departure_date <= pred.return_date:
        score += date_weight * 0.3
    if gold.departure_date == pred.departure_date:
        score += date_weight * 0.35
    if gold.return_date == pred.return_date:
        score += date_weight * 0.35
    
    # 目的地列表匹配
    dest_weight = 3.0
    max_score += dest_weight
    
    gold_dests = list(normalize_loc(d.location) for d in gold.destinations)
    pred_dests = list(normalize_loc(d.location) for d in pred.destinations)
    
    if gold_dests == pred_dests:
        score += dest_weight
    else:
        matches = len(set(gold_dests) & set(pred_dests))
        total = max(len(set(gold_dests)), 1)
        score += (matches / total)*dest_weight*0.8

    format_weight = 1.0
    max_score += format_weight
    if isinstance(pred, TravelIntentReport):
        score += format_weight

    # 归一化浮点数
    final_score = score / max_score
    return final_score
print(settings.LLM_PROVIDER)
print(settings.LLM_MODEL_NAME)
lm = dspy.LM(model=settings.LLM_PROVIDER+"/"+settings.LLM_MODEL_NAME, api_key=settings.LLM_API_KEY)
deepseek_teacher = dspy.LM(model='deepseek/deepseek-reasoner', api_key=settings.LLM_API_KEY)
dspy.configure(lm=lm)

optimizer = BootstrapFewShot(
    metric=travel_intent_metric,
    max_bootstrapped_demos=3,  # 自动生成的例子上限
    max_labeled_demos=2,       # 直接从你数据里拿的例子上限
    teacher_settings=dict(lm=deepseek_teacher)
)

# 3. 编译：这会触发模型多次调用，自动寻找最佳 Few-shot
optimized_parser = optimizer.compile(TravelParserModule(), trainset=trainset)
optimized_parser.save("training/result/travel_parser.json")