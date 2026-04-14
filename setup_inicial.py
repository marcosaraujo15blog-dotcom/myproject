"""
Script para criação do superusuário e dados iniciais do sistema.
Execute: python setup_inicial.py
"""

import os
import sys
import django

# Força encoding UTF-8 no terminal Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from empresas.models import Empresa
from usuarios.models import Usuario


def main():
    print("=" * 50)
    print("ERP Logistica - Setup Inicial")
    print("=" * 50)

    # 1. Criar empresa demo
    empresa, created = Empresa.objects.get_or_create(
        cnpj='00.000.000/0001-00',
        defaults={
            'nome_empresa': 'GRF Logistica T2',
            'email': 'contato@grflogistica.com.br',
            'telefone': '(11) 99999-0000',
            'status': 'ativo',
        }
    )
    if created:
        print(f"[OK] Empresa criada: {empresa.nome_empresa}")
    else:
        print(f"[--] Empresa ja existe: {empresa.nome_empresa}")

    # 2. Criar superusuário
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            email='admin@erp.com',
        )
        print("[OK] Superusuario criado: admin / admin123")
    else:
        print("[--] Superusuario ja existe: admin")

    # 3. Criar usuário administrador da empresa
    if not User.objects.filter(username='marcos').exists():
        user_marcos = User.objects.create_user(
            username='marcos',
            password='marcos123',
            first_name='Marcos',
            last_name='Araujo',
            email='marcos@grflogistica.com.br',
        )
        Usuario.objects.create(
            user=user_marcos,
            empresa=empresa,
            tipo_usuario='administrador',
        )
        print("[OK] Usuario criado: marcos / marcos123 (Administrador)")
    else:
        print("[--] Usuario 'marcos' ja existe")

    # 4. Criar usuário operacional
    if not User.objects.filter(username='operacao').exists():
        user_op = User.objects.create_user(
            username='operacao',
            password='operacao123',
            first_name='Operacao',
            last_name='Logistica',
        )
        Usuario.objects.create(
            user=user_op,
            empresa=empresa,
            tipo_usuario='operacional',
        )
        print("[OK] Usuario criado: operacao / operacao123 (Operacional)")
    else:
        print("[--] Usuario 'operacao' ja existe")

    print("\n" + "=" * 50)
    print("Setup concluido com sucesso!")
    print("\nAcesse: http://localhost:8000")
    print("Usuarios disponiveis:")
    print("  admin    / admin123    (superusuario)")
    print("  marcos   / marcos123   (administrador da empresa)")
    print("  operacao / operacao123 (operacional)")
    print("=" * 50)


if __name__ == '__main__':
    main()
