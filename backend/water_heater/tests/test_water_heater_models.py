from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from equipment.tests.factories import WaterHeaterFactory
from planning.tests.factories import SchedulePatternFactory
from water_heater.tests.factories import WaterHeaterDayPlanFactory


@pytest.mark.django_db
class TestWaterHeaterDayPlan:
    def test_create_water_heater_day_plan(self):
        """Test basic creation of a water heater day plan"""
        plan = WaterHeaterDayPlanFactory()
        assert plan.id is not None
        assert plan.water_heater is not None
        assert plan.date is not None
        assert plan.schedule_pattern is not None

    def test_unique_constraint_water_heater_date(self):
        """Test that only one plan per water heater per date is allowed"""
        water_heater = WaterHeaterFactory()
        pattern = SchedulePatternFactory()
        test_date = date(2025, 10, 24)

        WaterHeaterDayPlanFactory(
            water_heater=water_heater, date=test_date, schedule_pattern=pattern
        )

        with pytest.raises(IntegrityError):
            WaterHeaterDayPlanFactory(
                water_heater=water_heater, date=test_date, schedule_pattern=pattern
            )

    def test_can_create_same_date_different_water_heaters(self):
        """Test that same date can be used for different water heaters"""
        water_heater_1 = WaterHeaterFactory()
        water_heater_2 = WaterHeaterFactory()
        pattern = SchedulePatternFactory()
        test_date = date(2025, 10, 24)

        plan1 = WaterHeaterDayPlanFactory(
            water_heater=water_heater_1, date=test_date, schedule_pattern=pattern
        )
        plan2 = WaterHeaterDayPlanFactory(
            water_heater=water_heater_2, date=test_date, schedule_pattern=pattern
        )

        assert plan1.id != plan2.id
        assert plan1.water_heater != plan2.water_heater
        assert plan1.date == plan2.date

    def test_can_create_same_water_heater_different_dates(self):
        """Test that same water heater can have plans for different dates"""
        water_heater = WaterHeaterFactory()
        pattern = SchedulePatternFactory()

        plan1 = WaterHeaterDayPlanFactory(
            water_heater=water_heater, date=date(2025, 10, 24), schedule_pattern=pattern
        )
        plan2 = WaterHeaterDayPlanFactory(
            water_heater=water_heater, date=date(2025, 10, 25), schedule_pattern=pattern
        )

        assert plan1.id != plan2.id
        assert plan1.water_heater == plan2.water_heater
        assert plan1.date != plan2.date

    def test_multiple_plans_can_share_same_pattern(self):
        """Test that multiple day plans can reuse the same schedule pattern"""
        pattern = SchedulePatternFactory()

        plan1 = WaterHeaterDayPlanFactory(schedule_pattern=pattern)
        plan2 = WaterHeaterDayPlanFactory(schedule_pattern=pattern)

        assert plan1.schedule_pattern.id == plan2.schedule_pattern.id

    def test_str_representation(self):
        """Test string representation of WaterHeaterDayPlan"""
        water_heater = WaterHeaterFactory(name="Cumulus")
        test_date = date(2025, 10, 24)
        plan = WaterHeaterDayPlanFactory(water_heater=water_heater, date=test_date)

        assert str(plan) == "Cumulus - 2025-10-24"

    def test_can_modify_pattern_with_one_usage(self):
        """Test that pattern with single usage can be modified"""
        pattern = SchedulePatternFactory()
        WaterHeaterDayPlanFactory(schedule_pattern=pattern)

        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "onoff", "value": "on"}
        ]
        pattern.save()

        assert pattern.slots[0]["start"] == "10:00"

    def test_cannot_modify_pattern_with_multiple_usages(self):
        """Test that pattern with multiple usages cannot be modified"""
        pattern = SchedulePatternFactory()
        WaterHeaterDayPlanFactory(schedule_pattern=pattern)
        WaterHeaterDayPlanFactory(schedule_pattern=pattern)

        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "onoff", "value": "on"}
        ]

        with pytest.raises(ValidationError, match="used by multiple"):
            pattern.save()

    def test_usage_shared_across_heating_and_water_heater(self):
        """A pattern used by both a room and a water heater counts as
        multiple usages, even though they're different consumer types —
        this is exactly what SchedulePattern.usage_count()'s reflection
        is for."""
        from heating.tests.factories import RoomHeatingDayPlanFactory

        pattern = SchedulePatternFactory()
        RoomHeatingDayPlanFactory(heating_pattern=pattern)
        WaterHeaterDayPlanFactory(schedule_pattern=pattern)

        assert pattern.usage_count() == 2

        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "onoff", "value": "on"}
        ]
        with pytest.raises(ValidationError, match="used by multiple"):
            pattern.save()

    def test_cannot_delete_pattern_in_use(self):
        """Test that deleting a pattern used by day plans is prevented"""
        pattern = SchedulePatternFactory()
        WaterHeaterDayPlanFactory(schedule_pattern=pattern)

        with pytest.raises(ProtectedError):
            pattern.delete()
