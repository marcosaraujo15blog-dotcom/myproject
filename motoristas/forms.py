"""Formulários e validações para Motorista."""

import re
from django import forms
from .models import Motorista


def validar_cpf(cpf):
    """Valida CPF brasileiro."""
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise forms.ValidationError('CPF inválido.')
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            raise forms.ValidationError('CPF inválido.')
    return cpf


class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = [
            'cpf', 'nome', 'data_nascimento', 'cnh', 'categoria_cnh',
            'data_vencimento_cnh', 'data_expedicao_cnh', 'telefone', 'status',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '000.000.000-00',
                'data-mask': '000.000.000-00',
            }),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'cnh': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria_cnh': forms.Select(attrs={'class': 'form-select'}),
            'data_vencimento_cnh': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'data_expedicao_cnh': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        return validar_cpf(cpf)
