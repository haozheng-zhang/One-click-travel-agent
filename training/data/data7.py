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
        query="四月清明节去杭州西湖游玩，三天两晚，三个人，每人两千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="杭州")],
            departure_date=date(2026, 4, 4),
            person_count=3,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="周末突然想出游，去南京一天一晚，一个人自驾，预算一千",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="南京")],
            departure_date=_get_next_weekday(5),
            person_count=1,
            budget_per_person=1000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="寒假和朋友去重庆火锅之旅，五天，八个人，每人预算四千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="重庆")],
            departure_date=date(2026, 2, 1),
            person_count=8,
            budget_per_person=4000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
