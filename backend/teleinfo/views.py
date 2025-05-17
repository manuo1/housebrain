from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def teleinfo_data(request):
    """Render the complete Teleinfo monitor page."""
    data = cache.get("teleinfo_data", {"last_read": None, "last_saved_at": None})
    sorted_data = dict(sorted(data.items()))
    return render(request, "teleinfo_data.html", {"data": sorted_data})
