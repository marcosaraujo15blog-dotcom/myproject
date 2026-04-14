"""
Testes de controle de acesso por tipo de usuário.

Cobre os três mixins de permissão:
  - AdminMixin       → ['administrador']           → /usuarios/
  - OperacionalMixin → ['administrador', 'operacional'] → /transportes/
  - FinanceiroMixin  → ['administrador', 'financeiro']  → /financeiro/

Regras validadas:
  - Usuário com permissão → HTTP 200
  - Usuário sem permissão → redirect para /
  - Usuário não autenticado → redirect para /usuarios/login/
  - Superusuário → HTTP 200 (bypass de verificação de tipo)
  - Mensagem de erro exibida ao usuário sem permissão
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from empresas.models import Empresa
from usuarios.models import Usuario


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empresa(nome='Empresa Permissoes', cnpj='99.888.777/0001-66'):
    return Empresa.objects.create(nome_empresa=nome, cnpj=cnpj, status='ativo')


def _usuario(empresa, tipo, username):
    user = User.objects.create_user(username=username, password='testpass123')
    Usuario.objects.create(user=user, empresa=empresa, tipo_usuario=tipo)
    return user


def _superuser(username='superadmin'):
    return User.objects.create_superuser(
        username=username, password='testpass123', email='super@test.com'
    )


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BasePermissaoTest(TestCase):
    def setUp(self):
        self.empresa = _empresa()
        self.admin_user = _usuario(self.empresa, 'administrador', 'usr_admin')
        self.operacional_user = _usuario(self.empresa, 'operacional', 'usr_op')
        self.financeiro_user = _usuario(self.empresa, 'financeiro', 'usr_fin')
        self.super_user = _superuser()


# ---------------------------------------------------------------------------
# 1. AdminMixin — somente administradores
#    View de referência: usuarios:lista (/usuarios/)
# ---------------------------------------------------------------------------

class AdminMixinTest(BasePermissaoTest):
    """
    Valida AdminMixin: somente 'administrador' pode acessar.
    View testada: UsuarioListView (usuarios:lista).
    """

    URL = 'usuarios:lista'

    def _get(self):
        return self.client.get(reverse(self.URL))

    def test_administrador_acessa_200(self):
        self.client.login(username='usr_admin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_operacional_e_redirecionado_para_raiz(self):
        self.client.login(username='usr_op', password='testpass123')
        response = self._get()
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_financeiro_e_redirecionado_para_raiz(self):
        self.client.login(username='usr_fin', password='testpass123')
        response = self._get()
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_anonimo_redirecionado_para_login(self):
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response['Location'])

    def test_superuser_acessa_sem_restricao(self):
        self.client.login(username='superadmin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_operacional_recebe_mensagem_de_erro(self):
        """Usuário sem permissão deve receber mensagem de aviso."""
        self.client.login(username='usr_op', password='testpass123')
        response = self.client.get(reverse(self.URL), follow=True)
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(
            any('Acesso restrito' in m or 'Permissão' in m for m in messages),
            msg=f'Mensagem de erro não encontrada. Mensagens: {messages}',
        )


# ---------------------------------------------------------------------------
# 2. OperacionalMixin — administradores + operacionais
#    View de referência: transportes:lista (/transportes/)
# ---------------------------------------------------------------------------

class OperacionalMixinTest(BasePermissaoTest):
    """
    Valida OperacionalMixin: 'administrador' e 'operacional' podem acessar.
    View testada: TransporteListView (transportes:lista).
    """

    URL = 'transportes:lista'

    def _get(self):
        return self.client.get(reverse(self.URL))

    def test_administrador_acessa_200(self):
        self.client.login(username='usr_admin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_operacional_acessa_200(self):
        self.client.login(username='usr_op', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_financeiro_e_redirecionado_para_raiz(self):
        self.client.login(username='usr_fin', password='testpass123')
        response = self._get()
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_anonimo_redirecionado_para_login(self):
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response['Location'])

    def test_superuser_acessa_sem_restricao(self):
        self.client.login(username='superadmin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_financeiro_recebe_mensagem_de_erro(self):
        self.client.login(username='usr_fin', password='testpass123')
        response = self.client.get(reverse(self.URL), follow=True)
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any('Acesso restrito' in m or 'Permissão' in m for m in messages))

    def test_operacional_acessa_formulario_criacao(self):
        self.client.login(username='usr_op', password='testpass123')
        response = self.client.get(reverse('transportes:criar'))
        self.assertEqual(response.status_code, 200)

    def test_financeiro_nao_acessa_formulario_criacao(self):
        self.client.login(username='usr_fin', password='testpass123')
        response = self.client.get(reverse('transportes:criar'))
        self.assertRedirects(response, '/', fetch_redirect_response=False)


# ---------------------------------------------------------------------------
# 3. FinanceiroMixin — administradores + financeiros
#    View de referência: financeiro:lista (/financeiro/)
# ---------------------------------------------------------------------------

class FinanceiroMixinTest(BasePermissaoTest):
    """
    Valida FinanceiroMixin: 'administrador' e 'financeiro' podem acessar.
    View testada: FinanceiroListView (financeiro:lista).
    """

    URL = 'financeiro:lista'

    def _get(self):
        return self.client.get(reverse(self.URL))

    def test_administrador_acessa_200(self):
        self.client.login(username='usr_admin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_financeiro_acessa_200(self):
        self.client.login(username='usr_fin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_operacional_e_redirecionado_para_raiz(self):
        self.client.login(username='usr_op', password='testpass123')
        response = self._get()
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_anonimo_redirecionado_para_login(self):
        response = self._get()
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response['Location'])

    def test_superuser_acessa_sem_restricao(self):
        self.client.login(username='superadmin', password='testpass123')
        self.assertEqual(self._get().status_code, 200)

    def test_operacional_recebe_mensagem_de_erro(self):
        self.client.login(username='usr_op', password='testpass123')
        response = self.client.get(reverse(self.URL), follow=True)
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any('Acesso restrito' in m or 'Permissão' in m for m in messages))


# ---------------------------------------------------------------------------
# 4. Comportamento de login_required — redireciona preservando next
# ---------------------------------------------------------------------------

class LoginRedirectTest(TestCase):
    """
    Valida que rotas protegidas redirecionam para o login
    e preservam a URL de destino no parâmetro ?next=.
    """

    def test_transportes_preserva_next(self):
        url = reverse('transportes:lista')
        response = self.client.get(url)
        self.assertIn('?next=', response['Location'])
        self.assertIn('/transportes/', response['Location'])

    def test_financeiro_preserva_next(self):
        url = reverse('financeiro:lista')
        response = self.client.get(url)
        self.assertIn('?next=', response['Location'])

    def test_usuarios_preserva_next(self):
        url = reverse('usuarios:lista')
        response = self.client.get(url)
        self.assertIn('?next=', response['Location'])

    def test_criacao_transporte_exige_login(self):
        url = reverse('transportes:criar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/usuarios/login/', response['Location'])
