from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport

def _get_next_weekday(target_weekday: int, from_date: Optional[date] = None) -> date:
    """
    计算从某个日期开始的下一个目标周几的绝对日期
    target_weekday: 0(一), 1(二), 2(三)... 6(日)
    """
    start_date = from_date or date.today()
    days_ahead = (target_weekday - start_date.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    return start_date + timedelta(days=days_ahead)


dataset = [
    dspy.Example(
        query="下周三去北京玩四天，两个人，预算八千",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="北京")],
            departure_date=_get_next_weekday(2),
            person_count=2,
            budget_per_person=4000
        )
    ).with_inputs('query'), # 明确告诉 DSPy，query 是输入，report 是标签
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]