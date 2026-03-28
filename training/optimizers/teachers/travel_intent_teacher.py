import dspy
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from backend.app.utils.travel_intent_parser import TravelParserModule
from backend.config import settings
from training.optimizers.train_travel_intent import travel_intent_metric,trainset,devset

# 定义老师 (强逻辑模型)
teacher_lm = dspy.LM(model=settings.TEACH_PROVIDER+"/"+settings.TEACH_MODEL_NAME, api_key=settings.TEACH_API_KEY,api_base=settings.TEACH_BASE_URL,cache=True)
dspy.configure(lm=teacher_lm)
# 设置优化器
# teacher 必须指定，否则它会默认用学生教学生，效果大打折扣
teachset=trainset+devset
optimizer = BootstrapFewShotWithRandomSearch(
    metric=travel_intent_metric,
    max_bootstrapped_demos=8,
    max_labeled_demos=8,
    num_candidate_programs=10, 
    
    teacher_settings=dict(lm=teacher_lm) # 指定老师
)

# 编译过程：这一步就是“老师带徒弟”
# 它会遍历 teachset，让老师生成 Reasoning 和 Report
optimized_program = optimizer.compile(TravelParserModule(),trainset=teachset)
optimized_program.save("train/result/teacher_traces.json")