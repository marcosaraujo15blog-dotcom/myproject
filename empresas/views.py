"""Views de CRUD para Empresa (somente superusuário/admin)."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Empresa
from .forms import EmpresaForm


class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20
    login_url = '/usuarios/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Empresas'
        return ctx


class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')
    login_url = '/usuarios/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Nova Empresa'
        return ctx


class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'empresas/form.html'
    success_url = reverse_lazy('empresas:lista')
    login_url = '/usuarios/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Empresa'
        return ctx


class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('empresas:lista')
    login_url = '/usuarios/login/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Empresa'
        ctx['objeto'] = self.object
        ctx['voltar_url'] = reverse_lazy('empresas:lista')
        return ctx
