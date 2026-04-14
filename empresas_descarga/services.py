"""Regras de negócio para Empresas de Descarga."""

from django.db.models import Q


def filtrar_empresas_descarga(qs, q=''):
    """Aplica filtro de busca por nome, nome fantasia ou CNPJ/CPF."""
    if q:
        qs = qs.filter(
            Q(nome__icontains=q) |
            Q(nome_fantasia__icontains=q) |
            Q(cnpj_cpf__icontains=q)
        )
    return qs
