from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="想去秦皇岛海边，两天一晚，情侣两个人，预算三千块钱",
        report=TravelIntentReport(
            destinations=[Destination(location="秦皇岛")],
            departure_date=_get_next_weekday(5),
            person_count=2,
            budget_per_person=1500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="公司集体旅游去舟山群岛，四天，五十个人，每个人预算五千块",
        report=TravelIntentReport(
            destinations=[Destination(location="舟山")],
            departure_date=date(2026, 5, 10),
            person_count=50,
            budget_per_person=5000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="秋天自驾去新疆游玩，二十天，四个人，预算两万一个人",
        report=TravelIntentReport(
            destinations=[Destination(location="新疆")],
            departure_date=date(2026, 9, 1),
            person_count=4,
            budget_per_person=20000
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
