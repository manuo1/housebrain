from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError

from heating.tests.factories import RoomHeatingDayPlanFactory
from planning.models import SchedulePattern
from planning.tests.factories import SchedulePatternFactory
from rooms.tests.factories import RoomFactory


@pytest.mark.django_db
class TestRoomHeatingDayPlan:
    def test_create_room_heating_day_plan(self):
        """Test basic creation of a room heating day plan"""
        plan = RoomHeatingDayPlanFactory()
        assert plan.id is not None
        assert plan.room is not None
        assert plan.date is not None
        assert plan.heating_pattern is not None

    def test_unique_constraint_room_date(self):
        """Test that only one plan per room per date is allowed"""
        room = RoomFactory()
        pattern = SchedulePatternFactory()
        test_date = date(2025, 10, 24)

        RoomHeatingDayPlanFactory(room=room, date=test_date, heating_pattern=pattern)

        with pytest.raises(IntegrityError):
            RoomHeatingDayPlanFactory(
                room=room, date=test_date, heating_pattern=pattern
            )

    def test_can_create_same_date_different_rooms(self):
        """Test that same date can be used for different rooms"""
        room1 = RoomFactory()
        room2 = RoomFactory()
        pattern = SchedulePatternFactory()
        test_date = date(2025, 10, 24)

        plan1 = RoomHeatingDayPlanFactory(
            room=room1, date=test_date, heating_pattern=pattern
        )
        plan2 = RoomHeatingDayPlanFactory(
            room=room2, date=test_date, heating_pattern=pattern
        )

        assert plan1.id != plan2.id
        assert plan1.room != plan2.room
        assert plan1.date == plan2.date

    def test_can_create_same_room_different_dates(self):
        """Test that same room can have plans for different dates"""
        room = RoomFactory()
        pattern = SchedulePatternFactory()

        plan1 = RoomHeatingDayPlanFactory(
            room=room, date=date(2025, 10, 24), heating_pattern=pattern
        )
        plan2 = RoomHeatingDayPlanFactory(
            room=room, date=date(2025, 10, 25), heating_pattern=pattern
        )

        assert plan1.id != plan2.id
        assert plan1.room == plan2.room
        assert plan1.date != plan2.date

    def test_multiple_plans_can_share_same_pattern(self):
        """Test that multiple day plans can reuse the same schedule pattern"""
        pattern = SchedulePatternFactory()

        plan1 = RoomHeatingDayPlanFactory(heating_pattern=pattern)
        plan2 = RoomHeatingDayPlanFactory(heating_pattern=pattern)

        assert plan1.heating_pattern.id == plan2.heating_pattern.id

    def test_str_representation(self):
        """Test string representation of RoomHeatingDayPlan"""
        room = RoomFactory(name="Salon")
        test_date = date(2025, 10, 24)
        plan = RoomHeatingDayPlanFactory(room=room, date=test_date)

        assert str(plan) == "Salon - 2025-10-24"

    def test_can_modify_pattern_with_zero_usage(self):
        """Test that pattern with no usage can be modified"""
        pattern = SchedulePatternFactory()
        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "temp", "value": 21.0}
        ]
        pattern.save()

        assert pattern.slots[0]["start"] == "10:00"
        assert pattern.slots[0]["value"] == 21.0

    def test_can_modify_pattern_with_one_usage(self):
        """Test that pattern with single usage can be modified"""
        pattern = SchedulePatternFactory()
        RoomHeatingDayPlanFactory(heating_pattern=pattern)

        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "temp", "value": 21.0}
        ]
        pattern.save()

        assert pattern.slots[0]["start"] == "10:00"
        assert pattern.slots[0]["value"] == 21.0

    def test_cannot_modify_pattern_with_multiple_usages(self):
        """Test that pattern with multiple usages cannot be modified"""
        pattern = SchedulePatternFactory()
        RoomHeatingDayPlanFactory(heating_pattern=pattern)
        RoomHeatingDayPlanFactory(heating_pattern=pattern)

        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "temp", "value": 21.0}
        ]

        with pytest.raises(ValidationError, match="used by multiple"):
            pattern.save()

    def test_can_save_pattern_without_changes_multiple_usages(self):
        """Test that pattern with multiple usages can be saved without modifications"""
        pattern = SchedulePatternFactory()
        plan1 = RoomHeatingDayPlanFactory(heating_pattern=pattern)
        plan2 = RoomHeatingDayPlanFactory(heating_pattern=pattern)

        # Save without modifying slots
        pattern.save()

        # Verify pattern still linked to both plans
        assert plan1.heating_pattern.id == pattern.id
        assert plan2.heating_pattern.id == pattern.id

    def test_cannot_delete_pattern_in_use(self):
        """Test that deleting a pattern used by day plans is prevented"""
        pattern = SchedulePatternFactory()
        RoomHeatingDayPlanFactory(heating_pattern=pattern)

        with pytest.raises(ProtectedError):
            pattern.delete()

    def test_can_delete_unused_pattern(self):
        """Test that deleting an unused pattern works fine"""
        pattern = SchedulePatternFactory()
        pattern_id = pattern.id

        pattern.delete()

        assert not SchedulePattern.objects.filter(id=pattern_id).exists()
