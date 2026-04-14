"""Regras de negócio para o Dashboard e utilitários globais."""

from django.utils import timezone

from transportes.services_financeiro import calcular_totais_por_status


def obter_dados_dashboard(empresa):
    """
    Retorna um dict com os dados agregados para o Dashboard.
    Recebe a empresa do usuário logado (None se superuser).
    """
    from transportes.models import Transporte

    qs = Transporte.objects.prefetch_related('entregas').select_related(
        'motorista', 'veiculo'
    )
    if empresa:
        qs = qs.filter(empresa=empresa)

    hoje = timezone.localdate()
    totais = calcular_totais_por_status(qs)

    return {
        'transportes_hoje': qs.filter(data_transporte=hoje).count(),
        'transportes_andamento': qs.filter(status_transporte='em_andamento').count(),
        'total_pendente': totais['total_pendente'],
        'total_faturamento': totais['total_recebido'],
        'ultimos_transportes': list(qs.order_by('-data_transporte')[:5]),
    }
