from rest_framework import serializers

from consumption.constants import ALLOWED_CONSUMPTION_PERIODS, ALLOWED_CONSUMPTION_STEPS


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
                f"Invalid step. Allowed values: {ALLOWED_CONSUMPTION_STEPS} (in minutes)."
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


class ConsumptionByPeriodQueryParamsSerializer(serializers.Serializer):
    start_date = serializers.DateField(
        help_text="First date included in YYYY-MM-DD format.",
    )
    end_date = serializers.DateField(
        help_text="Last date excluded in YYYY-MM-DD format.",
    )
    period = serializers.ChoiceField(
        choices=ALLOWED_CONSUMPTION_PERIODS,
        required=False,
        help_text=f"Aggregation level: {ALLOWED_CONSUMPTION_PERIODS}.",
    )


class ConsumptionByPeriodValueSerializer(serializers.Serializer):
    wh = serializers.IntegerField(help_text="Energy consumption in watt-hours")
    euros = serializers.FloatField(help_text="Price in euros")


class ConsumptionByPeriodSerializer(serializers.Serializer):
    start_date = serializers.DateField(help_text="Start date of the period")
    end_date = serializers.DateField(help_text="End date of the period (excluded)")
    consumption = serializers.DictField(
        child=ConsumptionByPeriodValueSerializer(),
        help_text=(
            "Dictionary mapping tariff period labels (e.g. 'Heures Creuses') "
            "to consumption values with kwh and euros"
        ),
    )


class ConsumptionByPeriodResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(help_text="First date of the data")
    end_date = serializers.DateField(help_text="Last date of the data (excluded)")
    period = serializers.CharField(
        help_text="Aggregation period, e.g. day, week, month"
    )
    data = ConsumptionByPeriodSerializer(
        many=True, help_text="List of consumption data per period"
    )
    totals = serializers.DictField(
        child=TotalByLabelSerializer(),
        help_text="Totals per label with energy (Wh) and cost (Euros).",
        required=False,
    )
