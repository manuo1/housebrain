from rest_framework import serializers

from consumption.constants import ALLOWED_CONSUMPTION_STEPS


class DailyConsumptionQueryParamsSerializer(serializers.Serializer):
    date = serializers.DateField(
        help_text="Date of consumption in YYYY-MM-DD format. Defaults to today if not provided.",
    )
    step = serializers.IntegerField(
        required=False,
        default=1,
        help_text="Time resolution in minutes. Accepted values: 1, 30, 60. Defaults to 1.",
    )

    def validate_step(self, value):
        if value not in ALLOWED_CONSUMPTION_STEPS:
            raise serializers.ValidationError(
                f"Step {value} is not allowed. Must be an integer in Allowed steps: {ALLOWED_CONSUMPTION_STEPS}."
            )
        return value


class DailyConsumptionElementSerializer(serializers.Serializer):
    date = serializers.DateField(help_text="Date of the measurement.")
    start_time = serializers.CharField(
        help_text="Start time of the consumption period (HH:MM)."
    )
    end_time = serializers.CharField(
        help_text="End time of the consumption period (HH:MM)."
    )
    wh = serializers.FloatField(
        help_text="Energy consumed during the period, in watt-hours (Wh)."
    )
    average_watt = serializers.FloatField(
        help_text="Average power during the period, in watts (W)."
    )
    euros = serializers.FloatField(
        help_text="Estimated cost in euros for the given period."
    )
    interpolated = serializers.BooleanField(
        help_text="True if the data point was interpolated."
    )
    tarif_period = serializers.CharField(
        help_text="Tariff period name (e.g., off-peak, peak)."
    )


class TotalByLabelSerializer(serializers.Serializer):
    wh = serializers.IntegerField(help_text="Total energy consumption in watt-hours.")
    euros = serializers.FloatField(help_text="Total cost in euros.")


class DailyConsumptionOutputSerializer(serializers.Serializer):
    date = serializers.DateField(help_text="Requested date of consumption.")
    step = serializers.IntegerField(help_text="Time resolution in minutes.")
    data = DailyConsumptionElementSerializer(
        many=True, help_text="List of consumption entries."
    )
    totals = serializers.DictField(
        child=TotalByLabelSerializer(),
        help_text="Totals per label with energy (Wh) and cost (Euros).",
        required=False,
    )
