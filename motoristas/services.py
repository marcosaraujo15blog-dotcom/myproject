"""Regras de negócio para Motoristas."""

from django.db.models import Q


def filtrar_motoristas(qs, q='', status=''):
    """Aplica filtros de busca por nome, CPF, CNH e status."""
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) |
            Q(cpf__icontains=q) |
            Q(cnh__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    return qs
