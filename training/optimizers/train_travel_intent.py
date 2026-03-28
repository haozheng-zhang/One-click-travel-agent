from datetime import date
import importlib
import json
import re
import threading
import dspy
from dspy import evaluate
from dspy.teleprompt import BootstrapFewShot
from rapidfuzz import process
from rapidfuzz import fuzz
from rapidfuzz.fuzz import partial_ratio, token_set_ratio
from backend.app.utils.travel_intent_parser import TravelIntentReport, TravelParserModule
from backend.config import settings

# 导入所有训练数据
trainset, devset = [], []
for i in range(11):
    module = importlib.import_module(f"training.dataset.intentdata.data{i}")
    trainset.extend(module.trainset)
    devset.extend(module.devset)

def _calculate_f1_fuzzy(gold_list, pred_list,similarity=85):
    """F1 评估两个字符串数组的相似度，不考虑顺序"""
    if not gold_list and not pred_list: return 1.0
    if not gold_list or not pred_list: return 0.0
    
    matched_count = 0
    # 为了保证 1对1 匹配，我们需要拷贝一份预测列表，匹配一个删一个
    remaining_pred_list = list(pred_list)
    
    for g_item in gold_list:
        if not remaining_pred_list:
            break
            
        # extractOne 会返回 (字符串, 分数, 索引)
        # score_cutoff=85 相当于内置了 if score > 85 判断
        result = process.extractOne(
            g_item, 
            remaining_pred_list, 
            scorer=fuzz.token_set_ratio, 
            score_cutoff=similarity
        )
        
        if result:
            matched_count += 1
            # 获取在当前 remaining_pred_list 中的索引并剔除
            # 这样可以防止多个标准元素匹配到同一个预测元素
            match_idx = result[2]
            remaining_pred_list.pop(match_idx)
            
    if matched_count == 0: return 0.0
    
    precision = matched_count / len(pred_list)
    recall = matched_count / len(gold_list)
    # 返回归一化分数
    return 2 * (precision * recall) / (precision + recall)

def _validate_destination(gold_dest, pred_dest):
    score = 0.0
    
    # 1. Location (精确匹配)
    if token_set_ratio(gold_dest.location,pred_dest.location)>85:
        score += 0.3
        
    # 2. Hotel Needed (布尔匹配)
    if gold_dest.hotel_needed == pred_dest.hotel_needed:
        score += 0.2
        
    # 3. Attractions
    # 此处不考虑顺序了
    score += 0.25 * _calculate_f1_fuzzy(gold_dest.attractions, pred_dest.attractions)
    score += 0.15 * _calculate_f1_fuzzy(gold_dest.ticket_needed, pred_dest.ticket_needed)
    
    # 5. Stay (模糊字符串匹配)
    if gold_dest.stay == pred_dest.stay:
        score += 0.1
    elif gold_dest.stay and pred_dest.stay:
        ratio = token_set_ratio(gold_dest.stay,pred_dest.stay)/100
        if ratio > 0.8: score += 0.1*ratio
        
    return score

def travel_intent_metric(gold, pred, trace=None):
    """评估函数"""
    if pred is None:
        return 0
    try:
        pred = pred.report
    except AttributeError:
        return 0
    gold = gold.report
    score = 0
    max_score = 0

    if not isinstance(pred, TravelIntentReport):
        return 0
    
    # 1. 基础字段校验 (Origin, Person Count, Budget)
    # 权重设定
    base_weight = 2.0
    max_score += base_weight
    
    # 出发地
    if token_set_ratio(gold.origin,pred.origin)>85:
        score += base_weight * 0.4
    if gold.person_count is None and gold.person_count is None:
        score += base_weight * 0.3
    if gold.person_count == pred.person_count:
        score += base_weight * 0.3

    if gold.budget_per_person is None and pred.budget_per_person is None:
        score += base_weight * 0.3
    elif gold.budget_per_person is not None and pred.budget_per_person is not None:
        if abs(gold.budget_per_person - pred.budget_per_person) / gold.budget_per_person < 0.02:
            score += base_weight * 0.3
    else:
        pass

    # 2. 时间逻辑校验
    date_weight = 3.0
    max_score += date_weight
    if gold.departure_date == pred.departure_date:
        score += date_weight * 0.4
    if gold.return_date == pred.return_date:
        score += date_weight * 0.4
    if gold.duration_days == pred.duration_days:
        score += date_weight * 0.2
    
    # 目的地列表匹配
    dest_weight = 3.0
    max_score += dest_weight
    
    gold_dests = gold.destinations or []
    pred_dests = pred.destinations or []
    num_gold = len(gold_dests)
    num_pred = len(pred_dests)
    
    if num_gold == 0:
            # 如果标准答案没目的地（极少见），模型也没给，则满分
            score += dest_weight if num_pred == 0 else 0
    else:
        total_step_score = 0
        # 使用 zip_longest 或者简单的 index 循环
        for i in range(max(num_gold, num_pred)):
            if i < num_gold and i < num_pred:
                # 核心：调用深度校验函数
                step_score = _validate_destination(gold_dests[i], pred_dests[i])
                total_step_score += step_score
            elif i < num_gold:
                # 惩罚：模型漏掉了目的地
                total_step_score += 0
            else:
                # 惩罚：模型多报了（幻觉）目的地，每个扣 0.2 分
                total_step_score -= 0.2
        
        # 归一化得分并乘以权重
        # ensure score doesn't go below 0
        final_dest_score = max(0, (total_step_score / num_gold) * dest_weight)
        score += final_dest_score

    max_score += 1
    if gold.transport_mode == pred.transport_mode:
        score += 1
    elif gold.transport_mode and pred.transport_mode:
        # 模糊匹配：比如 "高铁" 包含在 "坐高铁去" 里面
        if partial_ratio(gold.transport_mode,pred.transport_mode)>=90:
            score += 0.8

    field_strategies = {
        # 偏好字段：允许口语化，阈值设为 80
        'extra_needs_and_preferences': lambda g, p: _calculate_f1_fuzzy(list(g or []), list(p or []), 80),
        
        # 自动补全字段：必须是精确的变量名，阈值设为 100 (或直接用集合比较)
        'auto_filled_fields': lambda g, p: 1.0 if set(g or []) == set(p or []) else (
            len(set(g or []) & set(p or [])) / len(set(g or []) | set(p or [])) if (g or p) else 1.0
        )
    }

    # 3. 循环逻辑
    for field_name, strategy_func in field_strategies.items():
        max_score += 1.0
        gold_val = getattr(gold, field_name)
        pred_val = getattr(pred, field_name)
        
        # 执行对应的 Lambda 策略
        score += strategy_func(gold_val, pred_val)

    # 归一化浮点数
    final_score = score / max_score
    return final_score

