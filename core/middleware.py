"""
Middleware para garantir que usuários autenticados só acessem
dados da sua própria empresa (segurança multiempresa).
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class EmpresaMiddleware:
    """
    Verifica se o usuário autenticado possui empresa associada.
    Redireciona para login se não tiver perfil configurado.
    """
    ROTAS_LIBERADAS = [
        '/usuarios/login/',
        '/usuarios/logout/',
        '/admin/',
        '/static/',
        '/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # Verificar se está em rota liberada
            path = request.path
            liberada = any(path.startswith(r) for r in self.ROTAS_LIBERADAS)

            if not liberada:
                try:
                    # Verificar se tem perfil de usuário com empresa
                    _ = request.user.usuario.empresa
                except Exception:
                    messages.error(
                        request,
                        'Seu usuário não possui empresa associada. '
                        'Contate o administrador.'
                    )
                    return redirect(reverse('usuarios:login'))

        response = self.get_response(request)
        return response
