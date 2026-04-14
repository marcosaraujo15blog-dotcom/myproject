"""Views CRUD para Transporte e tela de Programação."""

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from core.mixins import OperacionalMixin
from .models import Transporte
from .forms import TransporteForm, get_entrega_formset
from .services import filtrar_transportes, salvar_transporte_com_entregas


class TransporteListView(OperacionalMixin, ListView):
    """Tela de Programação de Transportes."""
    model = Transporte
    template_name = 'transportes/lista.html'
    context_object_name = 'transportes'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'veiculo', 'motorista'
        ).prefetch_related('entregas__cliente', 'entregas__empresa_descarga')

        return filtrar_transportes(
            qs,
            q=self.request.GET.get('q', '').strip(),
            data_inicio=self.request.GET.get('data_inicio', ''),
            data_fim=self.request.GET.get('data_fim', ''),
            status=self.request.GET.get('status', ''),
            motorista_id=self.request.GET.get('motorista', ''),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from motoristas.models import Motorista
        empresa = self.get_empresa()
        motoristas_qs = Motorista.objects.filter(empresa=empresa) if empresa else Motorista.objects.all()

        ctx['titulo'] = 'Programação de Transportes'
        ctx['subtitulo'] = 'Gerencie as cargas com filtros de data e status'
        ctx['q'] = self.request.GET.get('q', '')
        ctx['data_inicio'] = self.request.GET.get('data_inicio', '')
        ctx['data_fim'] = self.request.GET.get('data_fim', '')
        ctx['status_filtro'] = self.request.GET.get('status', '')
        ctx['motorista_filtro'] = self.request.GET.get('motorista', '')
        ctx['motoristas'] = motoristas_qs
        ctx['status_choices'] = Transporte.STATUS_TRANSPORTE
        return ctx


class TransporteDetailView(OperacionalMixin, DetailView):
    model = Transporte
    template_name = 'transportes/detail.html'
    context_object_name = 'transporte'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Transporte {self.object.numero_transporte}'
        return ctx


class TransporteCreateView(OperacionalMixin, CreateView):
    model = Transporte
    form_class = TransporteForm
    template_name = 'transportes/form.html'
    success_url = reverse_lazy('transportes:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_empresa()
        EntregaFormSet = get_entrega_formset(empresa=empresa, extra=1)
        if self.request.POST:
            ctx['entrega_formset'] = EntregaFormSet(
                self.request.POST, prefix='entregas'
            )
        else:
            ctx['entrega_formset'] = EntregaFormSet(prefix='entregas')
        ctx['titulo'] = 'Novo Transporte'
        return ctx

    def form_valid(self, form):
        empresa = self.get_empresa()
        form.instance.empresa = empresa
        EntregaFormSet = get_entrega_formset(empresa=empresa, extra=1)
        entrega_formset = EntregaFormSet(self.request.POST, prefix='entregas')

        if entrega_formset.is_valid():
            self.object = salvar_transporte_com_entregas(form, entrega_formset)
            messages.success(
                self.request,
                f'Transporte {self.object.numero_transporte} criado com sucesso!'
            )
            return redirect(self.success_url)
        else:
            # Re-render com erros no formset
            ctx = self.get_context_data(form=form)
            ctx['entrega_formset'] = entrega_formset
            messages.error(self.request, 'Corrija os erros abaixo.')
            return self.render_to_response(ctx)


class TransporteUpdateView(OperacionalMixin, UpdateView):
    model = Transporte
    form_class = TransporteForm
    template_name = 'transportes/form.html'
    success_url = reverse_lazy('transportes:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        empresa = self.get_empresa()
        EntregaFormSet = get_entrega_formset(empresa=empresa, extra=0)
        if self.request.POST:
            ctx['entrega_formset'] = EntregaFormSet(
                self.request.POST, instance=self.object, prefix='entregas'
            )
        else:
            ctx['entrega_formset'] = EntregaFormSet(
                instance=self.object, prefix='entregas'
            )
        ctx['titulo'] = f'Editar Transporte {self.object.numero_transporte}'
        return ctx

    def form_valid(self, form):
        empresa = self.get_empresa()
        EntregaFormSet = get_entrega_formset(empresa=empresa, extra=0)
        entrega_formset = EntregaFormSet(
            self.request.POST, instance=self.object, prefix='entregas'
        )

        if entrega_formset.is_valid():
            self.object = salvar_transporte_com_entregas(form, entrega_formset)
            messages.success(self.request, 'Transporte atualizado com sucesso!')
            return redirect(self.success_url)
        else:
            ctx = self.get_context_data(form=form)
            ctx['entrega_formset'] = entrega_formset
            messages.error(self.request, 'Corrija os erros abaixo.')
            return self.render_to_response(ctx)


class TransporteDeleteView(OperacionalMixin, DeleteView):
    model = Transporte
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('transportes:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Transporte'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('transportes:lista')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Transporte excluído com sucesso!')
        return super().form_valid(form)
