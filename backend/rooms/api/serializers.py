from rest_framework import serializers


class HeatingSerializer(serializers.Serializer):
    """Heating control configuration"""

    mode = serializers.CharField(
        help_text="Heating control mode: 'thermostat' or 'on_off'"
    )
    value = serializers.JSONField(
        help_text="Current setpoint (float for thermostat) or state (string for on_off)"
    )


class TemperatureMeasurementsSerializer(serializers.Serializer):
    """Temperature sensor measurements"""

    temperature = serializers.FloatField(
        allow_null=True, help_text="Current temperature in °C (null if data is stale)"
    )
    trend = serializers.CharField(
        allow_null=True, help_text="Temperature trend: 'up', 'down', 'same', or null"
    )


class TemperatureSerializer(serializers.Serializer):
    """Temperature sensor information with real-time data"""

    id = serializers.IntegerField(help_text="Temperature sensor ID")
    mac_short = serializers.CharField(
        help_text="Last 3 segments of MAC address (e.g., '46:C0:F4')"
    )
    signal_strength = serializers.IntegerField(help_text="Signal quality as bars (1-5)")
    measurements = TemperatureMeasurementsSerializer(
        help_text="Current and trend measurements"
    )


class RadiatorSerializer(serializers.Serializer):
    """Radiator state information"""

    id = serializers.IntegerField(help_text="Radiator ID")
    state = serializers.CharField(
        help_text="Current state: 'on', 'off', 'turning_on', 'shutting_down', 'load_shed', 'undefined'"
    )


class RoomOutputSerializer(serializers.Serializer):
    """Complete room information with heating, temperature, and radiator"""

    id = serializers.IntegerField(help_text="Room ID")
    name = serializers.CharField(help_text="Room name")
    heating = HeatingSerializer(help_text="Heating control configuration")
    temperature = TemperatureSerializer(
        allow_null=True,
        help_text="Temperature sensor data (null if no sensor assigned)",
    )
    radiator = RadiatorSerializer(
        allow_null=True, help_text="Radiator state (null if no radiator assigned)"
    )
