from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from consumption.utils import (
    build_consumption_data,
    compute_totals,
)
from consumption.models import DailyIndexes

from .serializers import (
    DailyConsumptionQueryParamsSerializer,
    DailyConsumptionOutputSerializer,
)


class DailyConsumptionView(APIView):
    def get(self, request, **kwargs):

        data = request.query_params.copy()
        data["date"] = kwargs.get("date")

        query_serializer = DailyConsumptionQueryParamsSerializer(data=data)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        requested_date = params.get("date")
        step = params.get("step", 1)

        try:
            daily_indexes = DailyIndexes.objects.get(date=requested_date)
        except DailyIndexes.DoesNotExist:
            return Response(
                {"detail": f"No data found for the given date {requested_date}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = {
            "date": requested_date,
            "step": step,
            "data": build_consumption_data(daily_indexes, requested_date, step),
            "totals": compute_totals(requested_date, daily_indexes.values),
        }

        output_serializer = DailyConsumptionOutputSerializer(response_data)

        return Response(output_serializer.data, status=status.HTTP_200_OK)
