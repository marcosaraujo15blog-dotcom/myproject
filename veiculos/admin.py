from django.contrib import admin
from .models import Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'modelo', 'tipo_vinculo', 'motorista', 'status', 'empresa']
    list_filter = ['status', 'tipo_vinculo', 'empresa']
    search_fields = ['placa', 'modelo']
