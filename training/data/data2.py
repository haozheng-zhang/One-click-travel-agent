from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="下个月去西安看兵马俑，三天两晚，五个人一起去，每个人三千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="西安")],
            departure_date=date(2026, 4, 15),
            person_count=5,
            budget_per_person=3000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="春节假期想带孩子去南京玩，八天七晚，四个人，预算六千一个人",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="南京")],
            departure_date=date(2026, 1, 29),
            person_count=4,
            budget_per_person=6000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="最近想去青岛海边放松一下，四天，两个人，预算四千块钱",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="青岛")],
            departure_date=_get_next_weekday(4),
            person_count=2,
            budget_per_person=4000
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
