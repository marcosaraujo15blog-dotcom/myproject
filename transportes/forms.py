"""
Formulários para Transporte e Entrega.
empresa_descarga agora fica em cada Entrega (não mais no Transporte).
"""

from django import forms
from django.forms import inlineformset_factory
from .models import Transporte, Entrega
from motoristas.models import Motorista
from veiculos.models import Veiculo
from clientes.models import Cliente
from empresas_descarga.models import EmpresaDescarga


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = [
            'documento_transporte', 'data_transporte',
            'veiculo', 'motorista',
            'status_transporte', 'status_pagamento', 'cef_pagamento',
            'desconto', 'acrescimo', 'adiantamento', 'frete_terceiro',
        ]
        widgets = {
            'documento_transporte': forms.TextInput(attrs={'class': 'form-control'}),
            'data_transporte': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'veiculo': forms.Select(attrs={'class': 'form-select'}),
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'status_transporte': forms.Select(attrs={'class': 'form-select'}),
            'status_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'cef_pagamento': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '10'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'acrescimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'adiantamento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'frete_terceiro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['veiculo'].queryset = Veiculo.objects.filter(
                empresa=empresa, status='ativo'
            )
            self.fields['motorista'].queryset = Motorista.objects.filter(
                empresa=empresa, status='ativo'
            )


class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['empresa_descarga', 'cliente', 'pallets', 'valor_pallet', 'ordem_entrega']
        widgets = {
            'empresa_descarga': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select entrega-cliente'}),
            'pallets': forms.NumberInput(attrs={
                'class': 'form-control entrega-pallets', 'min': '0'
            }),
            'valor_pallet': forms.NumberInput(attrs={
                'class': 'form-control entrega-valor', 'step': '0.01', 'min': '0'
            }),
            'ordem_entrega': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '3'
            }),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['cliente'].queryset = Cliente.objects.filter(empresa=empresa)
            self.fields['empresa_descarga'].queryset = EmpresaDescarga.objects.filter(
                empresa=empresa
            )
        self.fields['empresa_descarga'].required = False
        self.fields['empresa_descarga'].empty_label = '— Selecione —'


def get_entrega_formset(empresa=None, extra=1):
    """Cria o formset de entregas filtrado por empresa."""
    FormSet = inlineformset_factory(
        Transporte, Entrega,
        form=EntregaForm,
        extra=extra,
        max_num=3,
        validate_max=True,
        can_delete=True,
    )

    class EntregaFormSetComEmpresa(FormSet):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for form in self.forms:
                if empresa:
                    form.fields['cliente'].queryset = Cliente.objects.filter(empresa=empresa)
                    form.fields['empresa_descarga'].queryset = EmpresaDescarga.objects.filter(
                        empresa=empresa
                    )

    return EntregaFormSetComEmpresa
