"""Formulários de criação e edição de usuários."""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario
from empresas.models import Empresa


class LoginForm(AuthenticationForm):
    """Formulário de login estilizado com Bootstrap."""
    username = forms.CharField(
        label='Usuário',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Seu usuário',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Sua senha',
        })
    )


class UsuarioCreateForm(forms.ModelForm):
    """Formulário para criação de novo usuário + perfil."""
    first_name = forms.CharField(
        label='Nome', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Sobrenome', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        label='Login', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 8 caracteres.'
    )

    class Meta:
        model = Usuario
        fields = ['tipo_usuario', 'empresa']
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Administradores de empresa só podem criar usuários na própria empresa
        if empresa:
            self.fields['empresa'].queryset = Empresa.objects.filter(pk=empresa.pk)
            self.fields['empresa'].initial = empresa
            self.fields['empresa'].disabled = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Criar o User do Django primeiro
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data.get('email', ''),
        )
        usuario.user = user
        if commit:
            usuario.save()
        return usuario


class UsuarioUpdateForm(forms.ModelForm):
    """Formulário para edição de usuário existente."""
    first_name = forms.CharField(
        label='Nome', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Sobrenome', max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail', required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        label='Ativo', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Usuario
        fields = ['tipo_usuario', 'empresa']
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'empresa': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['is_active'].initial = self.instance.user.is_active
        if empresa:
            self.fields['empresa'].queryset = Empresa.objects.filter(pk=empresa.pk)
            self.fields['empresa'].disabled = True

    def save(self, commit=True):
        usuario = super().save(commit=False)
        user = usuario.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data.get('email', '')
        user.is_active = self.cleaned_data.get('is_active', True)
        if commit:
            user.save()
            usuario.save()
        return usuario
