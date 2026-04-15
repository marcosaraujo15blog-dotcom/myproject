"""Views CRUD para Cliente."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

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


@method_decorator(login_required, name='dispatch')
class ClienteInfoView(View):
    """
    Endpoint JSON para o formulário de transporte.
    Retorna valor_tipo e valor_pallet do cliente para pré-preencher
    o campo Valor Unit. (R$) quando o tipo for carga_cheia ou descarga_direto.
    Respeita isolamento por empresa.
    """

    def get(self, request, pk):
        # Superusuários veem todos; usuários normais só da própria empresa
        if request.user.is_superuser:
            cliente = get_object_or_404(Cliente, pk=pk)
        else:
            empresa = request.user.usuario.empresa
            cliente = get_object_or_404(Cliente, pk=pk, empresa=empresa)

        return JsonResponse({
            'valor_tipo': cliente.valor_tipo,
            'valor_pallet': str(cliente.valor_pallet),
        })
