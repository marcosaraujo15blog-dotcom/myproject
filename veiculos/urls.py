from django.urls import path
from . import views

app_name = 'veiculos'

urlpatterns = [
    path('', views.VeiculoListView.as_view(), name='lista'),
    path('novo/', views.VeiculoCreateView.as_view(), name='criar'),
    path('<str:pk>/editar/', views.VeiculoUpdateView.as_view(), name='editar'),
    path('<str:pk>/excluir/', views.VeiculoDeleteView.as_view(), name='excluir'),
]
