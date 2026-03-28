from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.dataset.intentdata.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="劳动节假期去贵阳避免人流，五天，一个人独自旅行，预算三千块",
        report=TravelIntentReport(
            destinations=[Destination(location="贵阳")],
            departure_date=date(2026, 5, 1),
            person_count=1,
            budget_per_person=3000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="中秋节一家人去南昌看滕王阁，三天，七个人，预算两千五一个人",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="南昌", attractions=["滕王阁"], hotel_needed=True, ticket_needed=["滕王阁"])],
            departure_date=date(2026, 9, 25),
            return_date=date(2026, 9, 27),
            duration_days=3,
            person_count=7,
            budget_per_person=2500,
            auto_filled_fields={"departure_date", "destinations[0].ticket_needed", "return_date", "destinations[0].attractions", "destinations[0].hotel_needed"}
        )
    ).with_inputs('query'),
    dspy.Example(
        query="年底去西藏拉萨朝圣，十四天，四个人一起，每人三万块预算",
        report=TravelIntentReport(
            origin="",
            destinations=[Destination(location="拉萨")],
            departure_date=date(2026, 12, 20),
            return_date=date(2027, 1, 3),
            duration_days=14,
            person_count=4,
            budget_per_person=30000,
            extra_needs_and_preferences={"朝圣", "四人团体出行"},
            auto_filled_fields={"return_date", "departure_date"}
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
