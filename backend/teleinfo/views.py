from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def teleinfo_monitor(request):
    """Render the complete Teleinfo monitor page."""
    data = cache.get("teleinfo_data", {"created": None, "last_saved_at": None})
    sorted_data = dict(sorted(data.items()))
    return render(request, "teleinfo_monitor.html", {"data": sorted_data})
