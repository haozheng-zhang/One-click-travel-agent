from datetime import date, timedelta
from typing import Optional
import dspy
from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday

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
midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
