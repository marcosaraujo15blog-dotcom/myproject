"""Regras de negócio para Usuários."""

from django.db.models import Q


def filtrar_usuarios(qs, q=''):
    """Aplica filtro de busca por nome, username ou e-mail."""
    if q:
        qs = qs.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q)
        )
    return qs


def excluir_usuario(usuario):
    """
    Exclui o perfil Usuario e o User Django associado.
    O User não é removido em cascade, portanto precisa ser deletado manualmente.
    """
    user = usuario.user
    usuario.delete()
    user.delete()
