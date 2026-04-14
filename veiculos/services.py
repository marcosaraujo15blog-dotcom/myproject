"""Regras de negócio para Veículos."""

from django.db.models import Q


def filtrar_veiculos(qs, q='', status=''):
    """Aplica filtros de busca por placa, modelo, motorista e status."""
    if q:
        qs = qs.filter(
            Q(placa__icontains=q) |
            Q(modelo__icontains=q) |
            Q(motorista__nome__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    return qs
