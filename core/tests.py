"""
Testes de isolamento por empresa (tenant isolation).

Valida que nenhum usuário consegue visualizar ou manipular dados
de outra empresa — em listagens, detalhes, edições e exclusões.

Modelos testados: Motorista, Veiculo, Cliente, Transporte, Entrega.

Para rodar:
    python manage.py test core.tests --settings=config.settings
    (defina USE_SQLITE=True no .env para não precisar do PostgreSQL)
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from empresas.models import Empresa
from empresas_descarga.models import EmpresaDescarga
from motoristas.models import Motorista
from transportes.models import Entrega, Transporte
from usuarios.models import Usuario
from veiculos.models import Veiculo


# ---------------------------------------------------------------------------
# Helpers de criação de dados de teste
# ---------------------------------------------------------------------------

def criar_empresa(sufixo):
    """Cria uma Empresa com dados únicos baseados no sufixo."""
    return Empresa.objects.create(
        nome_empresa=f'Empresa {sufixo}',
        cnpj=f'{sufixo}{sufixo}.{sufixo}{sufixo}{sufixo}.{sufixo}{sufixo}{sufixo}/000{sufixo[-1]}-0{sufixo[-1]}',
    )


def criar_usuario(username, empresa, tipo='operacional'):
    """Cria User + Usuario com empresa associada."""
    user = User.objects.create_user(username=username, password='senha@123')
    Usuario.objects.create(user=user, empresa=empresa, tipo_usuario=tipo)
    return user


def criar_motorista(cpf, nome, empresa):
    return Motorista.objects.create(
        cpf=cpf,
        nome=nome,
        cnh=cpf.replace('.', '').replace('-', '')[:11],
        categoria_cnh='B',
        data_vencimento_cnh=datetime.date(2030, 1, 1),
        data_expedicao_cnh=datetime.date(2020, 1, 1),
        empresa=empresa,
    )


def criar_veiculo(placa, empresa, motorista=None):
    return Veiculo.objects.create(
        placa=placa,
        modelo='Modelo Teste',
        tipo_vinculo='proprio',
        ano=2022,
        tipo_carroceria='bau',
        capacidade_carga=5000,
        qtd_palete=20,
        empresa=empresa,
        motorista=motorista,
    )


def criar_cliente(nome, empresa):
    return Cliente.objects.create(
        nome_femsa=f'{nome} Femsa',
        nome_mercado=nome,
        tipo_equipamento='toco',
        tipo_descarga='manual',
        valor_tipo='por_palete',
        valor_pallet=50,
        empresa=empresa,
    )


def criar_transporte(empresa, motorista, veiculo):
    return Transporte.objects.create(
        data_transporte=datetime.date.today(),
        motorista=motorista,
        veiculo=veiculo,
        empresa=empresa,
    )


def criar_entrega(transporte, cliente):
    return Entrega.objects.create(
        transporte=transporte,
        cliente=cliente,
        pallets=10,
        valor_pallet=50,
        ordem_entrega=1,
    )


# ---------------------------------------------------------------------------
# Base: setUp compartilhado entre todos os testes de isolamento
# ---------------------------------------------------------------------------

class BaseIsolamentoTest(TestCase):
    """
    Prepara duas empresas (A e B) com seus respectivos dados.
    Cada subclasse de teste herda este setUp.
    """

    def setUp(self):
        # --- Empresas ---
        self.empresa_a = Empresa.objects.create(
            nome_empresa='Empresa Alpha', cnpj='11.111.111/0001-11'
        )
        self.empresa_b = Empresa.objects.create(
            nome_empresa='Empresa Beta', cnpj='22.222.222/0001-22'
        )

        # --- Usuários ---
        self.user_a = criar_usuario('user_alpha', self.empresa_a)
        self.user_b = criar_usuario('user_beta', self.empresa_b)
        self.superuser = User.objects.create_superuser('admin', password='admin@123')

        # --- Motoristas ---
        self.motorista_a = criar_motorista('111.111.111-11', 'Motorista Alpha', self.empresa_a)
        self.motorista_b = criar_motorista('222.222.222-22', 'Motorista Beta', self.empresa_b)

        # --- Veículos ---
        self.veiculo_a = criar_veiculo('AAA1A11', self.empresa_a, self.motorista_a)
        self.veiculo_b = criar_veiculo('BBB2B22', self.empresa_b, self.motorista_b)

        # --- Clientes ---
        self.cliente_a = criar_cliente('Cliente Alpha', self.empresa_a)
        self.cliente_b = criar_cliente('Cliente Beta', self.empresa_b)

        # --- Transportes ---
        self.transporte_a = criar_transporte(self.empresa_a, self.motorista_a, self.veiculo_a)
        self.transporte_b = criar_transporte(self.empresa_b, self.motorista_b, self.veiculo_b)

        # --- Entregas ---
        self.entrega_a = criar_entrega(self.transporte_a, self.cliente_a)
        self.entrega_b = criar_entrega(self.transporte_b, self.cliente_b)

    def login_a(self):
        self.client.login(username='user_alpha', password='senha@123')

    def login_b(self):
        self.client.login(username='user_beta', password='senha@123')

    def login_super(self):
        self.client.login(username='admin', password='admin@123')


# ---------------------------------------------------------------------------
# Motorista
# ---------------------------------------------------------------------------

class MotoristaIsolamentoTest(BaseIsolamentoTest):

    def test_lista_exibe_apenas_motoristas_da_propria_empresa(self):
        self.login_a()
        response = self.client.get(reverse('motoristas:lista'))
        self.assertEqual(response.status_code, 200)
        nomes = [m.nome for m in response.context['motoristas']]
        self.assertIn('Motorista Alpha', nomes)
        self.assertNotIn('Motorista Beta', nomes)

    def test_lista_empresa_b_nao_ve_dados_empresa_a(self):
        self.login_b()
        response = self.client.get(reverse('motoristas:lista'))
        self.assertEqual(response.status_code, 200)
        nomes = [m.nome for m in response.context['motoristas']]
        self.assertIn('Motorista Beta', nomes)
        self.assertNotIn('Motorista Alpha', nomes)

    def test_edicao_motorista_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('motoristas:editar', kwargs={'pk': self.motorista_b.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_exclusao_motorista_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('motoristas:excluir', kwargs={'pk': self.motorista_b.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_edicao_motorista_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('motoristas:editar', kwargs={'pk': self.motorista_b.cpf})
        response = self.client.post(url, {'nome': 'Invadido'})
        self.assertEqual(response.status_code, 404)
        # Garante que o objeto não foi alterado
        self.motorista_b.refresh_from_db()
        self.assertEqual(self.motorista_b.nome, 'Motorista Beta')

    def test_superuser_ve_todos_os_motoristas(self):
        self.login_super()
        response = self.client.get(reverse('motoristas:lista'))
        self.assertEqual(response.status_code, 200)
        nomes = [m.nome for m in response.context['motoristas']]
        self.assertIn('Motorista Alpha', nomes)
        self.assertIn('Motorista Beta', nomes)

    def test_usuario_nao_autenticado_redireciona_para_login(self):
        response = self.client.get(reverse('motoristas:lista'))
        self.assertRedirects(response, '/usuarios/login/?next=/motoristas/')


# ---------------------------------------------------------------------------
# Veículo
# ---------------------------------------------------------------------------

class VeiculoIsolamentoTest(BaseIsolamentoTest):

    def test_lista_exibe_apenas_veiculos_da_propria_empresa(self):
        self.login_a()
        response = self.client.get(reverse('veiculos:lista'))
        self.assertEqual(response.status_code, 200)
        placas = [v.placa for v in response.context['veiculos']]
        self.assertIn('AAA1A11', placas)
        self.assertNotIn('BBB2B22', placas)

    def test_lista_empresa_b_nao_ve_veiculos_empresa_a(self):
        self.login_b()
        response = self.client.get(reverse('veiculos:lista'))
        self.assertEqual(response.status_code, 200)
        placas = [v.placa for v in response.context['veiculos']]
        self.assertIn('BBB2B22', placas)
        self.assertNotIn('AAA1A11', placas)

    def test_edicao_veiculo_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('veiculos:editar', kwargs={'pk': self.veiculo_b.placa})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_exclusao_veiculo_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('veiculos:excluir', kwargs={'pk': self.veiculo_b.placa})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_exclusao_veiculo_outra_empresa_nao_deleta(self):
        self.login_a()
        url = reverse('veiculos:excluir', kwargs={'pk': self.veiculo_b.placa})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Veiculo.objects.filter(placa='BBB2B22').exists())

    def test_superuser_ve_todos_os_veiculos(self):
        self.login_super()
        response = self.client.get(reverse('veiculos:lista'))
        placas = [v.placa for v in response.context['veiculos']]
        self.assertIn('AAA1A11', placas)
        self.assertIn('BBB2B22', placas)


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

class ClienteIsolamentoTest(BaseIsolamentoTest):

    def test_lista_exibe_apenas_clientes_da_propria_empresa(self):
        self.login_a()
        response = self.client.get(reverse('clientes:lista'))
        self.assertEqual(response.status_code, 200)
        nomes = [c.nome_mercado for c in response.context['clientes']]
        self.assertIn('Cliente Alpha', nomes)
        self.assertNotIn('Cliente Beta', nomes)

    def test_lista_empresa_b_nao_ve_clientes_empresa_a(self):
        self.login_b()
        response = self.client.get(reverse('clientes:lista'))
        nomes = [c.nome_mercado for c in response.context['clientes']]
        self.assertIn('Cliente Beta', nomes)
        self.assertNotIn('Cliente Alpha', nomes)

    def test_edicao_cliente_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('clientes:editar', kwargs={'pk': self.cliente_b.codigo_cliente})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_exclusao_cliente_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('clientes:excluir', kwargs={'pk': self.cliente_b.codigo_cliente})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_exclusao_cliente_outra_empresa_nao_deleta(self):
        self.login_a()
        url = reverse('clientes:excluir', kwargs={'pk': self.cliente_b.codigo_cliente})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente_b.codigo_cliente).exists())

    def test_superuser_ve_todos_os_clientes(self):
        self.login_super()
        response = self.client.get(reverse('clientes:lista'))
        nomes = [c.nome_mercado for c in response.context['clientes']]
        self.assertIn('Cliente Alpha', nomes)
        self.assertIn('Cliente Beta', nomes)


# ---------------------------------------------------------------------------
# Transporte
# ---------------------------------------------------------------------------

class TransporteIsolamentoTest(BaseIsolamentoTest):

    def test_lista_exibe_apenas_transportes_da_propria_empresa(self):
        self.login_a()
        response = self.client.get(reverse('transportes:lista'))
        self.assertEqual(response.status_code, 200)
        pks = [t.pk for t in response.context['transportes']]
        self.assertIn(self.transporte_a.pk, pks)
        self.assertNotIn(self.transporte_b.pk, pks)

    def test_lista_empresa_b_nao_ve_transportes_empresa_a(self):
        self.login_b()
        response = self.client.get(reverse('transportes:lista'))
        pks = [t.pk for t in response.context['transportes']]
        self.assertIn(self.transporte_b.pk, pks)
        self.assertNotIn(self.transporte_a.pk, pks)

    def test_detalhe_transporte_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('transportes:detalhe', kwargs={'pk': self.transporte_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edicao_transporte_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('transportes:editar', kwargs={'pk': self.transporte_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_exclusao_transporte_outra_empresa_retorna_404(self):
        self.login_a()
        url = reverse('transportes:excluir', kwargs={'pk': self.transporte_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_exclusao_transporte_outra_empresa_nao_deleta(self):
        self.login_a()
        url = reverse('transportes:excluir', kwargs={'pk': self.transporte_b.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Transporte.objects.filter(pk=self.transporte_b.pk).exists())

    def test_superuser_ve_todos_os_transportes(self):
        self.login_super()
        response = self.client.get(reverse('transportes:lista'))
        pks = [t.pk for t in response.context['transportes']]
        self.assertIn(self.transporte_a.pk, pks)
        self.assertIn(self.transporte_b.pk, pks)


# ---------------------------------------------------------------------------
# Entrega (isolamento via Transporte)
# ---------------------------------------------------------------------------

class EntregaIsolamentoTest(BaseIsolamentoTest):
    """
    Entregas não possuem campo 'empresa' direto.
    O isolamento é garantido via Transporte: se o usuário não tem acesso
    ao Transporte, não tem acesso às suas Entregas.
    """

    def test_detalhe_transporte_exibe_apenas_suas_entregas(self):
        self.login_a()
        url = reverse('transportes:detalhe', kwargs={'pk': self.transporte_a.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        transporte = response.context['transporte']
        entregas_ids = list(transporte.entregas.values_list('pk', flat=True))
        self.assertIn(self.entrega_a.pk, entregas_ids)
        self.assertNotIn(self.entrega_b.pk, entregas_ids)

    def test_acesso_ao_detalhe_do_transporte_da_entrega_outra_empresa_retorna_404(self):
        """
        Ao tentar acessar o transporte que contém entrega_b via empresa A → 404.
        Indiretamente protege as entregas de empresa B.
        """
        self.login_a()
        url = reverse('transportes:detalhe', kwargs={'pk': self.transporte_b.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_entrega_nao_aparece_no_detalhe_de_transporte_errado(self):
        """
        Mesmo que a entrega_b pertença a transporte_b (empresa B),
        ela nunca aparece no contexto de usuário da empresa A.
        """
        self.login_a()
        url = reverse('transportes:detalhe', kwargs={'pk': self.transporte_a.pk})
        response = self.client.get(url)
        transporte = response.context['transporte']
        entregas_ids = list(transporte.entregas.values_list('pk', flat=True))
        self.assertNotIn(self.entrega_b.pk, entregas_ids)


# ---------------------------------------------------------------------------
# EmpresaQuerySetMixin — testes unitários do mixin em si
# ---------------------------------------------------------------------------

class EmpresaQuerySetMixinUnitTest(BaseIsolamentoTest):
    """
    Valida o comportamento do EmpresaQuerySetMixin diretamente,
    exercitando os mesmos cenários por caminhos de URL.
    """

    def test_get_queryset_filtra_por_empresa_automaticamente(self):
        """
        O queryset retornado pela listagem deve ser filtrado pela empresa
        do usuário logado, sem nenhuma ação adicional na view.
        """
        self.login_a()
        response = self.client.get(reverse('motoristas:lista'))
        self.assertEqual(response.status_code, 200)
        qs = response.context['motoristas']
        empresas_retornadas = set(qs.values_list('empresa_id', flat=True))
        self.assertEqual(empresas_retornadas, {self.empresa_a.pk})

    def test_get_object_bloqueia_objeto_de_outra_empresa(self):
        """
        Tentar acessar um objeto cujo PK pertence a outra empresa
        deve retornar 404, não o objeto.
        """
        self.login_a()
        # Motorista B pertence à empresa B; usuário A não deve conseguir editá-lo
        url = reverse('motoristas:editar', kwargs={'pk': self.motorista_b.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_superuser_sem_empresa_nao_e_filtrado(self):
        """
        Superusuário não tem empresa associada (get_empresa() retorna None),
        portanto o filtro não é aplicado e ele vê todos os registros.
        """
        self.login_super()
        response = self.client.get(reverse('motoristas:lista'))
        self.assertEqual(response.status_code, 200)
        total = response.context['motoristas'].count()
        self.assertEqual(total, Motorista.objects.count())

    def test_usuario_sem_sessao_redireciona_para_login(self):
        """
        Requisições sem autenticação devem redirecionar para a tela de login.
        """
        for url in [
            reverse('motoristas:lista'),
            reverse('veiculos:lista'),
            reverse('clientes:lista'),
            reverse('transportes:lista'),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn('/usuarios/login/', response['Location'])

    def test_criacao_atribui_empresa_do_usuario_logado(self):
        """
        Ao criar um objeto, a empresa deve ser atribuída automaticamente
        a partir do usuário logado (form_valid do EmpresaMixin).
        """
        self.login_a()
        url = reverse('clientes:criar')
        dados = {
            'nome_femsa': 'Novo Cliente Femsa',
            'nome_mercado': 'Novo Cliente',
            'tipo_equipamento': 'toco',
            'tipo_descarga': 'manual',
            'valor_tipo': 'por_palete',
            'valor_pallet': '75.00',
            'qtd_chapas': '0',
        }
        response = self.client.post(url, dados)
        # Deve redirecionar após criação bem-sucedida
        self.assertEqual(response.status_code, 302)
        novo = Cliente.objects.filter(nome_mercado='Novo Cliente').first()
        self.assertIsNotNone(novo)
        self.assertEqual(novo.empresa, self.empresa_a)
