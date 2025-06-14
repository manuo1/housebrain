from rest_framework import serializers


class DailyConsumptionInputSerializer(serializers.Serializer):
    date = serializers.DateField()


class DailyConsumptionOutputSerializer(serializers.Serializer):
    watt_hours = serializers.DictField(
        child=serializers.DictField(child=serializers.IntegerField(allow_null=True)),
        required=False,
    )
