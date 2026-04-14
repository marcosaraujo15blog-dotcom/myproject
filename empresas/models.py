"""Model principal da empresa (tenant do sistema SaaS)."""

from django.db import models

from core.models import TimeStampedModel


class Empresa(TimeStampedModel):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('suspenso', 'Suspenso'),
    ]

    nome_empresa = models.CharField('Nome da Empresa', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, unique=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    status = models.CharField(
        'Status', max_length=20, choices=STATUS_CHOICES, default='ativo'
    )

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome_empresa']
        indexes = [
            models.Index(fields=['status'], name='empresa_status_idx'),
            models.Index(fields=['cnpj'], name='empresa_cnpj_idx'),
        ]

    def __str__(self):
        return f'{self.nome_empresa} ({self.cnpj})'
