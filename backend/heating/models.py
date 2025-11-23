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
        return f"Pattern {self.id} ({len(self.slots)} créneaux)"

    def clean(self):
        """Validate slots format and check for overlaps"""
        if not self.slots:
            return

        # Validate that slots is a list
        if not isinstance(self.slots, list):
            raise ValidationError("Slots must be a list")

        # Check that all slots have the same type
        if len(self.slots) > 0:
            first_type = None
            for idx, slot in enumerate(self.slots):
                if not isinstance(slot, dict):
                    raise ValidationError(f"Slot {idx} must be a dictionary")

                # Check required fields
                required_fields = ["start", "end", "type", "value"]
                for field in required_fields:
                    if field not in slot:
                        raise ValidationError(
                            f"Slot {idx} missing required field: {field}"
                        )

                # Validate type
                if slot["type"] not in [choice[0] for choice in self.SlotType.choices]:
                    raise ValidationError(
                        f"Slot {idx} has invalid type: {slot['type']}. "
                        f"Must be one of: {', '.join([choice[0] for choice in self.SlotType.choices])}"
                    )

                # Check type consistency
                if first_type is None:
                    first_type = slot["type"]
                elif slot["type"] != first_type:
                    raise ValidationError(
                        f"All slots must have the same type. "
                        f"Found mixed types: '{first_type}' and '{slot['type']}'"
                    )

                # Validate value based on type
                if slot["type"] == self.SlotType.TEMPERATURE:
                    if not isinstance(slot["value"], (int, float)):
                        raise ValidationError(
                            f"Slot {idx} with type 'temp' must have numeric value"
                        )
                elif slot["type"] == self.SlotType.ONOFF:
                    if slot["value"] not in ["on", "off"]:
                        raise ValidationError(
                            f"Slot {idx} with type 'onoff' must have value 'on' or 'off'"
                        )

                # Validate time format
                try:
                    datetime.strptime(slot["start"], "%H:%M")
                    datetime.strptime(slot["end"], "%H:%M")
                except ValueError:
                    raise ValidationError(
                        f"Slot {idx} has invalid time format (expected HH:MM)"
                    )

        # Check for duplicates
        temp_hash = self.calculate_hash()

        qs = HeatingPattern.objects.filter(slots_hash=temp_hash)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError("Un pattern de chauffage identique existe déjà.")

        # Check for overlaps (rest of the code unchanged)
        try:
            sorted_slots = sorted(self.slots, key=lambda s: s["start"])
        except (KeyError, TypeError):
            raise ValidationError("Invalid slot format")

        for i in range(len(sorted_slots) - 1):
            current_end = datetime.strptime(sorted_slots[i]["end"], "%H:%M").time()
            next_start = datetime.strptime(sorted_slots[i + 1]["start"], "%H:%M").time()

            if current_end > next_start:
                raise ValidationError(
                    f"Slots overlap: {sorted_slots[i]['start']}-{sorted_slots[i]['end']} "
                    f"and {sorted_slots[i + 1]['start']}-{sorted_slots[i + 1]['end']}"
                )

    def save(self, *args, **kwargs):
        # Validate before saving
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
        temp_pattern = cls(slots=slots)
        slots_hash = temp_pattern.calculate_hash()

        # Look for existing pattern with this hash
        existing = cls.objects.filter(slots_hash=slots_hash).first()
        if existing:
            return existing, False

        # Otherwise create a new one
        temp_pattern.slots_hash = slots_hash
        temp_pattern.save()
        return temp_pattern, True


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
