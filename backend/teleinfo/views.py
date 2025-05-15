from django.core.cache import cache
from django.http import JsonResponse


def teleinfo_data(request):
    """Return the latest Teleinfo data as JSON."""
    data = cache.get("teleinfo_data", {"created": None, "last_saved_at": None})
    sorted_data = dict(sorted(data.items()))
    return JsonResponse(sorted_data)
