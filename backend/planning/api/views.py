from dataclasses import dataclass

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from equipment.models import WaterHeater
from planning.api.selectors import get_equipment_day_plans
from planning.api.serializers import (
    DailyEquipmentPlanInputSerializer,
    DailyEquipmentPlansSerializer,
)
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
