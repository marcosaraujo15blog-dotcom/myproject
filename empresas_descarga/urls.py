from django.urls import path
from . import views

app_name = 'empresas_descarga'

urlpatterns = [
    path('', views.EmpresaDescargaListView.as_view(), name='lista'),
    path('nova/', views.EmpresaDescargaCreateView.as_view(), name='criar'),
    path('<int:pk>/editar/', views.EmpresaDescargaUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.EmpresaDescargaDeleteView.as_view(), name='excluir'),
]
