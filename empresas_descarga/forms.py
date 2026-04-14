"""Formulários para EmpresaDescarga."""

from django import forms
from .models import EmpresaDescarga


class EmpresaDescargaForm(forms.ModelForm):
    class Meta:
        model = EmpresaDescarga
        fields = ['cnpj_cpf', 'nome', 'nome_fantasia', 'telefone']
        widgets = {
            'cnpj_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0001-00 ou 000.000.000-00',
            }),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
        }
