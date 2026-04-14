"""Regras de negócio para o módulo Financeiro."""

from django.db.models import Q

from transportes.services_financeiro import calcular_totais_por_status


def filtrar_transportes_financeiro(qs, q='', data_inicio='', data_fim='',
                                   cliente_id='', motorista_id='', status_pag=''):
    """Aplica filtros de busca ao queryset de transportes no contexto financeiro."""
    if q:
        qs = qs.filter(
            Q(numero_transporte__icontains=q) |
            Q(motorista__nome__icontains=q)
        )
    if data_inicio:
        qs = qs.filter(data_transporte__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data_transporte__lte=data_fim)
    if cliente_id:
        qs = qs.filter(
            entregas__cliente__codigo_cliente=cliente_id
        ).distinct()
    if motorista_id:
        qs = qs.filter(motorista__cpf=motorista_id)
    if status_pag:
        qs = qs.filter(status_pagamento=status_pag)
    return qs.order_by('-data_transporte')


def calcular_totalizadores(qs):
    """
    Calcula os totais financeiros a partir do queryset filtrado.
    Delega ao serviço financeiro centralizado.
    Retorna dict com total_receber, total_recebido e total_pendente.
    """
    return calcular_totais_por_status(qs)
