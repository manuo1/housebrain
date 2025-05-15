from django.core.cache import cache
from django.http import JsonResponse


def teleinfo_data(request):
    """Return the latest Teleinfo data as JSON."""


def teleinfo_view(request):
    data = cache.get("teleinfo_data", {})
    sorted_data = dict(sorted(data.items()))
    return JsonResponse(sorted_data)
