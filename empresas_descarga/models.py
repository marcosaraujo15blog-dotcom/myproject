"""Model EmpresaDescarga (empresa responsável pela descarga)."""

from django.db import models

from core.models import BaseModel


class EmpresaDescarga(BaseModel):
    # Sobrescreve o campo empresa herdado de BaseModel para usar o
    # related_name correto, pois '%(class)ss' geraria 'empresadescargass'.
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.PROTECT,
        related_name='empresas_descarga',
        verbose_name='Empresa',
    )

    cnpj_cpf = models.CharField('CNPJ / CPF', max_length=18, unique=True)
    nome = models.CharField('Razão Social / Nome', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)

    class Meta:
        verbose_name = 'Empresa de Descarga'
        verbose_name_plural = 'Empresas de Descarga'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome'], name='empdescar_nome_idx'),
            models.Index(fields=['cnpj_cpf'], name='empdescar_cnpj_cpf_idx'),
            models.Index(fields=['empresa'], name='empdescar_empresa_idx'),
        ]

    def __str__(self):
        display = self.nome_fantasia or self.nome
        return f'{display} ({self.cnpj_cpf})'
