from django.contrib import admin
from .models import EmpresaDescarga


@admin.register(EmpresaDescarga)
class EmpresaDescargaAdmin(admin.ModelAdmin):
    list_display = ['cnpj_cpf', 'nome', 'nome_fantasia', 'telefone', 'empresa']
    list_filter = ['empresa']
    search_fields = ['nome', 'nome_fantasia', 'cnpj_cpf']
