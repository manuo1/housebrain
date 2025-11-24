import pytest
from django.core.exceptions import ValidationError
from heating.models import HeatingPattern
from heating.tests.factories import HeatingPatternFactory, HeatingPatternOnOffFactory
from rooms.tests.factories import RoomFactory


@pytest.mark.django_db
class TestHeatingPattern:
    def test_create_heating_pattern(self):
        """Test basic creation of a heating pattern"""
        pattern = HeatingPatternFactory()
        assert pattern.id is not None
        assert len(pattern.slots) == 2
        assert pattern.slots_hash is not None
        assert len(pattern.slots_hash) == 32  # MD5 hash length

    def test_hash_calculated_automatically(self):
        """Test that hash is calculated on save"""
        pattern = HeatingPatternFactory.build(slots_hash="")
        pattern.save()
        assert pattern.slots_hash is not None
        assert len(pattern.slots_hash) == 32

    def test_get_or_create_from_slots_creates_new(self):
        """Test get_or_create_from_slots creates a new pattern"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]
        pattern, created = HeatingPattern.get_or_create_from_slots(slots)

        assert created is True
        assert pattern.id is not None
        assert pattern.slots == slots

    def test_get_or_create_from_slots_reuses_existing(self):
        """Test get_or_create_from_slots reuses existing pattern with same slots"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]

        # Create first pattern
        pattern1, created1 = HeatingPattern.get_or_create_from_slots(slots)
        assert created1 is True

        # Try to create with same slots
        pattern2, created2 = HeatingPattern.get_or_create_from_slots(slots)
        assert created2 is False
        assert pattern1.id == pattern2.id

    def test_overlapping_slots_raises_error(self):
        """Test that overlapping slots raise ValidationError"""
        with pytest.raises(ValidationError, match="Slots overlap"):
            HeatingPatternFactory(
                slots=[
                    {"start": "07:00", "end": "10:00", "type": "temp", "value": 20.0},
                    {
                        "start": "09:00",
                        "end": "12:00",
                        "type": "temp",
                        "value": 21.0,
                    },  # Overlaps!
                ]
            )

    def test_reversed_start_and_stop_slot_raises_error(self):
        """Test that reversed start and stop slots raise ValidationError"""
        with pytest.raises(ValidationError, match="Slot start must be before end"):
            HeatingPatternFactory(
                slots=[
                    {"start": "11:00", "end": "10:00", "type": "temp", "value": 20.0},
                ]
            )

    def test_invalid_slot_format_missing_field(self):
        """Test that missing required field raises ValidationError"""
        with pytest.raises(ValidationError, match="missing or invalid field"):
            HeatingPatternFactory(
                slots=[
                    {"start": "07:00", "type": "temp", "value": 20.0}  # Missing 'end'
                ]
            )

    def test_invalid_slot_type(self):
        """Test that invalid type raises ValidationError"""
        with pytest.raises(ValidationError, match="invalid type"):
            HeatingPatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "invalid", "value": 20.0}
                ]
            )

    def test_invalid_value_for_temp_type(self):
        """Test that non-numeric value for temp type raises ValidationError"""
        with pytest.raises(ValidationError, match="Slot value does not match its type"):
            HeatingPatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "temp", "value": "hot"}
                ]
            )

    def test_invalid_value_for_onoff_type(self):
        """Test that invalid value for onoff type raises ValidationError"""
        with pytest.raises(ValidationError, match="Slot value does not match its type"):
            HeatingPatternFactory(
                slots=[
                    {
                        "start": "07:00",
                        "end": "09:00",
                        "type": "onoff",
                        "value": "maybe",
                    }
                ]
            )

    def test_invalid_time_format(self):
        """Test that invalid time format raises ValidationError"""
        with pytest.raises(ValidationError, match="Slot must have HH:MM time format"):
            HeatingPatternFactory(
                slots=[
                    {"start": "25:00", "end": "09:00", "type": "temp", "value": 20.0}
                ]
            )

    def test_onoff_pattern_creation(self):
        """Test creation of on/off heating pattern"""
        pattern = HeatingPatternOnOffFactory()
        assert pattern.id is not None
        assert all(slot["type"] == "onoff" for slot in pattern.slots)

    def test_cannot_delete_pattern_in_use(self):
        """Test that deleting a pattern used by day plans is prevented"""
        from django.db.models import ProtectedError
        from heating.tests.factories import RoomHeatingDayPlanFactory

        pattern = HeatingPatternFactory()
        # Create a day plan using this pattern
        RoomHeatingDayPlanFactory(heating_pattern=pattern)

        # Try to delete the pattern
        with pytest.raises(ProtectedError):
            pattern.delete()

    def test_can_delete_unused_pattern(self):
        """Test that deleting an unused pattern works fine"""
        pattern = HeatingPatternFactory()
        pattern_id = pattern.id

        pattern.delete()

        # Verify it's deleted
        assert not HeatingPattern.objects.filter(id=pattern_id).exists()

    def test_mixed_slot_types_raises_error(self):
        """Test that mixing temp and onoff types raises ValidationError"""
        with pytest.raises(ValidationError, match="All slots must have the same type"):
            HeatingPatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
                    {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
                ]
            )

    def test_duplicate_pattern_raises_error(self):
        """Creating a pattern with identical slots must raise ValidationError"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]

        # First creation works
        p1 = HeatingPatternFactory(slots=slots)
        assert p1.id is not None

        # Second creation with same slots must fail
        with pytest.raises(ValidationError, match="heating pattern already exists."):
            p2 = HeatingPattern(slots=slots)
            p2.full_clean()  # triggers clean()
            p2.save()  # should never reach here

        # Only one entry must exist in DB
        assert HeatingPattern.objects.count() == 1


@pytest.mark.django_db
class TestRoomHeatingDayPlan:
    def test_create_room_heating_day_plan(self):
        """Test basic creation of a room heating day plan"""
        from heating.tests.factories import RoomHeatingDayPlanFactory

        plan = RoomHeatingDayPlanFactory()
        assert plan.id is not None
        assert plan.room is not None
        assert plan.date is not None
        assert plan.heating_pattern is not None

    def test_unique_constraint_room_date(self):
        """Test that only one plan per room per date is allowed"""
        from datetime import date

        from django.db import IntegrityError
        from heating.tests.factories import RoomHeatingDayPlanFactory

        room = RoomFactory()
        pattern = HeatingPatternFactory()
        test_date = date(2025, 10, 24)

        # Create first plan
        RoomHeatingDayPlanFactory(room=room, date=test_date, heating_pattern=pattern)

        # Try to create second plan for same room and date
        with pytest.raises(IntegrityError):
            RoomHeatingDayPlanFactory(
                room=room, date=test_date, heating_pattern=pattern
            )

    def test_can_create_same_date_different_rooms(self):
        """Test that same date can be used for different rooms"""
        from datetime import date

        from heating.tests.factories import RoomHeatingDayPlanFactory

        room1 = RoomFactory()
        room2 = RoomFactory()
        pattern = HeatingPatternFactory()
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
        from datetime import date

        from heating.tests.factories import RoomHeatingDayPlanFactory

        room = RoomFactory()
        pattern = HeatingPatternFactory()

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
        """Test that multiple day plans can reuse the same heating pattern"""
        from heating.tests.factories import RoomHeatingDayPlanFactory

        pattern = HeatingPatternFactory()

        plan1 = RoomHeatingDayPlanFactory(heating_pattern=pattern)
        plan2 = RoomHeatingDayPlanFactory(heating_pattern=pattern)

        assert plan1.heating_pattern.id == plan2.heating_pattern.id

    def test_str_representation(self):
        """Test string representation of RoomHeatingDayPlan"""
        from datetime import date

        from heating.tests.factories import RoomHeatingDayPlanFactory

        room = RoomFactory(name="Salon")
        test_date = date(2025, 10, 24)
        plan = RoomHeatingDayPlanFactory(room=room, date=test_date)

        assert str(plan) == "Salon - 2025-10-24"
