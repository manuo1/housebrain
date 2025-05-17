from django.core.cache import cache
from django.http import JsonResponse


def sensors_data(request):
    """Return the latest sensors data as JSON."""
    data = cache.get("sensors_data", {"no": "data"})
    sorted_data = dict(sorted(data.items()))
    return JsonResponse(sorted_data)
