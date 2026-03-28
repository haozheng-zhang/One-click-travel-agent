from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="端午节和朋友一起去厦门，三天，六个人，每人预算两千五",
        report=TravelIntentReport(
            destinations=[Destination(location="厦门")],
            departure_date=date(2026, 6, 9),
            person_count=6,
            budget_per_person=2500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="暑假想去南方旅游，广州玩五天，全家六口人，大概四万块钱",
        report=TravelIntentReport(
            destinations=[Destination(location="广州")],
            departure_date=date(2026, 7, 1),
            person_count=6,
            budget_per_person=5000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="今年秋天想去云南大理，十天自驾游，两个人，预算三万块",
        report=TravelIntentReport(
            destinations=[Destination(location="大理")],
            departure_date=date(2026, 9, 20),
            person_count=2,
            budget_per_person=15000
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
