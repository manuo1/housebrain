from datetime import date, timedelta

import pytest
from heating.api.mutators import duplicate_heating_plan_with_override
from heating.models import RoomHeatingDayPlan
from heating.tests.factories import HeatingPatternFactory, RoomHeatingDayPlanFactory
from rooms.tests.factories import RoomFactory

DEFAULT_DATE = date(2025, 12, 9)
DEFAULT_SLOTS = [{"start": "07:00", "end": "23:30", "type": "onoff", "value": "on"}]


@pytest.mark.django_db
def test_duplicate_heating_plan_creates_new_plans():
    """Test creating new heating plans for dates without existing plans"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    duplication_dates = [DEFAULT_DATE, DEFAULT_DATE + timedelta(days=1)]

    result = duplicate_heating_plan_with_override(
        room_id=room.id,
        heating_pattern_id=heating_pattern.id,
        duplication_dates=duplication_dates,
    )

    assert result == 2
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 2

    for duplication_date in duplication_dates:
        plan = RoomHeatingDayPlan.objects.get(room=room, date=duplication_date)
        assert plan.heating_pattern == heating_pattern
        assert plan.created_at is not None
        assert plan.updated_at is not None


@pytest.mark.django_db
def test_duplicate_heating_plan_overrides_existing_plans():
    """Test overriding existing heating plans with new pattern"""
    room = RoomFactory(id=1)

    old_pattern = HeatingPatternFactory(
        slots=[{"start": "08:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )
    new_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create existing plan
    existing_plan = RoomHeatingDayPlanFactory(
        room=room, date=DEFAULT_DATE, heating_pattern=old_pattern
    )
    old_updated_at = existing_plan.updated_at

    duplication_dates = [DEFAULT_DATE]

    result = duplicate_heating_plan_with_override(
        room_id=room.id,
        heating_pattern_id=new_pattern.id,
        duplication_dates=duplication_dates,
    )

    assert result == 1
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 1

    updated_plan = RoomHeatingDayPlan.objects.get(room=room, date=DEFAULT_DATE)
    assert updated_plan.heating_pattern == new_pattern
    assert updated_plan.updated_at > old_updated_at


@pytest.mark.django_db
def test_duplicate_heating_plan_mixed_new_and_existing():
    """Test creating and overriding plans in same operation"""
    room = RoomFactory(id=1)

    old_pattern = HeatingPatternFactory(
        slots=[{"start": "08:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )
    new_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Create existing plan for first date only
    RoomHeatingDayPlanFactory(room=room, date=DEFAULT_DATE, heating_pattern=old_pattern)

    duplication_dates = [
        DEFAULT_DATE,  # Should override
        DEFAULT_DATE + timedelta(days=1),  # Should create
        DEFAULT_DATE + timedelta(days=2),  # Should create
    ]

    result = duplicate_heating_plan_with_override(
        room_id=room.id,
        heating_pattern_id=new_pattern.id,
        duplication_dates=duplication_dates,
    )

    assert result == 3
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 3

    # All plans should have new pattern
    for duplication_date in duplication_dates:
        plan = RoomHeatingDayPlan.objects.get(room=room, date=duplication_date)
        assert plan.heating_pattern == new_pattern


@pytest.mark.django_db
def test_duplicate_heating_plan_empty_dates():
    """Test with empty duplication dates list"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    result = duplicate_heating_plan_with_override(
        room_id=room.id, heating_pattern_id=heating_pattern.id, duplication_dates=[]
    )

    assert result == 0
    assert RoomHeatingDayPlan.objects.filter(room=room).count() == 0


@pytest.mark.django_db
def test_duplicate_heating_plan_multiple_rooms_isolation():
    """Test that duplication only affects specified room"""
    room_1 = RoomFactory(id=1)
    room_2 = RoomFactory(id=2)

    pattern_1 = HeatingPatternFactory(slots=DEFAULT_SLOTS)
    pattern_2 = HeatingPatternFactory(
        slots=[{"start": "12:00", "end": "18:00", "type": "onoff", "value": "on"}]
    )

    # Create existing plan for room_2
    RoomHeatingDayPlanFactory(room=room_2, date=DEFAULT_DATE, heating_pattern=pattern_2)

    # Duplicate for room_1 only
    result = duplicate_heating_plan_with_override(
        room_id=room_1.id,
        heating_pattern_id=pattern_1.id,
        duplication_dates=[DEFAULT_DATE],
    )

    assert result == 1

    # room_1 should have new plan
    plan_1 = RoomHeatingDayPlan.objects.get(room=room_1, date=DEFAULT_DATE)
    assert plan_1.heating_pattern == pattern_1

    # room_2 should be unchanged
    plan_2 = RoomHeatingDayPlan.objects.get(room=room_2, date=DEFAULT_DATE)
    assert plan_2.heating_pattern == pattern_2


@pytest.mark.django_db
def test_duplicate_heating_plan_same_date_multiple_times():
    """Test duplicating same date multiple times in list (should deduplicate)"""
    room = RoomFactory(id=1)
    heating_pattern = HeatingPatternFactory(slots=DEFAULT_SLOTS)

    # Same date repeated
    duplication_dates = [DEFAULT_DATE, DEFAULT_DATE, DEFAULT_DATE]

    result = duplicate_heating_plan_with_override(
        room_id=room.id,
        heating_pattern_id=heating_pattern.id,
        duplication_dates=duplication_dates,
    )

    # Should only create one plan despite duplicates
    assert RoomHeatingDayPlan.objects.filter(room=room, date=DEFAULT_DATE).count() == 1
