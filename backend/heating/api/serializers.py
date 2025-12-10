from heating.models import HeatingPattern
from rest_framework import serializers


class HeatingCalendarInputSerializer(serializers.Serializer):
    year = serializers.IntegerField(required=False, min_value=1)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)


class CalendarDaySerializer(serializers.Serializer):
    date = serializers.CharField()
    status = serializers.CharField()


class HeatingCalendarSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    today = serializers.CharField()
    days = CalendarDaySerializer(many=True)


class HeatingSlotSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    value = serializers.CharField()


class DailyRoomPlanSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    name = serializers.CharField()
    slots = HeatingSlotSerializer(many=True)


class DailyHeatingPlanSerializer(serializers.Serializer):
    date = serializers.CharField()
    rooms = DailyRoomPlanSerializer(many=True)


class DailyHeatingPlanInputSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)


class HeatingSlotInputSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    type = serializers.ChoiceField(choices=HeatingPattern.SlotType.choices)
    value = serializers.JSONField()


class RoomHeatingPlanInputSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    slots = HeatingSlotInputSerializer(many=True)


class HeatingPlansInputSerializer(serializers.Serializer):
    plans = RoomHeatingPlanInputSerializer(many=True)
