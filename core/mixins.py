"""
Mixins reutilizáveis para as views do sistema.
Garantem isolamento por empresa e controle de acesso por tipo de usuário.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import redirect
from django.contrib import messages


class EmpresaQuerySetMixin:
    """
    Mixin de isolamento de dados por empresa.

    Responsabilidade única: garantir que nenhum usuário acesse dados
    de outra empresa, tanto em listagens quanto em operações por objeto.

    - get_queryset(): filtra automaticamente pela empresa do usuário.
    - get_object(): verificação secundária (belt-and-suspenders) que
      levanta Http404 se o objeto recuperado pertencer a outra empresa,
      mesmo que get_queryset() tenha sido sobrescrito sem chamar super().

    Deve ser combinado com LoginRequiredMixin (já feito via EmpresaMixin).
    """

    def get_empresa(self):
        """Retorna a empresa do usuário logado. None para superusuários."""
        if self.request.user.is_superuser:
            return None
        return self.request.user.usuario.empresa

    def get_queryset(self):
        """Filtra o queryset restringindo à empresa do usuário logado."""
        qs = super().get_queryset()
        empresa = self.get_empresa()
        if empresa:
            qs = qs.filter(empresa=empresa)
        return qs

    def get_object(self, queryset=None):
        """
        Verifica o isolamento no nível do objeto.
        Mesmo que get_queryset() já garanta o filtro, esta verificação
        explícita protege views que sobrescrevem get_queryset() diretamente.
        """
        obj = super().get_object(queryset)
        empresa = self.get_empresa()
        if empresa and hasattr(obj, 'empresa') and obj.empresa != empresa:
            raise Http404
        return obj


class EmpresaMixin(LoginRequiredMixin, EmpresaQuerySetMixin):
    """
    Mixin base que combina:
    - Autenticação obrigatória (LoginRequiredMixin)
    - Isolamento por empresa (EmpresaQuerySetMixin)
    - Atribuição automática de empresa ao salvar formulários
    """
    login_url = '/usuarios/login/'

    def form_valid(self, form):
        """Associa automaticamente a empresa ao salvar o objeto."""
        empresa = self.get_empresa()
        if empresa and isinstance(form, ModelForm) and hasattr(form.instance, 'empresa'):
            form.instance.empresa = empresa
        return super().form_valid(form)


class AdminMixin(EmpresaMixin):
    """Restringe acesso somente a administradores."""
    tipos_permitidos = ['administrador']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            try:
                tipo = request.user.usuario.tipo_usuario
                if tipo not in self.tipos_permitidos:
                    messages.error(request, 'Acesso restrito. Permissão insuficiente.')
                    return redirect('/')
            except Exception:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class OperacionalMixin(EmpresaMixin):
    """Permite acesso a administradores e operacionais."""
    tipos_permitidos = ['administrador', 'operacional']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            try:
                tipo = request.user.usuario.tipo_usuario
                if tipo not in self.tipos_permitidos:
                    messages.error(request, 'Acesso restrito. Permissão insuficiente.')
                    return redirect('/')
            except Exception:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class FinanceiroMixin(EmpresaMixin):
    """Permite acesso a administradores e financeiros."""
    tipos_permitidos = ['administrador', 'financeiro']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            try:
                tipo = request.user.usuario.tipo_usuario
                if tipo not in self.tipos_permitidos:
                    messages.error(request, 'Acesso restrito. Permissão insuficiente.')
                    return redirect('/')
            except Exception:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SuperuserMixin(LoginRequiredMixin):
    """Restringe acesso exclusivamente a superusuários (gestão do sistema)."""
    login_url = '/usuarios/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            messages.error(request, 'Acesso restrito ao administrador do sistema.')
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)
