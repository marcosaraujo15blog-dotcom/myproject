"""Formulários para Veículo com validação de placa."""

import re
from django import forms
from .models import Veiculo
from motoristas.models import Motorista


def validar_placa(placa):
    """Valida placa no formato antigo (ABC-1234) ou Mercosul (ABC1D23)."""
    placa = placa.upper().replace('-', '').replace(' ', '')
    if not re.match(r'^[A-Z]{3}\d{4}$', placa) and \
       not re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', placa):
        raise forms.ValidationError(
            'Placa inválida. Use o formato ABC-1234 ou ABC1D23 (Mercosul).'
        )
    return placa


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'placa', 'motorista', 'tipo_vinculo', 'modelo', 'ano',
            'tipo_carroceria', 'capacidade_carga', 'qtd_palete', 'status',
        ]
        widgets = {
            'placa': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'ABC-1234 ou ABC1D23',
                'style': 'text-transform:uppercase',
            }),
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'tipo_vinculo': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min': 1990, 'max': 2099}),
            'tipo_carroceria': forms.Select(attrs={'class': 'form-select'}),
            'capacidade_carga': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qtd_palete': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields['motorista'].queryset = Motorista.objects.filter(
                empresa=empresa, status='ativo'
            )

    def clean_placa(self):
        return validar_placa(self.cleaned_data.get('placa', ''))
