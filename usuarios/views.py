"""Views de autenticação e gestão de usuários."""

from django.contrib.auth import views as auth_views
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from core.mixins import AdminMixin
from .models import Usuario
from .forms import LoginForm, UsuarioCreateForm, UsuarioUpdateForm
from .services import filtrar_usuarios, excluir_usuario


class LoginView(auth_views.LoginView):
    """Tela de login customizada."""
    form_class = LoginForm
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = '/usuarios/login/'


class UsuarioListView(AdminMixin, ListView):
    model = Usuario
    template_name = 'usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        empresa = self.get_empresa()
        qs = Usuario.objects.select_related('user', 'empresa')
        if empresa:
            qs = qs.filter(empresa=empresa)
        return filtrar_usuarios(qs, q=self.request.GET.get('q', '').strip())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Usuários'
        ctx['subtitulo'] = 'Gerencie os usuários do sistema'
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class UsuarioCreateView(AdminMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreateForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Novo Usuário'
        return ctx


class UsuarioUpdateView(AdminMixin, UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'usuarios/form.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.get_empresa()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Editar Usuário'
        return ctx


class UsuarioDeleteView(AdminMixin, DeleteView):
    model = Usuario
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('usuarios:lista')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Excluir Usuário'
        ctx['objeto'] = str(self.object)
        ctx['voltar_url'] = reverse_lazy('usuarios:lista')
        return ctx

    def form_valid(self, form):
        excluir_usuario(self.object)
        messages.success(self.request, 'Usuário excluído com sucesso!')
        return redirect(self.success_url)
