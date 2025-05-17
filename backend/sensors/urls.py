from django.urls import path
from . import views

urlpatterns = [
    path("data/", views.sensors_data, name="sensors_data"),
]
