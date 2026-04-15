"""
Testes do módulo Motoristas.

Cobre:
  - Formulário de edição pré-preenche campos de data corretamente
  - View UpdateView retorna os valores salvos nos campos date
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from empresas.models import Empresa
from motoristas.forms import MotoristaForm
from motoristas.models import Motorista
from usuarios.models import Usuario


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empresa():
    return Empresa.objects.create(
        nome_empresa='Empresa Teste', cnpj='11.111.111/0001-11', status='ativo'
    )


def _usuario(empresa, tipo='operacional', username='usr_test'):
    user = User.objects.create_user(username=username, password='testpass123')
    Usuario.objects.create(user=user, empresa=empresa, tipo_usuario=tipo)
    return user


def _motorista(empresa):
    return Motorista.objects.create(
        cpf='111.111.111-11',
        nome='João da Silva',
        data_nascimento=datetime.date(1985, 6, 15),
        cnh='12345678901',
        categoria_cnh='E',
        data_vencimento_cnh=datetime.date(2030, 12, 31),
        data_expedicao_cnh=datetime.date(2015, 3, 20),
        status='ativo',
        empresa=empresa,
    )


# ---------------------------------------------------------------------------
# Testes do formulário
# ---------------------------------------------------------------------------

class MotoristaFormDateFormatTest(TestCase):
    """
    Valida que o MotoristaForm formata datas como YYYY-MM-DD.
    Campos type='date' exigem esse formato para pré-preencher no browser.
    """

    def setUp(self):
        self.empresa = _empresa()
        self.motorista = _motorista(self.empresa)

    def test_data_nascimento_formato_iso(self):
        form = MotoristaForm(instance=self.motorista)
        rendered = str(form['data_nascimento'])
        self.assertIn('value="1985-06-15"', rendered)

    def test_data_vencimento_cnh_formato_iso(self):
        form = MotoristaForm(instance=self.motorista)
        rendered = str(form['data_vencimento_cnh'])
        self.assertIn('value="2030-12-31"', rendered)

    def test_data_expedicao_cnh_formato_iso(self):
        form = MotoristaForm(instance=self.motorista)
        rendered = str(form['data_expedicao_cnh'])
        self.assertIn('value="2015-03-20"', rendered)


# ---------------------------------------------------------------------------
# Testes da view de edição
# ---------------------------------------------------------------------------

class MotoristaUpdateViewDateTest(TestCase):
    """
    Valida que a view de edição retorna as datas salvas nos campos do formulário.
    """

    def setUp(self):
        self.empresa = _empresa()
        self.user = _usuario(self.empresa)
        self.motorista = _motorista(self.empresa)
        self.url = reverse('motoristas:editar', kwargs={'pk': self.motorista.pk})
        self.client.login(username='usr_test', password='testpass123')

    def test_get_retorna_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_data_nascimento_preenche_campo(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="1985-06-15"')

    def test_data_vencimento_cnh_preenche_campo(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="2030-12-31"')

    def test_data_expedicao_cnh_preenche_campo(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'value="2015-03-20"')
