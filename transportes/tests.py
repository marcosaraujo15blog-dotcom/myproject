"""
Testes das regras de cálculo financeiro centralizadas em services_financeiro.

Valida cada função do serviço isoladamente com dados de fixture mínimos.

Para rodar:
    python manage.py test transportes.tests --settings=config.settings
    (defina USE_SQLITE=True no .env)
"""

import datetime
from decimal import Decimal

from django.test import TestCase

from clientes.models import Cliente
from empresas.models import Empresa
from motoristas.models import Motorista
from transportes.models import Entrega, Transporte
from transportes.services_financeiro import (
    _aplicar_regra_valor,
    calcular_total_entregas,
    calcular_total_transporte,
    calcular_totais_por_status,
    calcular_valor_cliente,
    calcular_valor_entrega,
)
from veiculos.models import Veiculo


# ---------------------------------------------------------------------------
# Fixtures helpers
# ---------------------------------------------------------------------------

def _empresa():
    return Empresa.objects.create(nome_empresa='Transportadora Teste', cnpj='99.999.999/0001-99')


def _motorista(empresa):
    return Motorista.objects.create(
        cpf='999.999.999-99',
        nome='Motorista Teste',
        cnh='99999999999',
        categoria_cnh='B',
        data_vencimento_cnh=datetime.date(2030, 1, 1),
        data_expedicao_cnh=datetime.date(2020, 1, 1),
        empresa=empresa,
    )


def _veiculo(empresa, motorista):
    return Veiculo.objects.create(
        placa='TST0T00',
        modelo='Caminhão Teste',
        tipo_vinculo='proprio',
        ano=2022,
        tipo_carroceria='bau',
        capacidade_carga=Decimal('10000'),
        qtd_palete=30,
        empresa=empresa,
        motorista=motorista,
    )


def _cliente(empresa, valor_tipo='por_palete', valor_pallet=Decimal('50')):
    return Cliente.objects.create(
        nome_femsa='Cliente Teste Femsa',
        nome_mercado='Cliente Teste',
        tipo_equipamento='toco',
        tipo_descarga='manual',
        valor_tipo=valor_tipo,
        valor_pallet=valor_pallet,
        empresa=empresa,
    )


def _transporte(empresa, motorista, veiculo, desconto=0, acrescimo=0, adiantamento=0, frete=0):
    return Transporte.objects.create(
        data_transporte=datetime.date.today(),
        motorista=motorista,
        veiculo=veiculo,
        empresa=empresa,
        desconto=Decimal(str(desconto)),
        acrescimo=Decimal(str(acrescimo)),
        adiantamento=Decimal(str(adiantamento)),
        frete_terceiro=Decimal(str(frete)),
    )


def _entrega(transporte, cliente, pallets=10, valor_pallet=None):
    vp = valor_pallet if valor_pallet is not None else cliente.valor_pallet
    return Entrega.objects.create(
        transporte=transporte,
        cliente=cliente,
        pallets=pallets,
        valor_pallet=vp,
        ordem_entrega=1,
    )


# ---------------------------------------------------------------------------
# Testes da regra primitiva
# ---------------------------------------------------------------------------

class AplicarRegraValorTest(TestCase):

    def test_por_palete_multiplica_pallets(self):
        resultado = _aplicar_regra_valor('por_palete', Decimal('50'), 10)
        self.assertEqual(resultado, Decimal('500'))

    def test_por_palete_zero_pallets(self):
        resultado = _aplicar_regra_valor('por_palete', Decimal('50'), 0)
        self.assertEqual(resultado, Decimal('0'))

    def test_carga_cheia_retorna_valor_fixo(self):
        resultado = _aplicar_regra_valor('carga_cheia', Decimal('800'), 30)
        self.assertEqual(resultado, Decimal('800'))

    def test_descarga_direto_retorna_valor_fixo(self):
        resultado = _aplicar_regra_valor('descarga_direto', Decimal('300'), 15)
        self.assertEqual(resultado, Decimal('300'))

    def test_carga_cheia_ignora_quantidade_pallets(self):
        r1 = _aplicar_regra_valor('carga_cheia', Decimal('600'), 1)
        r2 = _aplicar_regra_valor('carga_cheia', Decimal('600'), 100)
        self.assertEqual(r1, r2)


# ---------------------------------------------------------------------------
# Testes de calcular_valor_entrega
# ---------------------------------------------------------------------------

