import logging

from ai.api.serializers import AiHeatingPlanModifyInputSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger("django")


class AiHeatingPlanModifyView(APIView):
    def post(self, request):
        serializer = AiHeatingPlanModifyInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        logger.info(
            "AI heating modify request - instruction: %s | plan: %s",
            params["instruction"],
            params["plan"],
        )

        return Response({"status": "ok"}, status=status.HTTP_200_OK)
