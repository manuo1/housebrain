import calendar

from django.utils import timezone
from heating.api.constants import DayStatus
from heating.api.serializers import (
    HeatingCalendarInputSerializer,
    HeatingCalendarSerializer,
)
from heating.api.services import add_day_status
from rest_framework.response import Response
from rest_framework.views import APIView


class HeatingCalendarView(APIView):
    def get(self, request):
        today = timezone.localdate()
        input_serializer = HeatingCalendarInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data
        year = params.get("year", today.year)
        month = params.get("month", today.month)

        cal = calendar.Calendar(firstweekday=0)
        raw_heating_calendar = [
            {"date": date, "status": DayStatus.EMPTY}
            for date in cal.itermonthdates(year, month)
        ]

        heating_calendar = add_day_status(raw_heating_calendar)

        serializer = HeatingCalendarSerializer(
            {
                "year": year,
                "month": month,
                "today": today,
                "days": heating_calendar,
            }
        )
        return Response(serializer.data)
