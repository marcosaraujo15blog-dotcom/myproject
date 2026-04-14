"""
Modelos base abstratos do sistema.

Hierarquia:
    TimeStampedModel  — timestamps de auditoria (created_at, updated_at)
        └── BaseModel — adiciona vínculo com empresa (tenant)

Todos os modelos concretos devem herdar de BaseModel (se possuem empresa)
ou de TimeStampedModel (se não possuem vínculo direto com empresa).

Exemplos:
    class Motorista(BaseModel): ...      # tem empresa
    class Entrega(TimeStampedModel): ... # isolamento via Transporte
    class Empresa(TimeStampedModel): ... # É o tenant, não referencia a si mesma
"""

from django.db import models


class TimeStampedModel(models.Model):
    """
    Modelo base com campos de auditoria temporal.

    Campos:
        created_at — preenchido automaticamente na criação, nunca alterado
        updated_at — atualizado automaticamente em cada save()
    """
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """
    Modelo base para todos os registros com escopo de empresa (multi-tenant).

    Combina auditoria temporal com isolamento por tenant.

    O related_name usa o padrão Django '%(class)ss' que resolve automaticamente
    para o nome plural do model em letras minúsculas:
        Motorista → empresa.motoristas
        Veiculo   → empresa.veiculos
        Transporte → empresa.transportes

    Modelos cujo nome de classe não produz o plural correto devem sobrescrever
    o campo empresa com o related_name explícito (ex.: EmpresaDescarga).
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        verbose_name='Empresa',
    )

    class Meta:
        abstract = True
