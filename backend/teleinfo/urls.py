from django.urls import path
from . import views

urlpatterns = [
    path("data/", views.teleinfo_data, name="teleinfo_data"),
]
