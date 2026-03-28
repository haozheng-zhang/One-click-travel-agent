from datetime import date, timedelta
from typing import Optional
import dspy
from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.dataset.intentdata.data0 import _get_next_weekday
dataset = [
    dspy.Example(
        query="和家人五一去上海旅游五天，三个人，每人预算五千块",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="上海")],
            departure_date=date(2026, 5, 1),
            person_count=3,
            budget_per_person=5000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="周末想去杭州玩两天，就我一个人，预算不超过两千",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="杭州")],
            departure_date=_get_next_weekday(5),
            person_count=1,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="十一国庆假期，我和老婆孩子四个人想去成都，玩七天，预算一万五",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="成都")],
            departure_date=date(2026, 10, 1),
            person_count=4,
            budget_per_person=3750
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
