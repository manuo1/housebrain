from django.core.cache import cache
from django.http import JsonResponse


def teleinfo_data(request):
    """Return the latest Teleinfo data as JSON."""
    data = cache.get("teleinfo_data", {})
    return JsonResponse(data)
