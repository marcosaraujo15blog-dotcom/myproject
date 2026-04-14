from django.urls import path
from . import views

app_name = 'transportes'

urlpatterns = [
    path('', views.TransporteListView.as_view(), name='lista'),
    path('novo/', views.TransporteCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.TransporteDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.TransporteUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.TransporteDeleteView.as_view(), name='excluir'),
]
