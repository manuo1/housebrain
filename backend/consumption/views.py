from django.http import JsonResponse
from .models import DailyConsumption
from datetime import datetime


def consumption(request, date):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        obj = DailyConsumption.objects.get(date=date_obj)
        return JsonResponse(obj.values, safe=False)
    except DailyConsumption.DoesNotExist:
        return JsonResponse(
            {"error": "Aucune donnée trouvée pour cette date."}, status=404
        )
    except ValueError:
        return JsonResponse(
            {"error": "Format de date invalide. Utiliser YYYY-MM-DD."}, status=400
        )
