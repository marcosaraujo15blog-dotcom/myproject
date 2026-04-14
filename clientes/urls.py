from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='lista'),
    path('novo/', views.ClienteCreateView.as_view(), name='criar'),
    path('<str:pk>/editar/', views.ClienteUpdateView.as_view(), name='editar'),
    path('<str:pk>/excluir/', views.ClienteDeleteView.as_view(), name='excluir'),
]
