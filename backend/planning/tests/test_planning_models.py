import pytest
from django.core.exceptions import ValidationError

from planning.models import SchedulePattern
from planning.tests.factories import SchedulePatternFactory, SchedulePatternOnOffFactory


@pytest.mark.django_db
class TestSchedulePattern:
    def test_create_pattern(self):
        """Test basic creation of a schedule pattern"""
        pattern = SchedulePatternFactory()
        assert pattern.id is not None
        assert len(pattern.slots) == 2
        assert pattern.slots_hash is not None
        assert len(pattern.slots_hash) == 32  # MD5 hash length

    def test_hash_calculated_automatically(self):
        """Test that hash is calculated on save"""
        pattern = SchedulePatternFactory.build(slots_hash="")
        pattern.save()
        assert pattern.slots_hash is not None
        assert len(pattern.slots_hash) == 32

    def test_get_or_create_from_slots_creates_new(self):
        """Test get_or_create_from_slots creates a new pattern"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]
        pattern, created = SchedulePattern.get_or_create_from_slots(slots)

        assert created is True
        assert pattern.id is not None
        assert pattern.slots == slots

    def test_get_or_create_from_slots_reuses_existing(self):
        """Test get_or_create_from_slots reuses existing pattern with same slots"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]

        pattern1, created1 = SchedulePattern.get_or_create_from_slots(slots)
        assert created1 is True

        pattern2, created2 = SchedulePattern.get_or_create_from_slots(slots)
        assert created2 is False
        assert pattern1.id == pattern2.id

    def test_overlapping_slots_raises_error(self):
        """Test that overlapping slots raise ValidationError"""
        with pytest.raises(ValidationError, match="Slots overlap"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "end": "10:00", "type": "temp", "value": 20.0},
                    {"start": "09:00", "end": "12:00", "type": "temp", "value": 21.0},
                ]
            )

    def test_exact_overlapping_slots_raises_error(self):
        """Test that overlapping slots raise ValidationError"""
        with pytest.raises(ValidationError, match="Slots overlap"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "end": "10:00", "type": "temp", "value": 20.0},
                    {"start": "10:00", "end": "12:00", "type": "temp", "value": 21.0},
                ]
            )

    def test_reversed_start_and_stop_slot_raises_error(self):
        """Test that reversed start and stop slots raise ValidationError"""
        with pytest.raises(ValidationError, match="Slot start must be before end"):
            SchedulePatternFactory(
                slots=[
                    {"start": "11:00", "end": "10:00", "type": "temp", "value": 20.0},
                ]
            )

    def test_invalid_slot_format_missing_field(self):
        """Test that missing required field raises ValidationError"""
        with pytest.raises(ValidationError, match="missing or invalid field"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "type": "temp", "value": 20.0}  # Missing 'end'
                ]
            )

    def test_invalid_slot_type(self):
        """Test that invalid type raises ValidationError"""
        with pytest.raises(ValidationError, match="invalid type"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "invalid", "value": 20.0}
                ]
            )

    def test_invalid_value_for_temp_type(self):
        """Test that non-numeric value for temp type raises ValidationError"""
        with pytest.raises(ValidationError, match="Slot value does not match its type"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "temp", "value": "hot"}
                ]
            )

    def test_invalid_value_for_onoff_type(self):
        """Test that invalid value for onoff type raises ValidationError"""
        with pytest.raises(ValidationError, match="Slot value does not match its type"):
            SchedulePatternFactory(
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
            SchedulePatternFactory(
                slots=[
                    {"start": "25:00", "end": "09:00", "type": "temp", "value": 20.0}
                ]
            )

    def test_onoff_pattern_creation(self):
        """Test creation of on/off pattern"""
        pattern = SchedulePatternOnOffFactory()
        assert pattern.id is not None
        assert all(slot["type"] == "onoff" for slot in pattern.slots)

    def test_can_delete_unused_pattern(self):
        """Test that deleting an unused pattern works fine"""
        pattern = SchedulePatternFactory()
        pattern_id = pattern.id

        pattern.delete()

        assert not SchedulePattern.objects.filter(id=pattern_id).exists()

    def test_mixed_slot_types_raises_error(self):
        """Test that mixing temp and onoff types raises ValidationError"""
        with pytest.raises(ValidationError, match="All slots must have the same type"):
            SchedulePatternFactory(
                slots=[
                    {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
                    {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"},
                ]
            )

    def test_duplicate_pattern_raises_error(self):
        """Creating a pattern with identical slots must raise ValidationError"""
        slots = [{"start": "08:00", "end": "10:00", "type": "temp", "value": 19.0}]

        p1 = SchedulePatternFactory(slots=slots)
        assert p1.id is not None

        with pytest.raises(ValidationError, match="schedule pattern already exists."):
            p2 = SchedulePattern(slots=slots)
            p2.full_clean()  # triggers clean()
            p2.save()  # should never reach here

        assert SchedulePattern.objects.count() == 1

    def test_usage_count_with_no_consumer(self):
        """Test that usage_count is 0 when nothing points to the pattern"""
        pattern = SchedulePatternFactory()
        assert pattern.usage_count() == 0

    def test_can_modify_pattern_with_zero_usage(self):
        """Test that pattern with no usage can be modified"""
        pattern = SchedulePatternFactory()
        pattern.slots = [
            {"start": "10:00", "end": "12:00", "type": "temp", "value": 21.0}
        ]
        pattern.save()

        assert pattern.slots[0]["start"] == "10:00"
        assert pattern.slots[0]["value"] == 21.0
