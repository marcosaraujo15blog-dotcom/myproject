"""
Testes de criação de transporte.

Cobre:
  - Signal de geração automática do numero_transporte (TR00001, TR00002, ...)
  - TransporteCreateView — GET e POST com formset de entregas
  - TransporteUpdateView — GET e POST de edição
  - TransporteDeleteView — GET (confirmação) e POST (exclusão)
  - Isolamento por empresa no formulário (motorista/veículo de outra empresa)
  - Serviço filtrar_transportes — todos os filtros individuais e combinados
"""

import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from empresas.models import Empresa
from motoristas.models import Motorista
from transportes.models import Entrega, Transporte
from transportes.services import filtrar_transportes
from usuarios.models import Usuario
from veiculos.models import Veiculo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empresa(nome='Transportadora Teste', cnpj='12.345.678/0001-00'):
    return Empresa.objects.create(nome_empresa=nome, cnpj=cnpj, status='ativo')


def _usuario(empresa, tipo='operacional', username='usr_op'):
    user = User.objects.create_user(username=username, password='testpass123')
    Usuario.objects.create(user=user, empresa=empresa, tipo_usuario=tipo)
    return user


def _motorista(empresa, cpf='111.111.111-11', nome='Motorista Teste', cnh='12345678901'):
    return Motorista.objects.create(
        cpf=cpf, nome=nome,
        cnh=cnh, categoria_cnh='E',
        data_vencimento_cnh='2030-12-31',
        data_expedicao_cnh='2015-06-01',
        status='ativo', empresa=empresa,
    )


def _veiculo(empresa, motorista, placa='AAA0A00'):
    return Veiculo.objects.create(
        placa=placa, tipo_vinculo='proprio',
        modelo='Mercedes Axor', ano=2022,
        tipo_carroceria='bau',
        capacidade_carga=Decimal('15000.00'),
        qtd_palete=26, status='ativo',
        empresa=empresa, motorista=motorista,
    )


def _cliente(empresa, codigo='C001'):
    return Cliente.objects.create(
        codigo_cliente=codigo,
        nome_femsa='Cliente Femsa Teste',
        nome_mercado='Mercado Bom',
        tipo_equipamento='toco', tipo_descarga='manual',
        qtd_chapas=0, valor_tipo='por_palete',
        valor_pallet=Decimal('50.00'), empresa=empresa,
    )


def _transporte(empresa, motorista, veiculo, **kwargs):
    defaults = dict(
        data_transporte=datetime.date.today(),
        status_transporte='programado',
        status_pagamento='pendente',
    )
    defaults.update(kwargs)
    return Transporte.objects.create(
        empresa=empresa, motorista=motorista, veiculo=veiculo, **defaults
    )


def _entrega(transporte, cliente, pallets=10, valor_pallet=Decimal('50.00')):
    return Entrega.objects.create(
        transporte=transporte, cliente=cliente,
        pallets=pallets, valor_pallet=valor_pallet, ordem_entrega=1,
    )


# ---------------------------------------------------------------------------
# 1. Signal — geração automática de numero_transporte
# ---------------------------------------------------------------------------

class NumeroTransporteSignalTest(TestCase):
    """
    Valida que o signal pre_save gera numeros sequenciais no formato TR00001.
    """

    def setUp(self):
        empresa = _empresa()
        self.motorista = _motorista(empresa)
        self.veiculo = _veiculo(empresa, self.motorista)
        self.empresa = empresa

    def _novo(self):
        return _transporte(self.empresa, self.motorista, self.veiculo)

    def test_primeiro_transporte_recebe_TR00001(self):
        t = self._novo()
        self.assertEqual(t.numero_transporte, 'TR00001')

    def test_segundo_transporte_recebe_TR00002(self):
        self._novo()
        t2 = self._novo()
        self.assertEqual(t2.numero_transporte, 'TR00002')

    def test_sequencia_incremental_com_tres(self):
        numeros = [self._novo().numero_transporte for _ in range(3)]
        self.assertEqual(numeros, ['TR00001', 'TR00002', 'TR00003'])

    def test_numero_preexistente_nao_e_sobrescrito(self):
        """Se o transporte já tem numero, o signal não altera."""
        t = Transporte.objects.create(
            numero_transporte='TR99999',
            empresa=self.empresa, motorista=self.motorista,
            veiculo=self.veiculo,
            data_transporte=datetime.date.today(),
            status_transporte='programado', status_pagamento='pendente',
        )
        self.assertEqual(t.numero_transporte, 'TR99999')

    def test_formato_TR_com_cinco_digitos(self):
        t = self._novo()
        num = t.numero_transporte
        self.assertTrue(num.startswith('TR'))
        self.assertEqual(len(num), 7)
        self.assertTrue(num[2:].isdigit())

    def test_continua_a_partir_do_ultimo(self):
        """Se o último número existente é TR00050, o próximo deve ser TR00051."""
        Transporte.objects.create(
            numero_transporte='TR00050',
            empresa=self.empresa, motorista=self.motorista,
            veiculo=self.veiculo,
            data_transporte=datetime.date.today(),
            status_transporte='programado', status_pagamento='pendente',
        )
        t = self._novo()
        self.assertEqual(t.numero_transporte, 'TR00051')

    def test_save_nao_regera_numero_existente(self):
        """Re-salvar um transporte não muda o numero_transporte."""
        t = self._novo()
        numero_original = t.numero_transporte
        t.status_transporte = 'em_andamento'
        t.save()
        t.refresh_from_db()
        self.assertEqual(t.numero_transporte, numero_original)


