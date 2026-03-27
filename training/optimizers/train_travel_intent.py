from datetime import date
import re
import dspy
from dspy.teleprompt import BootstrapFewShot
from backend.app.utils.travel_intent_parser import TravelIntentReport, TravelParserModule
from backend.config import settings

# 导入所有训练数据
from training.data.data0 import trainset as trainset_0, devset as devset_0
from training.data.data1 import trainset as trainset_1, devset as devset_1
from training.data.data2 import trainset as trainset_2, devset as devset_2
from training.data.data3 import trainset as trainset_3, devset as devset_3
from training.data.data4 import trainset as trainset_4, devset as devset_4
from training.data.data5 import trainset as trainset_5, devset as devset_5
from training.data.data6 import trainset as trainset_6, devset as devset_6
from training.data.data7 import trainset as trainset_7, devset as devset_7
from training.data.data8 import trainset as trainset_8, devset as devset_8
from training.data.data9 import trainset as trainset_9, devset as devset_9
from training.data.data10 import trainset as trainset_10, devset as devset_10

# 合并所有训练数据
trainset = (trainset_0 + trainset_1 + trainset_2 + trainset_3 + trainset_4 + 
            trainset_5 + trainset_6 + trainset_7 + trainset_8 + trainset_9 + trainset_10)
devset = (devset_0 + devset_1 + devset_2 + devset_3 + devset_4 + 
          devset_5 + devset_6 + devset_7 + devset_8 + devset_9 + devset_10)

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
    if gold.departure_date == pred.departure_date:
        score += date_weight * 0.5
    if gold.return_date == pred.return_date:
        score += date_weight * 0.5
    
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
lm = dspy.LM(model=settings.LLM_PROVIDER+"/"+settings.LLM_MODEL_NAME, api_key=settings.LLM_API_KEY,temperature=0.1)
deepseek_teacher = dspy.LM(model='deepseek/deepseek-reasoner', api_key=settings.LLM_API_KEY)
dspy.configure(lm=lm)

optimizer = dspy.MIPROv2(
    metric=travel_intent_metric,
    prompt_model=deepseek_teacher, 
    task_model=lm,
    init_temperature = 1.0, # 思维更发散
    # num_candidates=10, 
    num_threads=16,
    auto="light"
)

# 使用合并后的训练集进行训练
print(f"使用 {len(trainset)} 个训练样本进行训练")
optimized_parser = optimizer.compile(
    TravelParserModule(),
    trainset=trainset,
    valset=devset,
    max_bootstrapped_demos=3,
    max_labeled_demos=3,
    # num_trials=10
)
optimized_parser.save("training/result/travel_parser.json")
print("模型训练完成，已保存至 training/result/travel_parser.json")