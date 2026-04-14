"""Regras de negócio para Clientes."""

from django.db.models import Q


def filtrar_clientes(qs, q=''):
    """Aplica filtro de busca por nome ou código do cliente."""
    if q:
        qs = qs.filter(
            Q(nome_femsa__icontains=q) |
            Q(nome_mercado__icontains=q) |
            Q(codigo_cliente__icontains=q)
        )
    return qs
