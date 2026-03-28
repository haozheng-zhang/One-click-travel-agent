from datetime import date, timedelta
from typing import Optional

import dspy

from backend.app.utils.travel_intent_parser import Destination, TravelIntentReport
from training.dataset.intentdata.data0 import _get_next_weekday


dataset = [
    dspy.Example(
        query="四月清明节去杭州西湖游玩，三天两晚，三个人，每人两千块",
        report=TravelIntentReport(
            destinations=[Destination(location="杭州")],
            departure_date=date(2026, 4, 4),
            person_count=3,
            budget_per_person=2000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="周末突然想出游，去南京一天一晚，一个人自驾，预算一千",
        report=TravelIntentReport(
            destinations=[Destination(location="南京")],
            departure_date=_get_next_weekday(5),
            person_count=1,
            budget_per_person=1000
        )
    ).with_inputs('query'),
    dspy.Example(
        query="寒假和朋友去重庆火锅之旅，五天，八个人，每人预算四千块",
        report=TravelIntentReport(
            origin="未知",
            destinations=[Destination(location="重庆")],
            departure_date=date(2027, 1, 20),
            return_date=date(2027, 1, 24),
            duration_days=5,
            person_count=8,
            budget_per_person=4000,
            extra_needs_and_preferences={"火锅美食之旅"},
            auto_filled_fields={"origin"}
        )
    ).with_inputs('query'),
]

midIndex = len(dataset)//2
trainset = dataset[:midIndex]
devset = dataset[midIndex:]
