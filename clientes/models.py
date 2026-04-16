"""Model Cliente com código auto-gerado via signal."""

from django.db import models

from core.models import BaseModel


class Cliente(BaseModel):
    TIPO_EQUIPAMENTO = [
        ('vuc', 'VUC'),
        ('toco', 'Toco'),
        ('truck', 'Truck'),
        ('carreta', 'Carreta'),
        ('bitruck', 'Bitruck'),
        ('outros', 'Outros'),
    ]
    TIPO_DESCARGA = [
        ('manual', 'Manual'),
        ('mecanica', 'Mecânica'),
        ('ambos', 'Manual e Mecânica'),
    ]
    VALOR_TIPO = [
        ('por_palete', 'Por Palete'),
        ('carga_cheia', 'Carga Cheia'),
        ('descarga_direto', 'Descarga Direto'),
    ]

    # Código auto-gerado via signal (ex.: CLI00001)
    codigo_cliente = models.CharField('Código do Cliente', max_length=10, primary_key=True)
    cod_femsa = models.CharField(
        'Cod FEMSA Cliente', max_length=10, blank=True, default=''
    )
    nome_femsa = models.CharField('Nome Femsa / Razão Social', max_length=200)
    nome_mercado = models.CharField('Nome Mercado / Fantasia', max_length=200)
    tipo_equipamento = models.CharField(
        'Tipo de Equipamento', max_length=20, choices=TIPO_EQUIPAMENTO
    )
    tipo_descarga = models.CharField(
        'Tipo de Descarga', max_length=20, choices=TIPO_DESCARGA
    )
    qtd_chapas = models.PositiveSmallIntegerField('Qtd. Chapas', default=0)
    valor_tipo = models.CharField(
        'Tipo de Cobrança', max_length=20, choices=VALOR_TIPO
    )
    valor_pallet = models.DecimalField(
        'Valor por Palete / Frete', max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome_femsa']
        indexes = [
            models.Index(fields=['nome_femsa'], name='cliente_nome_femsa_idx'),
            models.Index(fields=['nome_mercado'], name='cliente_nome_mercado_idx'),
            models.Index(fields=['empresa', 'valor_tipo'], name='cliente_empresa_tipo_idx'),
        ]

    def __str__(self):
        return f'{self.codigo_cliente} — {self.nome_femsa}'

    def calcular_valor(self, pallets):
        """Calcula o valor da entrega baseado no tipo de cobrança."""
        from transportes.services_financeiro import calcular_valor_cliente
        return calcular_valor_cliente(self, pallets)
