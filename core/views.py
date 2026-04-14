"""Views do core: dashboard principal."""

from django.views.generic import TemplateView

from core.mixins import EmpresaMixin
from .services import obter_dados_dashboard


class DashboardView(EmpresaMixin, TemplateView):
    """Dashboard com resumo operacional e financeiro do dia."""
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(obter_dados_dashboard(self.get_empresa()))
        ctx['titulo'] = 'Dashboard'
        return ctx