# ---------------------------------------------------------------------------
# 2. TransporteCreateView — integração via Client
# ---------------------------------------------------------------------------

class TransporteCreateViewTest(TestCase):
    """
    Testa o fluxo completo de criação: GET do formulário + POST com formset.
    """

    def setUp(self):
        self.empresa = _empresa()
        self.user = _usuario(self.empresa, tipo='operacional', username='op_create')
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.cliente = _cliente(self.empresa)
        self.url = reverse('transportes:criar')
        self.client.login(username='op_create', password='testpass123')

    def _dados_validos(self, com_entrega=True):
        data = {
            'data_transporte': datetime.date.today().isoformat(),
            'motorista': self.motorista.cpf,
            'veiculo': self.veiculo.placa,
            'status_transporte': 'programado',
            'status_pagamento': 'pendente',
            'documento_transporte': '',
            'desconto': '0',
            'acrescimo': '0',
            'adiantamento': '0',
            'frete_terceiro': '0',
            'entregas-TOTAL_FORMS': '1',
            'entregas-INITIAL_FORMS': '0',
            'entregas-MIN_NUM_FORMS': '0',
            'entregas-MAX_NUM_FORMS': '3',
        }
        if com_entrega:
            data.update({
                'entregas-0-cliente': self.cliente.codigo_cliente,
                'entregas-0-pallets': '10',
                'entregas-0-valor_pallet': '50.00',
                'entregas-0-ordem_entrega': '1',
                'entregas-0-empresa_descarga': '',
            })
        else:
            # Zero forms: formset vazio, sem entregas
            data['entregas-TOTAL_FORMS'] = '0'
        return data

    def test_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_valido_cria_transporte(self):
        self.client.post(self.url, self._dados_validos())
        self.assertEqual(Transporte.objects.count(), 1)

    def test_post_cria_entrega_vinculada(self):
        self.client.post(self.url, self._dados_validos(com_entrega=True))
        self.assertEqual(Entrega.objects.count(), 1)
        entrega = Entrega.objects.first()
        self.assertEqual(entrega.cliente, self.cliente)
        self.assertEqual(entrega.pallets, 10)

    def test_post_empresa_atribuida_pelo_usuario_logado(self):
        self.client.post(self.url, self._dados_validos())
        transporte = Transporte.objects.first()
        self.assertEqual(transporte.empresa, self.empresa)

    def test_post_numero_transporte_gerado_automaticamente(self):
        self.client.post(self.url, self._dados_validos())
        transporte = Transporte.objects.first()
        self.assertRegex(transporte.numero_transporte, r'^TR\d{5}$')

    def test_post_redireciona_para_lista(self):
        response = self.client.post(self.url, self._dados_validos())
        self.assertRedirects(response, reverse('transportes:lista'))

    def test_post_sem_motorista_retorna_formulario_com_erro(self):
        data = self._dados_validos()
        data.pop('motorista')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transporte.objects.count(), 0)

    def test_post_sem_veiculo_retorna_formulario_com_erro(self):
        data = self._dados_validos()
        data.pop('veiculo')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transporte.objects.count(), 0)

    def test_post_sem_entregas_cria_transporte_vazio(self):
        """Formset sem entregas preenchidas é válido — cria transporte sem entregas."""
        self.client.post(self.url, self._dados_validos(com_entrega=False))
        self.assertEqual(Transporte.objects.count(), 1)
        self.assertEqual(Entrega.objects.count(), 0)

    def test_post_valor_total_entrega_calculado_automaticamente(self):
        """valor_total da entrega é calculado pelo serviço financeiro no save."""
        self.client.post(self.url, self._dados_validos(com_entrega=True))
        entrega = Entrega.objects.first()
        # por_palete: 10 pallets × R$ 50,00 = R$ 500,00
        self.assertEqual(entrega.valor_total, Decimal('500.00'))

    def test_post_dois_transportes_recebem_numeros_distintos(self):
        self.client.post(self.url, self._dados_validos())
        self.client.post(self.url, self._dados_validos())
        numeros = list(Transporte.objects.values_list('numero_transporte', flat=True).order_by('numero_transporte'))
        self.assertEqual(len(numeros), 2)
        self.assertNotEqual(numeros[0], numeros[1])


