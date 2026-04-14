from django.contrib import admin
from .models import Motorista


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cnh', 'categoria_cnh', 'status', 'empresa']
    list_filter = ['status', 'categoria_cnh', 'empresa']
    search_fields = ['nome', 'cpf', 'cnh']
