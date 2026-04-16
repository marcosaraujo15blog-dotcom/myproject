"""Formulários para Cliente."""

from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'cod_femsa', 'nome_femsa', 'nome_mercado', 'tipo_equipamento',
            'tipo_descarga', 'qtd_chapas', 'valor_tipo', 'valor_pallet',
        ]
        widgets = {
            'cod_femsa': forms.TextInput(attrs={
                'class': 'form-control', 'maxlength': '10',
                'placeholder': 'Ex.: 1234567890',
            }),
            'nome_femsa': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_mercado': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_equipamento': forms.Select(attrs={'class': 'form-select'}),
            'tipo_descarga': forms.Select(attrs={'class': 'form-select'}),
            'qtd_chapas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'valor_tipo': forms.Select(attrs={'class': 'form-select'}),
            'valor_pallet': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0'
            }),
        }
        labels = {
            'valor_pallet': 'Valor (R$)',
        }
