"""Views CRUD para Motorista."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.mixins import OperacionalMixin
from .models import Motorista
from .forms import MotoristaForm
from .services import filtrar_motoristas


class MotoristaListView(OperacionalMixin, ListView):
    model = Motorista
    template_name = 'motoristas/lista.html'
    context_object_name = 'motoristas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return filtrar_motoristas(
            qs,
            q=self.request.GET.get('q', '').strip(),
            status=self.request.GET.get('status', ''),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Motoristas'
        ctx['subtitulo'] = 'Gerencie os motoristas cadastrados'
        ctx['q'] = self.request.GET.get('q', '')
        ctx['status_filtro'] = self.request.GET.get('status', '')
        return ctx


class MotoristaCreateView(OperacionalMixin, CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motoristas/form.html'
    success_url = reverse_lazy('motoristas:lista')

    def form_valid(self, form):
        form.instance.empresa = self.get_empresa()
        messages.success(self.request, 'Motorista cadastrado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Motorista'
        return ctx


class MotoristaUpdateView(OperacionalMixin, UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'motoristas/form.html'
    success_url = reverse_lazy('motoristas:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Motorista atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Motorista'
        return ctx


class MotoristaDeleteView(OperacionalMixin, DeleteView):
    model = Motorista
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('motoristas:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Motorista'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('motoristas:lista')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Motorista excluído com sucesso!')
        return super().form_valid(form)