class CalcularValorEntregaTest(TestCase):

    def setUp(self):
        self.empresa = _empresa()
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.transporte = _transporte(self.empresa, self.motorista, self.veiculo)

    def test_por_palete(self):
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('40'))
        entrega = _entrega(self.transporte, cliente, pallets=5)
        # calcular_valor_entrega é chamado no save(); valor_total já estará correto
        self.assertEqual(entrega.valor_total, Decimal('200'))
        # confirmar que a função retorna o mesmo valor
        self.assertEqual(calcular_valor_entrega(entrega), Decimal('200'))

    def test_carga_cheia(self):
        cliente = _cliente(self.empresa, valor_tipo='carga_cheia', valor_pallet=Decimal('1200'))
        entrega = _entrega(self.transporte, cliente, pallets=20)
        self.assertEqual(entrega.valor_total, Decimal('1200'))
        self.assertEqual(calcular_valor_entrega(entrega), Decimal('1200'))

    def test_descarga_direto(self):
        cliente = _cliente(self.empresa, valor_tipo='descarga_direto', valor_pallet=Decimal('350'))
        entrega = _entrega(self.transporte, cliente, pallets=8)
        self.assertEqual(entrega.valor_total, Decimal('350'))
        self.assertEqual(calcular_valor_entrega(entrega), Decimal('350'))

    def test_valor_pallet_da_entrega_prevalece_sobre_cliente(self):
        """
        O valor_pallet pode ser sobrescrito na Entrega (diferente do padrão do cliente).
        calcular_valor_entrega usa o da Entrega, não o do Cliente.
        """
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('50'))
        entrega = _entrega(self.transporte, cliente, pallets=10, valor_pallet=Decimal('70'))
        self.assertEqual(calcular_valor_entrega(entrega), Decimal('700'))

    def test_save_persiste_valor_total(self):
        """Entrega.save() deve chamar o serviço e persistir valor_total."""
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('30'))
        entrega = _entrega(self.transporte, cliente, pallets=4)
        entrega.refresh_from_db()
        self.assertEqual(entrega.valor_total, Decimal('120'))


# ---------------------------------------------------------------------------
# Testes de calcular_valor_cliente
# ---------------------------------------------------------------------------

class CalcularValorClienteTest(TestCase):

    def setUp(self):
        self.empresa = _empresa()

    def test_por_palete(self):
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('60'))
        self.assertEqual(calcular_valor_cliente(cliente, 5), Decimal('300'))

    def test_carga_cheia(self):
        cliente = _cliente(self.empresa, valor_tipo='carga_cheia', valor_pallet=Decimal('900'))
        self.assertEqual(calcular_valor_cliente(cliente, 50), Decimal('900'))

    def test_mesma_regra_que_calcular_valor_entrega(self):
        """calcular_valor_cliente e calcular_valor_entrega devem retornar o mesmo valor."""
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.transporte = _transporte(self.empresa, self.motorista, self.veiculo)
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('80'))
        entrega = _entrega(self.transporte, cliente, pallets=7)
        self.assertEqual(
            calcular_valor_cliente(cliente, 7),
            calcular_valor_entrega(entrega),
        )


# ---------------------------------------------------------------------------
# Testes de calcular_total_entregas
# ---------------------------------------------------------------------------

class CalcularTotalEntregasTest(TestCase):

    def setUp(self):
        self.empresa = _empresa()
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.transporte = _transporte(self.empresa, self.motorista, self.veiculo)

    def test_sem_entregas(self):
        self.assertEqual(calcular_total_entregas(self.transporte), Decimal('0'))

    def test_uma_entrega(self):
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('50'))
        _entrega(self.transporte, cliente, pallets=10)
        self.transporte.refresh_from_db()
        self.assertEqual(calcular_total_entregas(self.transporte), Decimal('500'))

    def test_multiplas_entregas_somadas(self):
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('50'))

        e1 = _entrega(self.transporte, cliente, pallets=10)          # 500
        e2 = Entrega.objects.create(                                  # 300
            transporte=self.transporte, cliente=cliente,
            pallets=6, valor_pallet=Decimal('50'), ordem_entrega=2
        )
        e3 = Entrega.objects.create(                                  # 200 (fixo)
            transporte=self.transporte,
            cliente=_cliente(self.empresa, valor_tipo='carga_cheia', valor_pallet=Decimal('200')),
            pallets=99, valor_pallet=Decimal('200'), ordem_entrega=3
        )

        self.transporte.refresh_from_db()
        self.assertEqual(calcular_total_entregas(self.transporte), Decimal('1000'))

    def test_propriedade_total_entregas_usa_servico(self):
        """Transporte.total_entregas deve retornar o mesmo que calcular_total_entregas."""
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('100'))
        _entrega(self.transporte, cliente, pallets=3)
        self.transporte.refresh_from_db()
        self.assertEqual(self.transporte.total_entregas, calcular_total_entregas(self.transporte))


# ---------------------------------------------------------------------------
# Testes de calcular_total_transporte
# ---------------------------------------------------------------------------

