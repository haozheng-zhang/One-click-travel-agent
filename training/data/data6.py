from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="劳动节假期去贵阳避免人流，五天，一个人独自旅行，预算三千块",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="贵阳")],
            departure_date=date(2026, 5, 1),
            person_count=1,
            budget_per_person=3000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="中秋节一家人去南昌看滕王阁，三天，七个人，预算两千五一个人",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="南昌")],
            departure_date=date(2026, 9, 15),
            person_count=7,
            budget_per_person=2500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="年底去西藏拉萨朝圣，十四天，四个人一起，每人三万块预算",
        report=TravelIntentReport(
            origin=None,
            destinations=[Destination(location="拉萨")],
            departure_date=date(2026, 11, 1),
            person_count=4,
            budget_per_person=30000
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
