from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.dataset.intentdata.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="年假从现在开始休，想去泰国旅游十二天，两个人夫妻，每人四万块",
        report=TravelIntentReport(
            destinations=[Destination(location="泰国")],
            departure_date=date.today(),
            person_count=2,
            budget_per_person=40000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="周末去平遥古城体验古镇，两天，六个家人，每人两千块预算",
        report=TravelIntentReport(
            destinations=[Destination(location="平遥")],
            departure_date=_get_next_weekday(5),
            person_count=6,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="十一放假带孩子去迪士尼乐园，四天，五个人全家出动，预算五万块",
        report=TravelIntentReport(
            destinations=[Destination(location="上海",attractions=list(["迪士尼乐园"]))],
            departure_date=date(2026, 10, 1),
            person_count=5,
            budget_per_person=10000
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
