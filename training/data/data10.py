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
        query="国庆假期想去桂林山水游，一周七天，三个老年人，每人三千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="桂林")],
            departure_date=date(2026, 10, 1),
            person_count=3,
            budget_per_person=3000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="下个月公司团建去三亚，五天四晚，一百人参加，每人两千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="三亚")],
            departure_date=date(2026, 4, 20),
            person_count=100,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="独自背包客计划，去云南环游，二十天，一个人，预算五千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="云南")],
            departure_date=date(2026, 7, 15),
            person_count=1,
            budget_per_person=5000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
