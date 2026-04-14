"""Context processors globais injetados em todos os templates."""


def empresa_context(request):
    """Injeta dados da empresa do usuário logado no contexto dos templates."""
    context = {}
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            usuario = request.user.usuario
            context['empresa_usuario'] = usuario.empresa
            context['tipo_usuario'] = usuario.tipo_usuario
        except Exception:
            pass
    return context
