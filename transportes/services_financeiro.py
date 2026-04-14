"""
Centralização de todas as regras de cálculo financeiro do sistema.

Este módulo é o único lugar onde as fórmulas de negócio estão definidas.
Models, services e views devem importar daqui — nunca reimplementar.

Funções públicas:
  calcular_valor_entrega(entrega)         — valor de uma Entrega
  calcular_valor_cliente(cliente, pallets) — valor prévia para um Cliente
  calcular_total_entregas(transporte)     — subtotal das Entregas
  calcular_total_transporte(transporte)   — total final com todos os ajustes
  calcular_totais_por_status(qs)          — agrega totais por status de pagamento
"""

from decimal import Decimal


# ---------------------------------------------------------------------------
# Regra central — única definição da lógica de tipo de cobrança
# ---------------------------------------------------------------------------

def _aplicar_regra_valor(valor_tipo, valor_pallet, pallets):
    """
    Regra primitiva de cálculo de valor por tipo de cobrança.

    Tipos:
      'por_palete'      → valor_pallet × pallets  (cobrança proporcional)
      'carga_cheia'     → valor_pallet             (frete fixo por viagem)
      'descarga_direto' → valor_pallet             (frete fixo por entrega)
    """
    if valor_tipo == 'por_palete':
        return valor_pallet * pallets
    return valor_pallet


# ---------------------------------------------------------------------------
# Cálculo de Entrega
# ---------------------------------------------------------------------------

def calcular_valor_entrega(entrega):
    """
    Retorna o valor total de uma Entrega.

    Lê valor_tipo do cliente associado, valor_pallet e pallets da própria entrega.
    Chamado por Entrega.save() para persistir valor_total automaticamente.
    """
    return _aplicar_regra_valor(
        valor_tipo=entrega.cliente.valor_tipo,
        valor_pallet=entrega.valor_pallet,
        pallets=entrega.pallets,
    )


def calcular_valor_cliente(cliente, pallets):
    """
    Calcula o valor esperado de uma entrega para um Cliente e uma quantidade
    de pallets, sem precisar de uma instância de Entrega.

    Útil para prévia de valores em formulários e relatórios.
    """
    return _aplicar_regra_valor(
        valor_tipo=cliente.valor_tipo,
        valor_pallet=cliente.valor_pallet,
        pallets=pallets,
    )


# ---------------------------------------------------------------------------
# Cálculo de Transporte
# ---------------------------------------------------------------------------

def calcular_total_entregas(transporte):
    """
    Subtotal das Entregas: soma de valor_total de todas as entregas do transporte.

    Depende de que cada Entrega.valor_total já esteja persistido via save().
    Se o queryset de entregas tiver sido prefetchado, não faz queries adicionais.
    """
    return sum(
        (e.valor_total for e in transporte.entregas.all()),
        Decimal('0'),
    )


def calcular_total_transporte(transporte):
    """
    Total financeiro final do Transporte.

    Fórmula:
        total_final = total_entregas
                    − desconto
                    + acrescimo
                    − adiantamento
                    − frete_terceiro

    Todos os campos financeiros têm default=0 no banco, portanto nunca são None.
    """
    return (
        calcular_total_entregas(transporte)
        - transporte.desconto
        + transporte.acrescimo
        - transporte.adiantamento
        - transporte.frete_terceiro
    )


# ---------------------------------------------------------------------------
# Agregação por status de pagamento
# ---------------------------------------------------------------------------

def calcular_totais_por_status(qs):
    """
    Itera o queryset de Transportes UMA vez e acumula totais por status.

    Retorna dict com:
      total_receber  — soma de total_final dos transportes com status 'pendente'
      total_recebido — soma de total_final dos transportes com status 'pago'
      total_pendente — alias de total_receber (mantido para compatibilidade de template)

    Nota: se o queryset já foi prefetchado com 'entregas', nenhuma query
    adicional é executada por transporte dentro de calcular_total_transporte().
    """
    total_receber = Decimal('0')
    total_recebido = Decimal('0')

    for t in qs:
        total = calcular_total_transporte(t)
        if t.status_pagamento == 'pendente':
            total_receber += total
        elif t.status_pagamento == 'pago':
            total_recebido += total

    return {
        'total_receber': total_receber,
        'total_recebido': total_recebido,
        'total_pendente': total_receber,
    }
