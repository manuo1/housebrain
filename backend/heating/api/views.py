import calendar

from core.utils.date_utils import weekdays_str_to_datetime_weekdays
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from heating.api.constants import DayStatus, DuplicationTypes
from heating.api.mutators import duplicate_heating_plan_with_override
from heating.api.selectors import (
    get_daily_heating_plan,
    get_room_heating_day_plan_data,
    invalid_room_ids,
    invalid_room_ids_in_plans,
)
from heating.api.serializers import (
    DailyHeatingPlanInputSerializer,
    DailyHeatingPlanSerializer,
    HeatingCalendarInputSerializer,
    HeatingCalendarSerializer,
    HeatingPlanDuplicationSerializer,
    HeatingPlansInputSerializer,
)
from heating.api.services import (
    add_day_status,
    error_in_duplication_dates,
    generate_duplication_dates,
)
from heating.models import HeatingPattern, RoomHeatingDayPlan
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
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
            else:
                if room_heating_day_plan.heating_pattern != heating_pattern:
                    room_heating_day_plan.heating_pattern = heating_pattern
                    room_heating_day_plan.save()
                    changes["updated"] += 1

        return Response(changes, status=status.HTTP_201_CREATED)


class HeatingPlanDuplication(APIView):
    def post(self, request):
        input_serializer = HeatingPlanDuplicationSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data

        duplication_type = params["type"]
        source_date = params["source_date"]
        end_date = params["repeat_until"]
        # check dates
        dates_errors = error_in_duplication_dates(
            source_date, end_date, duplication_type
        )
        if dates_errors:
            raise DRFValidationError(f"Invalid dates : {dates_errors}")
        # check rooms
        invalid_ids = invalid_room_ids(params["room_ids"])
        if invalid_ids:
            raise DRFValidationError(f"Invalid room_ids : {invalid_ids}")
        result = 0
        if duplication_type == DuplicationTypes.DAY:
            weekdays = weekdays_str_to_datetime_weekdays(params["weekdays"])
            duplication_dates = generate_duplication_dates(
                source_date, weekdays, end_date
            )
            for room_id, heating_pattern_id in get_room_heating_day_plan_data(
                source_date, params["room_ids"]
            ):
                room_result = duplicate_heating_plan_with_override(
                    room_id, heating_pattern_id, duplication_dates
                )
                result += room_result

        return Response({"created/updated": result}, status=status.HTTP_201_CREATED)
