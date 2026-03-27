import dspy
from datetime import date
import re
from backend.app.utils.travel_intent_parser import TravelIntentReport

def normalize_loc(text):
    """去掉行政区划后缀"""
    if not text: return ""
    return re.sub(r'(市|省|自治区|特别行政区|特区)$', '', text.strip())

def travel_intent_metric(gold, pred, trace=None):
    score = 0
    max_score = 0
    
    # 1. 基础字段校验 (Origin, Person Count, Budget)
    # 权重设定
    base_weight = 2.0
    max_score += base_weight
    
    # 简单的模糊匹配或等值匹配
    if gold.origin in pred.origin:
        score += base_weight * 0.5
    if gold.person_count == pred.person_count:
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