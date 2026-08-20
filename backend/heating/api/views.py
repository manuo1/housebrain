import calendar

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from heating.api.constants import DayStatus
from heating.api.selectors import (
    get_daily_heating_plan,
    get_room_names_by_ids,
    invalid_room_ids_in_plans,
)
from heating.api.serializers import (
    DailyHeatingPlanInputSerializer,
    DailyHeatingPlanSerializer,
    HeatingCalendarInputSerializer,
    HeatingCalendarSerializer,
    HeatingPlansInputSerializer,
    HeatingPlansSaveResultSerializer,
)
from heating.api.services import add_day_status
from heating.models import HeatingPattern, RoomHeatingDayPlan


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
            {"year": year, "month": month, "today": today, "days": heating_calendar}
        )
        return Response(serializer.data)


class DailyHeatingPlan(APIView):
    def get(self, request):
        input_serializer = DailyHeatingPlanInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data
        day = params.get("date", timezone.localdate())

        serializer = DailyHeatingPlanSerializer(
            {"date": day, "rooms": get_daily_heating_plan(day)}
        )
        return Response(serializer.data)

    def post(self, request):
        input_serializer = HeatingPlansInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data
        plans = params.get("plans", [])
        changes = {"updated": 0, "created": 0}
        changed_room_ids = set()

        invalid_room_ids = invalid_room_ids_in_plans(plans)

        if invalid_room_ids:
            raise DRFValidationError(f"Invalid room_ids : {invalid_room_ids}")

        for plan in plans:
            # HeatingPattern
            try:
                heating_pattern, _ = HeatingPattern.get_or_create_from_slots(
                    plan["slots"]
                )
            except DjangoValidationError as e:
                raise DRFValidationError(f"Invalid plan ({e}): {plan} ")

            # RoomHeatingDayPlan
            room_heating_day_plan, is_created = (
                RoomHeatingDayPlan.objects.get_or_create(
                    room_id=plan["room_id"],
                    date=plan["date"],
                    defaults={"heating_pattern": heating_pattern},
                )
            )

            if is_created:
                changes["created"] += 1
                changed_room_ids.add(plan["room_id"])
            else:
                if room_heating_day_plan.heating_pattern != heating_pattern:
                    room_heating_day_plan.heating_pattern = heating_pattern
                    room_heating_day_plan.save()
                    changes["updated"] += 1
                    changed_room_ids.add(plan["room_id"])

        room_names = get_room_names_by_ids(changed_room_ids)
        changes["changed_rooms"] = [
            {"id": room_id, "name": room_names[room_id]}
            for room_id in changed_room_ids
            if room_id in room_names
        ]

        output_serializer = HeatingPlansSaveResultSerializer(changes)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
