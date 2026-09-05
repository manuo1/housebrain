import factory
from factory.django import DjangoModelFactory

from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory
from water_heater.models import WaterHeaterDayPlan


class WaterHeaterDayPlanFactory(DjangoModelFactory):
    class Meta:
        model = WaterHeaterDayPlan

    water_heater = factory.SubFactory(WaterHeaterFactory)
    date = factory.Faker("date_object")
    schedule_pattern = factory.SubFactory(SchedulePatternFactory)
