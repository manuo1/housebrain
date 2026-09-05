import factory
from factory.django import DjangoModelFactory

from heating.models import RoomHeatingDayPlan
from planning.tests.factories import SchedulePatternFactory
from rooms.tests.factories import RoomFactory  # Assuming you have this


class RoomHeatingDayPlanFactory(DjangoModelFactory):
    class Meta:
        model = RoomHeatingDayPlan

    room = factory.SubFactory(RoomFactory)
    date = factory.Faker("date_object")
    heating_pattern = factory.SubFactory(SchedulePatternFactory)
