import hashlib
import json
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from rooms.models import Room


class HeatingPattern(models.Model):
    """
    Model representing a reusable heating pattern.
    Contains the complete configuration of time slots for a day.
    """

    class SlotType(models.TextChoices):
        TEMPERATURE = "temp", "Température"
        ONOFF = "onoff", "On/Off"

    # JSON storage for time slots
    # Format: [
    #   {"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},
    #   {"start": "18:00", "end": "22:00", "type": "onoff", "value": "on"}
    # ]
    slots = models.JSONField(
        verbose_name="Créneaux horaires",
        help_text=(
            "Une période non définie donnera forcément un chauffage éteint<br>"
            "Tous les créneaux doivent avoir le même type : temp ou onoff<br>"
            'Si "temp", "value" doit être numérique, exemple:<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;[{"start": "07:00", "end": "09:00", "type": "temp", "value": 20.0},{"start": "12:00", "end": "14:30", "type": "temp", "value": 24.0}]<br>'
            'Si "onoff"; "value" doit être "on" ou "off", exemple:<br>'
            '&nbsp;&nbsp;&nbsp;&nbsp;[{"start": "07:00", "end": "09:00", "type": "onoff", "value": "on"},{"start": "12:00", "end": "14:30", "type": "onoff", "value": "on"}]'
        ),
    )

    # MD5 hash for deduplication (32 characters)
    slots_hash = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name="Hash des créneaux",
        help_text="Hash MD5 des créneaux pour déduplication",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pattern de chauffage"
        verbose_name_plural = "Patterns de chauffage"

    def __str__(self):
        if not self.slots:
            return f"Pattern {self.id} (vide)"

        max_displayed_slots = 4
        parts = []
        for slot in self.slots[:max_displayed_slots]:
            parts.append(f"[{slot['start']}-{slot['end']} {slot['value']}]")

        result = " ".join(parts)
        if len(self.slots) > max_displayed_slots:
            result += f" +{len(self.slots) - max_displayed_slots}"

        return f"Pattern {self.id}: {result}"

    def clean(self):
        """Validate slots format and check for overlaps"""
        if not self.slots:
            return

        # Sort slots by start time
        try:
            self.slots.sort(key=lambda s: s["start"])
        except KeyError:
            raise ValidationError("Each slot must have a 'start' key")

        temp_slots_hash = self.calculate_hash()

        # Prevent modification if used by multiple RoomHeatingDayPlan
        if (
            # modification not creation
            self.pk
            # slots have changed (allow save if no change)
            and self.slots_hash != temp_slots_hash
            # self used by more than one RoomHeatingDayPlan
            and self.day_plans.count() > 1
        ):
            raise ValidationError(
                "Modification not possible: pattern used by multiple RoomHeatingDayPlan"
            )

        # Check for duplicates
        if (
            HeatingPattern.objects.filter(slots_hash=temp_slots_hash)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("An identical heating pattern already exists.")

        # Validate that self.slots is a list
        if not isinstance(self.slots, list):
            raise ValidationError("Slots must be a list")

        # Validate self.slots content
        valid_slot_types = [choice[0] for choice in self.SlotType.choices]
        slot_types_set = set()
        time_ranges = []
        for slot in self.slots:
            if not isinstance(slot, dict):
                raise ValidationError("Slot must be a dictionary")

            # Check required fields
            if set(slot.keys()) != {"start", "end", "type", "value"}:
                raise ValidationError("Slot has missing or invalid field")

            slot_type = slot["type"]

            # Validate type
            if slot_type not in valid_slot_types:
                raise ValidationError("Slot has invalid type")

            # Check type consistency
            slot_types_set.add(slot_type)
            if len(slot_types_set) != 1:
                raise ValidationError("All slots must have the same type.")

            # Validate slot value based on slot type
            validators = {
                self.SlotType.TEMPERATURE: lambda v: isinstance(v, (int, float)),
                self.SlotType.ONOFF: lambda v: v in {"on", "off"},
            }
            if not validators.get(slot_type, lambda v: True)(slot["value"]):
                raise ValidationError("Slot value does not match its type")

            # Validate time format
            try:
                start = datetime.strptime(slot["start"], "%H:%M")
                end = datetime.strptime(slot["end"], "%H:%M")
            except ValueError:
                raise ValidationError("Slot must have HH:MM time format")

            # Validate start is before end
            if start >= end:
                raise ValidationError("Slot start must be before end")

            # Check for overlaps
            if time_ranges and start < time_ranges[-1][1]:
                raise ValidationError("Slots overlap")

            time_ranges.append((start, end))

    def save(self, *args, **kwargs):
        self.clean()
        # Always recalculate hash
        self.slots_hash = self.calculate_hash()
        super().save(*args, **kwargs)

    def calculate_hash(self):
        """Calculate MD5 hash of the slots"""
        # Stable serialization (sorted keys)
        slots_str = json.dumps(self.slots, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(slots_str.encode("utf-8")).hexdigest()

    @classmethod
    def get_or_create_from_slots(cls, slots):
        """
        Get or create a HeatingPattern from a list of slots.
        Uses hash for deduplication.
        """
        # Create temporary pattern to calculate hash
        temp_heating_pattern = cls(slots=slots)
        slots_hash = temp_heating_pattern.calculate_hash()

        # Look for existing pattern with this hash
        existing = cls.objects.filter(slots_hash=slots_hash).first()
        if existing:
            return existing, False

        # Otherwise create a new one
        temp_heating_pattern.slots_hash = slots_hash
        temp_heating_pattern.save()
        return temp_heating_pattern, True


class RoomHeatingDayPlan(models.Model):
    """
    Daily heating plan for a specific room.
    Links a room to a heating pattern for a specific date.
    """

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="heating_day_plans",
        verbose_name="Pièce",
    )

    date = models.DateField(verbose_name="Date")

    heating_pattern = models.ForeignKey(
        "HeatingPattern",
        on_delete=models.PROTECT,
        related_name="day_plans",
        verbose_name="Pattern de chauffage",
        help_text="Programme de chauffage appliqué pour cette journée",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan de chauffage journalier"
        verbose_name_plural = "Plans de chauffage journaliers"
        # One plan per room per day
        unique_together = [["room", "date"]]
        ordering = ["date", "room"]

    def __str__(self):
        return f"{self.room.name} - {self.date}"
