"""
Extensão do modelo User nativo do Django.
Adiciona tipo de usuário e vínculo com empresa.
"""

from django.db import models
from django.contrib.auth.models import User

from core.models import BaseModel


class Usuario(BaseModel):
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('operacional', 'Operacional'),
        ('financeiro', 'Financeiro'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='usuario',
        verbose_name='Usuário'
    )
    tipo_usuario = models.CharField(
        'Tipo de Usuário', max_length=20,
        choices=TIPO_CHOICES, default='operacional'
    )

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['user__first_name']
        indexes = [
            models.Index(fields=['tipo_usuario'], name='usuario_tipo_idx'),
            models.Index(fields=['empresa', 'tipo_usuario'], name='usuario_empresa_tipo_idx'),
        ]

    def __str__(self):
        return f'{self.nome_completo} [{self.get_tipo_usuario_display()}] — {self.empresa}'

    @property
    def nome_completo(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_admin(self):
        return self.tipo_usuario == 'administrador'
