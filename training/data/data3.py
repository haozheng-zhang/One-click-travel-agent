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
        query="端午节和朋友一起去厦门，三天，六个人，每人预算两千五",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="厦门")],
            departure_date=date(2026, 6, 9),
            person_count=6,
            budget_per_person=2500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="暑假想去南方旅游，广州玩五天，全家六口人，大概四万块钱",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="广州")],
            departure_date=date(2026, 7, 1),
            person_count=6,
            budget_per_person=5000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="今年秋天想去云南大理，十天自驾游，两个人，预算三万块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="大理")],
            departure_date=date(2026, 9, 20),
            person_count=2,
            budget_per_person=15000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
