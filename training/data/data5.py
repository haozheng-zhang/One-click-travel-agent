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
        query="想和室友去武汉体验热干面，两天一晚，三个人，预算一千五一个人",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="武汉")],
            departure_date=_get_next_weekday(6),
            person_count=3,
            budget_per_person=1500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="暑期实习结束想去长沙玩一个星期，五个人，预算四千块一个人",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="长沙")],
            departure_date=date(2026, 8, 15),
            person_count=5,
            budget_per_person=4000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="蜜月旅游选择马尔代夫，十天九晚，两个人新婚，预算每人五万块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="马尔代夫")],
            departure_date=date(2026, 6, 20),
            person_count=2,
            budget_per_person=50000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
