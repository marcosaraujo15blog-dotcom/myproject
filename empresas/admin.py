from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome_empresa', 'cnpj', 'status', 'created_at']
    search_fields = ['nome_empresa', 'cnpj']
    list_filter = ['status']
