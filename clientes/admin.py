from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['codigo_cliente', 'nome_femsa', 'nome_mercado', 'valor_tipo', 'empresa']
    list_filter = ['valor_tipo', 'tipo_equipamento', 'empresa']
    search_fields = ['codigo_cliente', 'nome_femsa', 'nome_mercado']
