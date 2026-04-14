"""Views do módulo Financeiro."""

from django.views.generic import ListView

from core.mixins import FinanceiroMixin
from transportes.models import Transporte
from .services import filtrar_transportes_financeiro, calcular_totalizadores


class FinanceiroListView(FinanceiroMixin, ListView):
    """Tela de Controle Financeiro: visão por transporte."""
    model = Transporte
    template_name = 'financeiro/lista.html'
    context_object_name = 'transportes'
    paginate_by = 20

    def get_queryset(self):
        empresa = self.get_empresa()
        qs = Transporte.objects.select_related(
            'motorista', 'veiculo'
        ).prefetch_related('entregas__cliente')

        if empresa:
            qs = qs.filter(empresa=empresa)

        return filtrar_transportes_financeiro(
            qs,
            q=self.request.GET.get('q', '').strip(),
            data_inicio=self.request.GET.get('data_inicio', ''),
            data_fim=self.request.GET.get('data_fim', ''),
            cliente_id=self.request.GET.get('cliente', ''),
            motorista_id=self.request.GET.get('motorista', ''),
            status_pag=self.request.GET.get('status_pagamento', ''),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_empresa()

        from clientes.models import Cliente
        from motoristas.models import Motorista

        clientes_qs = Cliente.objects.filter(empresa=empresa) if empresa else Cliente.objects.all()
        motoristas_qs = Motorista.objects.filter(empresa=empresa) if empresa else Motorista.objects.all()

        totais = calcular_totalizadores(self.get_queryset())

        ctx.update({
            'titulo': 'Controle Financeiro',
            'subtitulo': 'Gerencie pagamentos, status e acompanhe os totalizadores por transporte',
            'q': self.request.GET.get('q', ''),
            'data_inicio': self.request.GET.get('data_inicio', ''),
            'data_fim': self.request.GET.get('data_fim', ''),
            'cliente_filtro': self.request.GET.get('cliente', ''),
            'motorista_filtro': self.request.GET.get('motorista', ''),
            'status_pagamento_filtro': self.request.GET.get('status_pagamento', ''),
            'clientes': clientes_qs,
            'motoristas': motoristas_qs,
            'status_pagamento_choices': Transporte.STATUS_PAGAMENTO,
            **totais,
        })
        return ctx
