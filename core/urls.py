"""URLs do app core (dashboard principal)."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
]
