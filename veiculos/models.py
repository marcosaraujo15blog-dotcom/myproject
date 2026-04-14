"""Model Veiculo com placa como chave primária."""

from django.db import models

from core.models import BaseModel
from motoristas.models import Motorista


class Veiculo(BaseModel):
    TIPO_VINCULO = [
        ('proprio', 'Próprio'),
        ('terceiro', 'Terceiro'),
        ('agregado', 'Agregado'),
    ]
    TIPO_CARROCERIA = [
        ('bau', 'Baú'),
        ('graneleiro', 'Graneleiro'),
        ('frigorifico', 'Frigorífico'),
        ('plataforma', 'Plataforma'),
        ('grade_baixa', 'Grade Baixa'),
        ('sider', 'Sider'),
        ('outros', 'Outros'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
    ]

    placa = models.CharField('Placa', max_length=10, primary_key=True)
    motorista = models.ForeignKey(
        Motorista, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='veiculos', verbose_name='Motorista'
    )
    tipo_vinculo = models.CharField('Tipo de Vínculo', max_length=20, choices=TIPO_VINCULO)
    modelo = models.CharField('Modelo', max_length=100)
    ano = models.PositiveSmallIntegerField('Ano')
    tipo_carroceria = models.CharField(
        'Tipo de Carroceria', max_length=20, choices=TIPO_CARROCERIA
    )
    capacidade_carga = models.DecimalField(
        'Capacidade de Carga (kg)', max_digits=10, decimal_places=2
    )
    qtd_palete = models.PositiveSmallIntegerField('Qtd. de Paletes')
    status = models.CharField(
        'Status', max_length=15, choices=STATUS_CHOICES, default='ativo'
    )

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['placa']
        indexes = [
            models.Index(fields=['status'], name='veiculo_status_idx'),
            models.Index(fields=['modelo'], name='veiculo_modelo_idx'),
            models.Index(fields=['empresa', 'status'], name='veiculo_empresa_status_idx'),
        ]

    def __str__(self):
        return f'{self.placa} — {self.modelo} ({self.get_status_display()})'