# ---------------------------------------------------------------------------
# 3. TransporteUpdateView — edição
# ---------------------------------------------------------------------------

class TransporteUpdateViewTest(TestCase):
    """
    Testa edição de transporte e atualização de entregas inline.
    """

    def setUp(self):
        self.empresa = _empresa()
        self.user = _usuario(self.empresa, tipo='operacional', username='op_edit')
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.cliente = _cliente(self.empresa)
        self.transporte = _transporte(self.empresa, self.motorista, self.veiculo)
        self.entrega = _entrega(self.transporte, self.cliente)
        self.url = reverse('transportes:editar', kwargs={'pk': self.transporte.pk})
        self.client.login(username='op_edit', password='testpass123')

    def _dados_edicao(self, status='em_andamento', pallets=15, documento='DOC-999'):
        return {
            'data_transporte': datetime.date.today().isoformat(),
            'motorista': self.motorista.cpf,
            'veiculo': self.veiculo.placa,
            'status_transporte': status,
            'status_pagamento': 'pendente',
            'documento_transporte': documento,
            'desconto': '0',
            'acrescimo': '0',
            'adiantamento': '0',
            'frete_terceiro': '0',
            'entregas-TOTAL_FORMS': '1',
            'entregas-INITIAL_FORMS': '1',
            'entregas-MIN_NUM_FORMS': '0',
            'entregas-MAX_NUM_FORMS': '3',
            'entregas-0-id': str(self.entrega.pk),
            'entregas-0-cliente': self.cliente.codigo_cliente,
            'entregas-0-pallets': str(pallets),
            'entregas-0-valor_pallet': '50.00',
            'entregas-0-ordem_entrega': '1',
            'entregas-0-empresa_descarga': '',
        }

    def test_get_exibe_formulario(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_atualiza_status_transporte(self):
        self.client.post(self.url, self._dados_edicao(status='em_andamento'))
        self.transporte.refresh_from_db()
        self.assertEqual(self.transporte.status_transporte, 'em_andamento')

    def test_post_atualiza_documento(self):
        self.client.post(self.url, self._dados_edicao(documento='NF-XYZ'))
        self.transporte.refresh_from_db()
        self.assertEqual(self.transporte.documento_transporte, 'NF-XYZ')

    def test_post_numero_transporte_nao_muda(self):
        numero_original = self.transporte.numero_transporte
        self.client.post(self.url, self._dados_edicao())
        self.transporte.refresh_from_db()
        self.assertEqual(self.transporte.numero_transporte, numero_original)

    def test_post_atualiza_pallets_da_entrega(self):
        self.client.post(self.url, self._dados_edicao(pallets=20))
        self.entrega.refresh_from_db()
        self.assertEqual(self.entrega.pallets, 20)

    def test_post_redireciona_para_lista(self):
        response = self.client.post(self.url, self._dados_edicao())
        self.assertRedirects(response, reverse('transportes:lista'))


# ---------------------------------------------------------------------------
# 4. TransporteDeleteView — exclusão
# ---------------------------------------------------------------------------

class TransporteDeleteViewTest(TestCase):
    """
    Testa confirmação e exclusão de transporte.
    Garante cascade de entregas.
    """

    def setUp(self):
        self.empresa = _empresa()
        self.user = _usuario(self.empresa, tipo='operacional', username='op_delete')
        self.motorista = _motorista(self.empresa)
        self.veiculo = _veiculo(self.empresa, self.motorista)
        self.cliente = _cliente(self.empresa)
        self.transporte = _transporte(self.empresa, self.motorista, self.veiculo)
        self.entrega = _entrega(self.transporte, self.cliente)
        self.url = reverse('transportes:excluir', kwargs={'pk': self.transporte.pk})
        self.client.login(username='op_delete', password='testpass123')

    def test_get_exibe_pagina_de_confirmacao(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_exclui_transporte(self):
        self.client.post(self.url)
        self.assertEqual(Transporte.objects.count(), 0)

    def test_post_exclui_entregas_em_cascade(self):
        self.assertEqual(Entrega.objects.count(), 1)
        self.client.post(self.url)
        self.assertEqual(Entrega.objects.count(), 0)

    def test_post_redireciona_para_lista(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('transportes:lista'))

    def test_motorista_nao_e_excluido_com_transporte(self):
        """PROTECT: motorista permanece após excluir o transporte."""
        self.client.post(self.url)
        self.assertTrue(Motorista.objects.filter(cpf=self.motorista.cpf).exists())

    def test_veiculo_nao_e_excluido_com_transporte(self):
        """PROTECT: veículo permanece após excluir o transporte."""
        self.client.post(self.url)
        self.assertTrue(Veiculo.objects.filter(placa=self.veiculo.placa).exists())


# ---------------------------------------------------------------------------
# 5. Isolamento por empresa no formulário de criação
# ---------------------------------------------------------------------------

class TransporteFormIsolamentoTest(TestCase):
    """
    Garante que o formulário filtra motoristas e veículos pela empresa do usuário.
    Tentativas de usar recursos de outra empresa devem falhar na validação.
    """

    def setUp(self):
        self.empresa_a = _empresa('Empresa Alpha', '11.111.111/0001-11')
        self.empresa_b = _empresa('Empresa Beta', '22.222.222/0001-22')

        self.user_a = _usuario(self.empresa_a, tipo='operacional', username='usr_a')

        self.motorista_a = _motorista(self.empresa_a, cpf='111.111.111-11', nome='Motorista A', cnh='11111111111')
        self.motorista_b = _motorista(self.empresa_b, cpf='222.222.222-22', nome='Motorista B', cnh='22222222222')

        self.veiculo_a = _veiculo(self.empresa_a, self.motorista_a, placa='AAA0000')
        self.veiculo_b = _veiculo(self.empresa_b, self.motorista_b, placa='BBB1111')

        self.cliente_a = _cliente(self.empresa_a, codigo='CA01')

        self.url = reverse('transportes:criar')
        self.client.login(username='usr_a', password='testpass123')

    def _base_data(self):
        return {
            'data_transporte': datetime.date.today().isoformat(),
            'status_transporte': 'programado',
            'status_pagamento': 'pendente',
            'documento_transporte': '',
            'desconto': '0',
            'acrescimo': '0',
            'adiantamento': '0',
            'frete_terceiro': '0',
            'entregas-TOTAL_FORMS': '1',
            'entregas-INITIAL_FORMS': '0',
            'entregas-MIN_NUM_FORMS': '0',
            'entregas-MAX_NUM_FORMS': '3',
            'entregas-0-cliente': self.cliente_a.codigo_cliente,
            'entregas-0-pallets': '10',
            'entregas-0-valor_pallet': '50.00',
            'entregas-0-ordem_entrega': '1',
            'entregas-0-empresa_descarga': '',
        }

    def test_post_com_motorista_de_outra_empresa_rejeitado(self):
        """O form filtra motoristas pela empresa — motorista da B é inválido para A."""
        data = self._base_data()
        data['motorista'] = self.motorista_b.cpf
        data['veiculo'] = self.veiculo_a.placa
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transporte.objects.count(), 0)

    def test_post_com_veiculo_de_outra_empresa_rejeitado(self):
        """O form filtra veículos pela empresa — veículo da B é inválido para A."""
        data = self._base_data()
        data['motorista'] = self.motorista_a.cpf
        data['veiculo'] = self.veiculo_b.placa
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Transporte.objects.count(), 0)

    def test_post_com_recursos_proprios_aceito(self):
        """Motorista e veículo da própria empresa devem ser aceitos."""
        data = self._base_data()
        data['motorista'] = self.motorista_a.cpf
        data['veiculo'] = self.veiculo_a.placa
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('transportes:lista'))
        self.assertEqual(Transporte.objects.count(), 1)


