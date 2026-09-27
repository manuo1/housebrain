from rest_framework import serializers


class DailyEquipmentPlanInputSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)


class EquipmentDayPlanSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    slots = serializers.JSONField()


class DailyEquipmentPlansSerializer(serializers.Serializer):
    date = serializers.CharField()
    equipments = EquipmentDayPlanSerializer(many=True)
