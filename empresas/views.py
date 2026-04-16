"""Views de CRUD para Empresa (somente superusuário do sistema)."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import SuperuserMixin
from .models import Empresa
from .forms import EmpresaForm


class EmpresaListView(SuperuserMixin, ListView):
    model = Empresa
    template_name = 'empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Empresas'
        return ctx


class EmpresaCreateView(SuperuserMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa cadastrada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nova Empresa'
        return ctx


class EmpresaUpdateView(SuperuserMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Empresa'
        return ctx


class EmpresaDeleteView(SuperuserMixin, DeleteView):
    model = Empresa
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('empresas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa excluída com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Empresa'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('empresas:lista')
        return ctx