# ---------------------------------------------------------------------------
# 6. Serviço filtrar_transportes
# ---------------------------------------------------------------------------

class FiltrarTransportesTest(TestCase):
    """
    Testa a função filtrar_transportes() com todos os filtros disponíveis.
    """

    def setUp(self):
        empresa = _empresa()

        motorista_a = _motorista(empresa, cpf='111.111.111-11', nome='Carlos Souza', cnh='11111111111')
        motorista_b = _motorista(empresa, cpf='222.222.222-22', nome='Pedro Lima', cnh='22222222222')

        veiculo_a = _veiculo(empresa, motorista_a, placa='AAA0000')
        veiculo_b = _veiculo(empresa, motorista_b, placa='BBB1111')

        hoje = datetime.date.today()
        ontem = hoje - datetime.timedelta(days=1)
        amanha = hoje + datetime.timedelta(days=1)

        self.t1 = _transporte(
            empresa, motorista_a, veiculo_a,
            data_transporte=ontem,
            status_transporte='programado',
            documento_transporte='NF-001',
        )
        self.t2 = _transporte(
            empresa, motorista_b, veiculo_b,
            data_transporte=hoje,
            status_transporte='em_andamento',
            documento_transporte='NF-002',
        )
        self.t3 = _transporte(
            empresa, motorista_a, veiculo_a,
            data_transporte=amanha,
            status_transporte='entregue',
            documento_transporte='NF-003',
        )

        self.qs = Transporte.objects.all()
        self.motorista_a = motorista_a
        self.motorista_b = motorista_b
        self.hoje = hoje
        self.ontem = ontem
        self.amanha = amanha

    def test_sem_filtros_retorna_todos(self):
        resultado = filtrar_transportes(self.qs)
        self.assertEqual(resultado.count(), 3)

    def test_filtro_por_numero_transporte(self):
        num = self.t1.numero_transporte
        resultado = filtrar_transportes(self.qs, q=num)
        self.assertIn(self.t1, resultado)
        self.assertNotIn(self.t2, resultado)

    def test_filtro_por_documento(self):
        resultado = filtrar_transportes(self.qs, q='NF-002')
        self.assertIn(self.t2, resultado)
        self.assertNotIn(self.t1, resultado)
        self.assertNotIn(self.t3, resultado)

    def test_filtro_por_nome_motorista(self):
        resultado = filtrar_transportes(self.qs, q='Carlos')
        self.assertIn(self.t1, resultado)
        self.assertIn(self.t3, resultado)
        self.assertNotIn(self.t2, resultado)

    def test_filtro_por_placa_veiculo(self):
        resultado = filtrar_transportes(self.qs, q='BBB1111')
        self.assertIn(self.t2, resultado)
        self.assertNotIn(self.t1, resultado)

    def test_filtro_data_inicio_exclui_anteriores(self):
        resultado = filtrar_transportes(self.qs, data_inicio=self.hoje.isoformat())
        self.assertNotIn(self.t1, resultado)
        self.assertIn(self.t2, resultado)
        self.assertIn(self.t3, resultado)

    def test_filtro_data_fim_exclui_posteriores(self):
        resultado = filtrar_transportes(self.qs, data_fim=self.hoje.isoformat())
        self.assertIn(self.t1, resultado)
        self.assertIn(self.t2, resultado)
        self.assertNotIn(self.t3, resultado)

    def test_filtro_data_intervalo_exato(self):
        resultado = filtrar_transportes(
            self.qs,
            data_inicio=self.hoje.isoformat(),
            data_fim=self.hoje.isoformat(),
        )
        self.assertEqual(resultado.count(), 1)
        self.assertIn(self.t2, resultado)

    def test_filtro_por_status_programado(self):
        resultado = filtrar_transportes(self.qs, status='programado')
        self.assertEqual(resultado.count(), 1)
        self.assertIn(self.t1, resultado)

    def test_filtro_por_status_entregue(self):
        resultado = filtrar_transportes(self.qs, status='entregue')
        self.assertEqual(resultado.count(), 1)
        self.assertIn(self.t3, resultado)

    def test_filtro_por_motorista_id(self):
        resultado = filtrar_transportes(self.qs, motorista_id=self.motorista_b.cpf)
        self.assertEqual(resultado.count(), 1)
        self.assertIn(self.t2, resultado)

    def test_filtros_combinados_status_e_data(self):
        # programado + data_fim=ontem → apenas t1
        resultado = filtrar_transportes(
            self.qs,
            status='programado',
            data_fim=self.ontem.isoformat(),
        )
        self.assertEqual(resultado.count(), 1)
        self.assertIn(self.t1, resultado)

    def test_filtros_sem_resultado(self):
        resultado = filtrar_transportes(self.qs, q='XXXXX-NAO-EXISTE')
        self.assertEqual(resultado.count(), 0)

    def test_filtro_busca_case_insensitive(self):
        resultado = filtrar_transportes(self.qs, q='carlos')
        self.assertIn(self.t1, resultado)
