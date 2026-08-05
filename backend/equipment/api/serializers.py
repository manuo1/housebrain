from rest_framework import serializers


class PulseSwitchOutputSerializer(serializers.Serializer):
    """Pulse switch information"""

    id = serializers.IntegerField(help_text="PulseSwitch ID")
    name = serializers.CharField(help_text="PulseSwitch name")
    status = serializers.CharField(
        help_text="Current status: 'IDLE' or 'IN_PROGRESS'"
    )
