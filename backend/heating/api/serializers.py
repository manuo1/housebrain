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
