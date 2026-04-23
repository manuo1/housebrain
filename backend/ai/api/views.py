import logging

from ai.api.serializers import AiHeatingPlanModifyInputSerializer
from ai.services.plan_modifier import modify_heating_plan
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("django")


class AiHeatingPlanModifyView(APIView):
    def post(self, request):
        serializer = AiHeatingPlanModifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        modified_plan = modify_heating_plan(
            instruction=params["instruction"],
            plan=params["plan"],
        )

        return Response(modified_plan, status=status.HTTP_200_OK)
