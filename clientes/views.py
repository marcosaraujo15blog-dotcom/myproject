"""Views CRUD para Cliente."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import OperacionalMixin
from .models import Cliente
from .forms import ClienteForm
from .services import filtrar_clientes


class ClienteListView(OperacionalMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return filtrar_clientes(qs, q=self.request.GET.get('q', '').strip())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Clientes'
        ctx['subtitulo'] = 'Gerencie os clientes cadastrados'
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ClienteCreateView(OperacionalMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Cliente'
        return ctx


class ClienteUpdateView(OperacionalMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Cliente'
        return ctx


class ClienteDeleteView(OperacionalMixin, DeleteView):
    model = Cliente
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('clientes:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Cliente'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('clientes:lista')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Cliente excluído com sucesso!')
        return super().form_valid(form)
