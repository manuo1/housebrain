from rest_framework import serializers

from planning.models import SchedulePattern


class DailyEquipmentPlanInputSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)


class EquipmentCalendarInputSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class EquipmentCalendarDaySerializer(serializers.Serializer):
    date = serializers.DateField()


class EquipmentCalendarSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    today = serializers.DateField()
    days = EquipmentCalendarDaySerializer(many=True)


class EquipmentDayPlanSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    slots = serializers.JSONField()


class DailyEquipmentPlansSerializer(serializers.Serializer):
    date = serializers.CharField()
    equipments = EquipmentDayPlanSerializer(many=True)


class EquipmentSlotInputSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    type = serializers.ChoiceField(choices=SchedulePattern.SlotType.choices)
    value = serializers.JSONField()


class EquipmentPlanInputSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    slots = EquipmentSlotInputSerializer(many=True)


class EquipmentPlansInputSerializer(serializers.Serializer):
    plans = EquipmentPlanInputSerializer(many=True)


class ChangedEquipmentSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    name = serializers.CharField()


class EquipmentPlansSaveResultSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    updated = serializers.IntegerField()
    changed_equipments = ChangedEquipmentSerializer(many=True)
