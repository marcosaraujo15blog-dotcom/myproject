from django.contrib import admin
from .models import Transporte, Entrega


class EntregaInline(admin.TabularInline):
    model = Entrega
    extra = 1
    max_num = 3
    fields = ['ordem_entrega', 'empresa_descarga', 'cliente', 'pallets', 'valor_pallet', 'valor_total']
    readonly_fields = ['valor_total']


@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = [
        'numero_transporte', 'data_transporte', 'motorista',
        'veiculo', 'status_transporte', 'status_pagamento', 'empresa'
    ]
    list_filter = ['status_transporte', 'status_pagamento', 'empresa']
    search_fields = ['numero_transporte', 'documento_transporte', 'motorista__nome']
    inlines = [EntregaInline]


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ['transporte', 'ordem_entrega', 'empresa_descarga', 'cliente', 'pallets', 'valor_total']
    list_filter = ['empresa_descarga', 'cliente__empresa']
