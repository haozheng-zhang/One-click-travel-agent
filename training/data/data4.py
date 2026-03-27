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
        query="三月陪女朋友去苏州玩，三天两晚，两个人，预算五千块钱",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="苏州")],
            departure_date=date(2026, 3, 15),
            person_count=2,
            budget_per_person=2500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="下下周末和同事去张家界爬山，四天，十个人一起，每人预算三千五",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="张家界")],
            departure_date=_get_next_weekday(5, date.today() + timedelta(days=7)),
            person_count=10,
            budget_per_person=3500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="冬天去三亚避寒，一周七天，全家四个人，预算没限制",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="三亚")],
            departure_date=date(2026, 12, 1),
            person_count=4,
            budget_per_person=5000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
