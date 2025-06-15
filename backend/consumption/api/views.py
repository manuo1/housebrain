from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from consumption.utils import compute_watt_hours
from consumption.models import DailyIndexes

from .serializers import (
    DailyConsumptionInputSerializer,
    DailyConsumptionOutputSerializer,
)


class DailyWattHourConsumptionView(APIView):
    def get(self, request, date):
        input_serializer = DailyConsumptionInputSerializer(data={"date": date})
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        date_obj = input_serializer.validated_data["date"]
        try:
            obj = DailyIndexes.objects.get(date=date_obj)
        except DailyIndexes.DoesNotExist:
            return Response(
                {"detail": "No data found for the given date."},
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = DailyConsumptionOutputSerializer(
            {"date": date_obj, "watt_hours": compute_watt_hours(obj.values)}
        )
        return Response(output_serializer.data)
