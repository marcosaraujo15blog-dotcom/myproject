"""Views CRUD para EmpresaDescarga."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import OperacionalMixin
from .models import EmpresaDescarga
from .forms import EmpresaDescargaForm
from .services import filtrar_empresas_descarga


class EmpresaDescargaListView(OperacionalMixin, ListView):
    model = EmpresaDescarga
    template_name = 'empresas_descarga/lista.html'
    context_object_name = 'descargas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return filtrar_empresas_descarga(qs, q=self.request.GET.get('q', '').strip())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Empresas de Descarga'
        ctx['subtitulo'] = 'Gerencie as empresas responsáveis pela descarga'
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class EmpresaDescargaCreateView(OperacionalMixin, CreateView):
    model = EmpresaDescarga
    form_class = EmpresaDescargaForm
    template_name = 'empresas_descarga/form.html'
    success_url = reverse_lazy('empresas_descarga:lista')

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, 'Empresa de descarga cadastrada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nova Empresa de Descarga'
        return ctx


class EmpresaDescargaUpdateView(OperacionalMixin, UpdateView):
    model = EmpresaDescarga
    form_class = EmpresaDescargaForm
    template_name = 'empresas_descarga/form.html'
    success_url = reverse_lazy('empresas_descarga:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa de descarga atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Empresa de Descarga'
        return ctx


class EmpresaDescargaDeleteView(OperacionalMixin, DeleteView):
    model = EmpresaDescarga
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('empresas_descarga:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Empresa de Descarga'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('empresas_descarga:lista')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Empresa de descarga excluída com sucesso!')
        return super().form_valid(form)
