import factory
from factory.django import DjangoModelFactory

from planning.models import SchedulePattern


class SchedulePatternFactory(DjangoModelFactory):
    class Meta:
        model = SchedulePattern

    slots = factory.LazyFunction(
        lambda: [
            {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
            {"start": "18:00", "end": "22:00", "type": "temp", "value": 21.0},
        ]
    )

    # Hash is calculated automatically in save()


class SchedulePatternOnOffFactory(DjangoModelFactory):
    class Meta:
        model = SchedulePattern

    slots = factory.LazyFunction(
        lambda: [
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
            {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
        ]
    )
