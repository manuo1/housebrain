from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache


class TeleinfoDataAPIView(APIView):
    def get(self, request):
        data = cache.get("teleinfo_data", {"last_read": None, "last_saved_at": None})
        return Response(data, status=status.HTTP_200_OK)
