"""Model Motorista com CPF como chave primária."""

from django.db import models

from core.models import BaseModel


class Motorista(BaseModel):
    CATEGORIA_CNH = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'),
        ('D', 'D'), ('E', 'E'),
        ('AB', 'AB'), ('AC', 'AC'), ('AD', 'AD'), ('AE', 'AE'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    ]

    cpf = models.CharField('CPF', max_length=14, primary_key=True)
    nome = models.CharField('Nome Completo', max_length=200)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    cnh = models.CharField('Nº CNH', max_length=20, unique=True)
    categoria_cnh = models.CharField('Categoria CNH', max_length=5, choices=CATEGORIA_CNH)
    data_vencimento_cnh = models.DateField('Vencimento CNH')
    data_expedicao_cnh = models.DateField('Expedição CNH')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    status = models.CharField(
        'Status', max_length=10, choices=STATUS_CHOICES, default='ativo'
    )

    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome'], name='motorista_nome_idx'),
            models.Index(fields=['status'], name='motorista_status_idx'),
            models.Index(fields=['empresa', 'status'], name='motorista_empresa_status_idx'),
        ]

    def __str__(self):
        return f'{self.nome} (CPF: {self.cpf})'
