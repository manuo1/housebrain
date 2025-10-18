from django.shortcuts import render
from django.views.decorators.http import require_GET
from teleinfo.utils.cache_teleinfo_data import get_teleinfo_data_in_cache


@require_GET
def teleinfo_data(request):
    """Render the complete Teleinfo monitor page."""
    data = get_teleinfo_data_in_cache()
    sorted_data = dict(sorted(data.items()))
    return render(request, "teleinfo_data.html", {"data": sorted_data})
