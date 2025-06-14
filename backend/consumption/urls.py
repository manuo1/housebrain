from django.urls import path, include
from . import views

urlpatterns = [
    path("indexes/<str:date>/", views.indexes, name="indexes"),
    path("api/", include("consumption.api.urls")),
]
