"""Views CRUD para Veículo."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import OperacionalMixin
from .models import Veiculo
from .forms import VeiculoForm
from .services import filtrar_veiculos


class VeiculoListView(OperacionalMixin, ListView):
    model = Veiculo
    template_name = 'veiculos/lista.html'
    context_object_name = 'veiculos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related('motorista')
        return filtrar_veiculos(
            qs,
            q=self.request.GET.get('q', '').strip(),
            status=self.request.GET.get('status', ''),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Veículos'
        ctx['subtitulo'] = 'Gerencie a frota de veículos'
        ctx['q'] = self.request.GET.get('q', '')
        ctx['status_filtro'] = self.request.GET.get('status', '')
        return ctx


class VeiculoCreateView(OperacionalMixin, CreateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('veiculos:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, 'Veículo cadastrado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Veículo'
        return ctx


class VeiculoUpdateView(OperacionalMixin, UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'veiculos/form.html'
    success_url = reverse_lazy('veiculos:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Veículo atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Veículo'
        return ctx


class VeiculoDeleteView(OperacionalMixin, DeleteView):
    model = Veiculo
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('veiculos:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Veículo'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('veiculos:lista')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Veículo excluído com sucesso!')
        return super().form_valid(form)
