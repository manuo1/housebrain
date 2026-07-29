from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from teleinfo.constants import TeleinfoLabel
from teleinfo.utils.cache_teleinfo_data import get_teleinfo_data_in_cache


class TeleinfoDataAPIView(APIView):
    def get(self, request):
        data = get_teleinfo_data_in_cache()
        # ADCO (adresse du compteur) n'est jamais exposé : cet endpoint est public.
        data = {key: value for key, value in data.items() if key != TeleinfoLabel.ADCO}
        return Response(data, status=status.HTTP_200_OK)
