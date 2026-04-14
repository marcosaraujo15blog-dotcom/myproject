from django.urls import path
from . import views

app_name = 'motoristas'

urlpatterns = [
    path('', views.MotoristaListView.as_view(), name='lista'),
    path('novo/', views.MotoristaCreateView.as_view(), name='criar'),
    path('<str:pk>/editar/', views.MotoristaUpdateView.as_view(), name='editar'),
    path('<str:pk>/excluir/', views.MotoristaDeleteView.as_view(), name='excluir'),
]
