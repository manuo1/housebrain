import factory
from factory.django import DjangoModelFactory
from heating.models import HeatingPattern, RoomHeatingDayPlan
from rooms.tests.factories import RoomFactory  # Assuming you have this


class HeatingPatternFactory(DjangoModelFactory):
    class Meta:
        model = HeatingPattern

    slots = factory.LazyFunction(
        lambda: [
            {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
            {"start": "18:00", "end": "22:00", "type": "temp", "value": 21.0},
        ]
    )

    # Hash is calculated automatically in save()


class HeatingPatternOnOffFactory(DjangoModelFactory):
    class Meta:
        model = HeatingPattern

    slots = factory.LazyFunction(
        lambda: [
            {"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},
            {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
        ]
    )


class RoomHeatingDayPlanFactory(DjangoModelFactory):
    class Meta:
        model = RoomHeatingDayPlan

    room = factory.SubFactory(RoomFactory)
    date = factory.Faker("date_object")
    heating_pattern = factory.SubFactory(HeatingPatternFactory)
