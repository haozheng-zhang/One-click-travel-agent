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
        query="想去秦皇岛海边，两天一晚，情侣两个人，预算三千块钱",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="秦皇岛")],
            departure_date=_get_next_weekday(5),
            person_count=2,
            budget_per_person=1500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="公司集体旅游去舟山群岛，四天，五十个人，每个人预算五千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="舟山")],
            departure_date=date(2026, 5, 10),
            person_count=50,
            budget_per_person=5000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="秋天自驾去新疆游玩，二十天，四个人，预算两万一个人",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="新疆")],
            departure_date=date(2026, 9, 1),
            person_count=4,
            budget_per_person=20000
        )
    ).with_inputs('query'),
]

trainset = dataset[:2]
devset = dataset[2:]
