"""URLs raiz do projeto ERP Logística."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('empresas/', include('empresas.urls')),
    path('motoristas/', include('motoristas.urls')),
    path('veiculos/', include('veiculos.urls')),
    path('clientes/', include('clientes.urls')),
    path('descargas/', include('empresas_descarga.urls')),
    path('transportes/', include('transportes.urls')),
    path('financeiro/', include('financeiro.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
