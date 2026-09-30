import calendar
from dataclasses import dataclass

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from equipment.models import WaterHeater
from planning.api.selectors import (
    get_equipment_day_plans,
    get_equipment_names_by_type_and_ids,
    get_schedulable_equipment_config,
    invalid_equipment_refs_in_plans,
)
from planning.api.serializers import (
    DailyEquipmentPlanInputSerializer,
    DailyEquipmentPlansSerializer,
    EquipmentCalendarInputSerializer,
    EquipmentCalendarSerializer,
    EquipmentPlansInputSerializer,
    EquipmentPlansSaveResultSerializer,
)
from planning.models import SchedulePattern
from water_heater.models import WaterHeaterDayPlan


@dataclass(frozen=True)
class SchedulableEquipment:
    type_name: str
    equipment_dayplan: type
    equipment_model: type


SCHEDULABLE_EQUIPMENTS = [
    SchedulableEquipment(
        type_name="water_heater",
        equipment_dayplan=WaterHeaterDayPlan,
        equipment_model=WaterHeater,
    ),
]


class EquipmentCalendarView(APIView):
    def get(self, request):
        today = timezone.localdate()
        input_serializer = EquipmentCalendarInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data
        year = params.get("year", today.year)
        month = params.get("month", today.month)

        cal = calendar.Calendar(firstweekday=0)
        days = [{"date": date} for date in cal.itermonthdates(year, month)]

        serializer = EquipmentCalendarSerializer(
            {"year": year, "month": month, "today": today, "days": days}
        )
        return Response(serializer.data)


class DailyEquipmentPlanView(APIView):
    def get(self, request):
        input_serializer = DailyEquipmentPlanInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data
        day = params.get("date", timezone.localdate())

        serializer = DailyEquipmentPlansSerializer(
            {
                "date": day,
                "equipments": get_equipment_day_plans(SCHEDULABLE_EQUIPMENTS, day),
            }
        )
        return Response(serializer.data)

    def post(self, request):
        input_serializer = EquipmentPlansInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        plans = input_serializer.validated_data["plans"]

        invalid_refs = invalid_equipment_refs_in_plans(SCHEDULABLE_EQUIPMENTS, plans)
        if invalid_refs:
            raise DRFValidationError(f"Invalid equipment refs: {invalid_refs}")

        changes = {"created": 0, "updated": 0}
        changed_refs: set[tuple[str, int]] = set()

        for plan in plans:
            config = get_schedulable_equipment_config(
                SCHEDULABLE_EQUIPMENTS, plan["type"]
            )

            try:
                schedule_pattern, _ = SchedulePattern.get_or_create_from_slots(
                    plan["slots"]
                )
            except DjangoValidationError as e:
                raise DRFValidationError(f"Invalid plan ({e}): {plan}")

            day_plan, is_created = config.equipment_dayplan.objects.get_or_create(
                equipment_id=plan["id"],
                date=plan["date"],
                defaults={"schedule_pattern": schedule_pattern},
            )

            if is_created:
                changes["created"] += 1
                changed_refs.add((plan["type"], plan["id"]))
            elif day_plan.schedule_pattern != schedule_pattern:
                day_plan.schedule_pattern = schedule_pattern
                day_plan.save()
                changes["updated"] += 1
                changed_refs.add((plan["type"], plan["id"]))

        names = get_equipment_names_by_type_and_ids(SCHEDULABLE_EQUIPMENTS, changed_refs)
        changes["changed_equipments"] = [
            {"type": type_name, "id": equipment_id, "name": names[(type_name, equipment_id)]}
            for (type_name, equipment_id) in changed_refs
            if (type_name, equipment_id) in names
        ]

        output_serializer = EquipmentPlansSaveResultSerializer(changes)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
