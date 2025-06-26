from django.urls import path

from consumption.api.views import ConsumptionByPeriodView
from . import views

urlpatterns = [
    path("indexes/<str:date>/", views.indexes, name="indexes"),
    path("by-period/", ConsumptionByPeriodView.as_view(), name="consumption-by-period"),
]
