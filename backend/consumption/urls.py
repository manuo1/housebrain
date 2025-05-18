from django.urls import path
from . import views

urlpatterns = [
    path("data/<str:date>/", views.consumption, name="consumption"),
]