class CalcularTotalTransporteTest(TestCase):

    def setUp(self):
        self.empresa = _empresa()
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)

    def _criar_transporte_com_entrega(self, pallets=10, valor_pallet=Decimal('100'),
                                      desconto=0, acrescimo=0, adiantamento=0, frete=0):
        t = _transporte(self.empresa, self.motorista, self.veiculo,
                        desconto=desconto, acrescimo=acrescimo,
                        adiantamento=adiantamento, frete=frete)
        cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=valor_pallet)
        _entrega(t, cliente, pallets=pallets)
        t.refresh_from_db()
        return t

    def test_sem_ajustes(self):
        # 10 pallets × R$ 100 = R$ 1.000; sem ajustes → R$ 1.000
        t = self._criar_transporte_com_entrega(pallets=10, valor_pallet=Decimal('100'))
        self.assertEqual(calcular_total_transporte(t), Decimal('1000'))

    def test_com_desconto(self):
        # R$ 1.000 − R$ 50 desconto = R$ 950
        t = self._criar_transporte_com_entrega(desconto=50)
        self.assertEqual(calcular_total_transporte(t), Decimal('950'))

    def test_com_acrescimo(self):
        # R$ 1.000 + R$ 30 = R$ 1.030
        t = self._criar_transporte_com_entrega(acrescimo=30)
        self.assertEqual(calcular_total_transporte(t), Decimal('1030'))

    def test_com_adiantamento(self):
        # R$ 1.000 − R$ 200 adiantamento = R$ 800
        t = self._criar_transporte_com_entrega(adiantamento=200)
        self.assertEqual(calcular_total_transporte(t), Decimal('800'))

    def test_com_frete_terceiro(self):
        # R$ 1.000 + R$ 150 frete terceiro = R$ 1.150 (custo repassado ao cliente)
        t = self._criar_transporte_com_entrega(frete=150)
        self.assertEqual(calcular_total_transporte(t), Decimal('1150'))

    def test_frete_terceiro_e_somado_ao_total(self):
        """frete_terceiro aumenta o total — é custo repassado ao cliente, não dedução."""
        t = self._criar_transporte_com_entrega(frete=200)
        self.assertGreater(calcular_total_transporte(t), Decimal('1000'))
        self.assertEqual(calcular_total_transporte(t), Decimal('1200'))

    def test_formula_completa(self):
        # R$ 1.000 − 50 + 30 − 200 + 150 = R$ 930
        t = self._criar_transporte_com_entrega(
            desconto=50, acrescimo=30, adiantamento=200, frete=150
        )
        self.assertEqual(calcular_total_transporte(t), Decimal('930'))

    def test_propriedade_total_final_usa_servico(self):
        """Transporte.total_final deve retornar o mesmo que calcular_total_transporte."""
        t = self._criar_transporte_com_entrega(desconto=100, acrescimo=50)
        self.assertEqual(t.total_final, calcular_total_transporte(t))

    def test_total_pode_ser_negativo(self):
        """Desconto maior que total das entregas → total negativo (sem restrição)."""
        t = self._criar_transporte_com_entrega(pallets=1, valor_pallet=Decimal('10'), desconto=500)
        self.assertEqual(calcular_total_transporte(t), Decimal('-490'))


# ---------------------------------------------------------------------------
# Testes de calcular_totais_por_status
# ---------------------------------------------------------------------------

class CalcularTotaisPorStatusTest(TestCase):

    def setUp(self):
        self.empresa = _empresa()
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.cliente = _cliente(self.empresa, valor_tipo='por_palete', valor_pallet=Decimal('100'))

    def _criar_transporte(self, status_pagamento, pallets=5, desconto=0):
        t = _transporte(self.empresa, self.motorista, self.veiculo, desconto=desconto)
        t.status_pagamento = status_pagamento
        t.save()
        _entrega(t, self.cliente, pallets=pallets)
        t.refresh_from_db()
        return t

    def test_queryset_vazio(self):
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.none())
        self.assertEqual(resultado['total_receber'], Decimal('0'))
        self.assertEqual(resultado['total_recebido'], Decimal('0'))

    def test_apenas_pendentes(self):
        # 5 × R$ 100 = R$ 500 pendente
        self._criar_transporte('pendente', pallets=5)
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.prefetch_related('entregas'))
        self.assertEqual(resultado['total_receber'], Decimal('500'))
        self.assertEqual(resultado['total_recebido'], Decimal('0'))

    def test_apenas_pagos(self):
        self._criar_transporte('pago', pallets=10)
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.prefetch_related('entregas'))
        self.assertEqual(resultado['total_receber'], Decimal('0'))
        self.assertEqual(resultado['total_recebido'], Decimal('1000'))

    def test_mistura_de_status(self):
        self._criar_transporte('pendente', pallets=5)   # R$ 500
        self._criar_transporte('pago', pallets=3)       # R$ 300
        self._criar_transporte('cancelado', pallets=99) # deve ser ignorado
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.prefetch_related('entregas'))
        self.assertEqual(resultado['total_receber'], Decimal('500'))
        self.assertEqual(resultado['total_recebido'], Decimal('300'))

    def test_total_pendente_alias_de_total_receber(self):
        self._criar_transporte('pendente', pallets=4)
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.prefetch_related('entregas'))
        self.assertEqual(resultado['total_pendente'], resultado['total_receber'])

    def test_com_ajustes_financeiros(self):
        # R$ 500 − R$ 100 desconto = R$ 400 pendente
        self._criar_transporte('pendente', pallets=5, desconto=100)
        from transportes.models import Transporte
        resultado = calcular_totais_por_status(Transporte.objects.prefetch_related('entregas'))
        self.assertEqual(resultado['total_receber'], Decimal('400'))
