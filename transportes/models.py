"""
Models de Transporte e Entrega.

- Transporte herda BaseModel (empresa + timestamps).
- Entrega herda TimeStampedModel — o isolamento por empresa é garantido
  via Transporte; não há FK direta para Empresa.
- O número do transporte é gerado automaticamente via signal (TR00001).
"""

from django.db import models
from django.utils import timezone

from core.models import BaseModel, TimeStampedModel
from motoristas.models import Motorista
from veiculos.models import Veiculo
from clientes.models import Cliente
from empresas_descarga.models import EmpresaDescarga


class Transporte(BaseModel):
    STATUS_TRANSPORTE = [
        ('programado', 'Programado'),
        ('em_andamento', 'Em Andamento'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    STATUS_PAGAMENTO = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]

    numero_transporte = models.CharField(
        'Nº Transporte', max_length=10, unique=True, editable=False
    )
    documento_transporte = models.CharField(
        'Documento', max_length=50, blank=True
    )
    data_transporte = models.DateField(
        'Data do Transporte', default=timezone.localdate
    )
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.PROTECT,
        related_name='transportes', verbose_name='Veículo'
    )
    motorista = models.ForeignKey(
        Motorista, on_delete=models.PROTECT,
        related_name='transportes', verbose_name='Motorista'
    )
    status_transporte = models.CharField(
        'Status', max_length=20,
        choices=STATUS_TRANSPORTE, default='programado'
    )
    status_pagamento = models.CharField(
        'Status Pagamento', max_length=20,
        choices=STATUS_PAGAMENTO, default='pendente'
    )
    cef_pagamento = models.CharField(
        'CEF - Pagamento', max_length=10, blank=True, default=''
    )
    # Campos financeiros
    desconto = models.DecimalField(
        'Desconto (R$)', max_digits=10, decimal_places=2, default=0
    )
    acrescimo = models.DecimalField(
        'Acréscimo (R$)', max_digits=10, decimal_places=2, default=0
    )
    adiantamento = models.DecimalField(
        'Adiantamento (R$)', max_digits=10, decimal_places=2, default=0
    )
    frete_terceiro = models.DecimalField(
        'Frete Terceiro (R$)', max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = 'Transporte'
        verbose_name_plural = 'Transportes'
        ordering = ['-data_transporte', '-numero_transporte']
        indexes = [
            models.Index(fields=['data_transporte'], name='transp_data_idx'),
            models.Index(fields=['status_transporte'], name='transp_status_idx'),
            models.Index(fields=['status_pagamento'], name='transp_status_pag_idx'),
            models.Index(
                fields=['empresa', 'data_transporte'],
                name='transp_empresa_data_idx',
            ),
            models.Index(
                fields=['empresa', 'status_pagamento'],
                name='transp_empresa_pag_idx',
            ),
        ]

    def __str__(self):
        return (
            f'{self.numero_transporte} — {self.motorista.nome} '
            f'({self.data_transporte:%d/%m/%Y})'
        )

    @property
    def total_entregas(self):
        """Subtotal das entregas — delega ao serviço financeiro centralizado."""
        from .services_financeiro import calcular_total_entregas
        return calcular_total_entregas(self)

    @property
    def total_pallets(self):
        """Total de pallets de todas as entregas."""
        return sum(e.pallets for e in self.entregas.all())

    @property
    def qtd_entregas(self):
        return self.entregas.count()

    @property
    def total_final(self):
        """Total financeiro final — delega ao serviço financeiro centralizado."""
        from .services_financeiro import calcular_total_transporte
        return calcular_total_transporte(self)


class Entrega(TimeStampedModel):
    """
    Entrega individual dentro de um Transporte.

    Herda TimeStampedModel (sem empresa direta).
    O isolamento por empresa é garantido via Transporte.
    """
    transporte = models.ForeignKey(
        Transporte, on_delete=models.CASCADE,
        related_name='entregas', verbose_name='Transporte'
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT,
        related_name='entregas', verbose_name='Cliente'
    )
    # Empresa de descarga por entrega — cada entrega pode ter a sua
    empresa_descarga = models.ForeignKey(
        EmpresaDescarga, on_delete=models.PROTECT,
        related_name='entregas', verbose_name='Empresa de Descarga',
        null=True, blank=True
    )
    pallets = models.PositiveSmallIntegerField('Qtd. Pallets', default=0)
    valor_pallet = models.DecimalField(
        'Valor por Palete (R$)', max_digits=10, decimal_places=2
    )
    valor_total = models.DecimalField(
        'Valor Total (R$)', max_digits=10, decimal_places=2, default=0
    )
    ordem_entrega = models.PositiveSmallIntegerField('Ordem', default=1)

    class Meta:
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        ordering = ['ordem_entrega']
        indexes = [
            models.Index(fields=['transporte', 'ordem_entrega'], name='entrega_transp_ordem_idx'),
            models.Index(fields=['cliente'], name='entrega_cliente_idx'),
        ]

    def __str__(self):
        return (
            f'Entrega {self.ordem_entrega} — {self.cliente.nome_femsa} '
            f'({self.transporte.numero_transporte})'
        )

    def save(self, *args, **kwargs):
        from .services_financeiro import calcular_valor_entrega
        self.valor_total = calcular_valor_entrega(self)
        super().save(*args, **kwargs)
