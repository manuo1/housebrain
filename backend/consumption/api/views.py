from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from consumption.constants import ConsumptionPeriod
from consumption.selectors import get_daily_indexes
from consumption.utils import (
    build_consumption_data,
    compute_totals_for_a_day,
    compute_totals_for_multiple_periods,
    get_consumption_by_day_data,
    get_consumption_by_month_data,
    get_consumption_by_week_data,
    get_end_date_according_to_period,
    get_start_date_according_to_period,
)
from consumption.models import DailyIndexes

from .serializers import (
    ConsumptionByPeriodQueryParamsSerializer,
    ConsumptionByPeriodResponseSerializer,
    DailyConsumptionQueryParamsSerializer,
    DailyConsumptionOutputSerializer,
)
from django.utils import timezone


class DailyConsumptionView(APIView):
    def get(self, request):

        query_serializer = DailyConsumptionQueryParamsSerializer(
            data=request.query_params
        )
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
            "totals": compute_totals_for_a_day(requested_date, daily_indexes.values),
        }

        output_serializer = DailyConsumptionOutputSerializer(response_data)

        return Response(output_serializer.data, status=status.HTTP_200_OK)


class ConsumptionByPeriodView(APIView):
    def get(self, request):
        serializer = ConsumptionByPeriodQueryParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        requested_start_date = params.get("start_date", timezone.now().date())
        requested_end_date = params.get("end_date", timezone.now().date())
        period = params.get("period", "day")
        start_date = get_start_date_according_to_period(requested_start_date, period)
        end_date = get_end_date_according_to_period(requested_end_date, period)
        daily_indexes_list = get_daily_indexes(start_date, end_date)
        match period:
            case ConsumptionPeriod.DAY:
                data = get_consumption_by_day_data(
                    start_date, end_date, daily_indexes_list
                )
            case ConsumptionPeriod.WEEK:
                data = get_consumption_by_week_data(
                    start_date, end_date, daily_indexes_list
                )
            case ConsumptionPeriod.MONTH:
                data = get_consumption_by_month_data(
                    start_date, end_date, daily_indexes_list
                )
            case _:
                data = []

        response_data = {
            "start_date": start_date,
            "end_date": end_date,
            "period": period,
            "data": data,
            "totals": compute_totals_for_multiple_periods(data),
        }

        output_serializer = ConsumptionByPeriodResponseSerializer(response_data)

        return Response(output_serializer.data, status=status.HTTP_200_OK)