def get_report_diff(gold_dict, pred_dict):
    """比较两个字典，目的地不同则全量打印，其他字段按需对比"""
    diffs = []
    
    # 1. 处理目的地（Destinations）- 只要内容不同，就全量对比
    g_dests = gold_dict.get("destinations", [])
    p_dests = pred_dict.get("destinations", [])
    
    if g_dests != p_dests:
        diffs.append("\n[Destinations 整体冲突]:")
        diffs.append(f"  Gold: {json.dumps(g_dests, ensure_ascii=False)}")
        diffs.append(f"  Pred: {json.dumps(p_dests, ensure_ascii=False)}")
        diffs.append("") # 留空行增加可读性

    # 2. 检查其他顶层字段（过滤掉已经处理过的 destinations）
    all_keys = (set(gold_dict.keys()) | set(pred_dict.keys())) - {"destinations"}
    
    for key in sorted(all_keys):
        g_val = gold_dict.get(key)
        p_val = pred_dict.get(key)
        
        if g_val != p_val:
            diffs.append(f"  [{key}]: Gold={g_val} vs Pred={p_val}")
                
    return "\n".join(diffs) if diffs else "  (无结构化差异)"

log_lock = threading.Lock()

def file_logging_metric(gold, pred, trace=None):
    score = travel_intent_metric(gold, pred, trace)
    
    if score < 0.5:
        with log_lock:
            with open("training/result/failure_cases.log", "a", encoding="utf-8") as f:
                f.write(f"Query: {gold.query} | Score: {score:.2f}\n")
                f.write(f"  Pred: {get_report_diff(gold.report.model_dump(), pred.report.model_dump())}\n")
                f.write("-" * 50 + "\n")
    return score

if __name__ == "__main__":

    print(settings.LLM_PROVIDER)
    print(settings.LLM_MODEL_NAME)
    student_lm = dspy.LM(model=settings.LLM_PROVIDER+"/"+settings.LLM_MODEL_NAME, api_key=settings.LLM_API_KEY,temperature=0,api_base=settings.LLM_BASE_URL,cache=True)
    teacher_lm = dspy.LM(model=settings.TEACH_PROVIDER+"/"+settings.TEACH_MODEL_NAME, api_key=settings.TEACH_API_KEY,api_base=settings.TEACH_BASE_URL,cache=True)
    dspy.configure(lm=student_lm)
    student_res = student_lm("Hi, say 'Student OK'", max_tokens=10)
    print(f"✅ Student Response: {student_res[0]}")
    teacher_res = teacher_lm("Hi, say 'Teacher OK'", max_tokens=10)
    print(f"✅ Teacher Response: {teacher_res[0]}")

    optimizer = dspy.MIPROv2(
        metric=file_logging_metric,
        prompt_model=teacher_lm, 
        task_model=student_lm,
        init_temperature = 1.0, # 思维更发散
        # num_candidates=10, 
        num_threads=24,
        auto="light"
    )

    # 使用合并后的训练集进行训练
    print(f"使用 {len(trainset)} 个训练样本进行训练")
    optimized_parser = optimizer.compile(
        TravelParserModule(),
        trainset=trainset,
        valset=devset,
        minibatch=True,
        max_bootstrapped_demos=3,
        max_labeled_demos=3,
        provide_traceback=True,
        # num_trials=10
    )
    optimized_parser.save("training/result/travel_parser.json")
    print("模型训练完成，已保存至 training/result/travel_parser.json")