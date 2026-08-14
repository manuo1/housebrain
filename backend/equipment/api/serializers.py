from rest_framework import serializers

from equipment.constants import EquipmentStatusLevel


class EquipmentCardSerializer(serializers.Serializer):
    """One home-screen card"""

    id = serializers.CharField(help_text="Composite id, format '<model_name>:<pk>'")
    name = serializers.CharField()
    state = serializers.CharField(allow_null=True, help_text="Null if not operational")
    status_level = serializers.ChoiceField(
        choices=[level.value for level in EquipmentStatusLevel],
        help_text="Drives the card color client-side; the front never derives it from `state`",
    )
    operational = serializers.BooleanField(
        help_text="False if the equipment's state couldn't be read (e.g. device unreachable)"
    )


class EquipmentListSerializer(serializers.Serializer):
    long_press_with_state = EquipmentCardSerializer(many=True)
