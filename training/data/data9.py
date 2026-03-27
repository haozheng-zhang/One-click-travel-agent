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
        query="年假从现在开始休，想去泰国旅游十二天，两个人夫妻，每人四万块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="泰国")],
            departure_date=date.today(),
            person_count=2,
            budget_per_person=40000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="周末去平遥古城体验古镇，两天，六个家人，每人两千块预算",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="平遥")],
            departure_date=_get_next_weekday(5),
            person_count=6,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="十一放假带孩子去迪士尼乐园，四天，五个人全家出动，预算五万块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="上海")],
            departure_date=date(2026, 10, 1),
            person_count=5,
            budget_per_person=10000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
