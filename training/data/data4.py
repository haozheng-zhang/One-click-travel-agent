from datetime import date, timedelta
import dspy
from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.data.data0 import _get_next_weekday

dataset = [
    dspy.Example(
        query="三月陪女朋友去苏州玩，三天两晚，两个人，预算五千块钱",
        report=TravelIntentReport(
            destinations=[Destination(location="苏州")],
            departure_date=date(2026, 3, 15),
            person_count=2,
            budget_per_person=2500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="下下周末和同事去张家界爬山，四天，十个人一起，每人预算三千五",
        report=TravelIntentReport(
            destinations=[Destination(location="张家界")],
            departure_date=_get_next_weekday(5, date.today() + timedelta(days=7)),
            person_count=10,
            budget_per_person=3500
        )
    ).with_inputs('query'),
    dspy.Example(
        query="冬天去三亚避寒，一周七天，全家四个人，预算没限制",
        report=TravelIntentReport(
            destinations=[Destination(location="三亚")],
            departure_date=date(2026, 12, 1),
            person_count=4,
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
