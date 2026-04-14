"""
Script de carga de dados fictícios para teste completo do sistema.
Cria: motoristas, veículos, clientes, empresas de descarga e transportes com entregas.
"""

import os, sys, django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from empresas.models import Empresa
from motoristas.models import Motorista
from veiculos.models import Veiculo
from clientes.models import Cliente
from empresas_descarga.models import EmpresaDescarga
from transportes.models import Transporte, Entrega

def limpar_dados_teste():
    print("[...] Limpando dados de teste anteriores...")
    Entrega.objects.all().delete()
    Transporte.objects.all().delete()
    Cliente.objects.filter(codigo_cliente__startswith='CLI').delete()
    EmpresaDescarga.objects.filter(cnpj_cpf__startswith='99').delete()
    Veiculo.objects.filter(placa__in=['ABC1234','DEF5678','GHI9012','JKL3D45','MNO6E78']).delete()
    Motorista.objects.filter(cpf__in=[
        '12345678901','23456789012','34567890123','45678901234','56789012345'
    ]).delete()
    print("[OK] Dados anteriores removidos.\n")

def criar_motoristas(empresa):
    print("[...] Criando motoristas...")
    dados = [
        ('12345678901', 'Marcos Araújo Silva',     '1985-03-15', 'CNH001001', 'E', '2026-12-31', '2016-01-10', '(11) 98888-1111'),
        ('23456789012', 'Roberto Santos Neto',     '1979-07-22', 'CNH002002', 'D', '2025-06-30', '2010-05-20', '(11) 97777-2222'),
        ('34567890123', 'Claudinho Pereira Lima',  '1990-11-05', 'CNH003003', 'E', '2027-03-15', '2018-08-12', '(11) 96666-3333'),
        ('45678901234', 'José Ferreira Costa',     '1982-04-18', 'CNH004004', 'C', '2026-09-20', '2012-11-30', '(11) 95555-4444'),
        ('56789012345', 'Anderson Machado Rocha',  '1993-08-30', 'CNH005005', 'E', '2028-01-10', '2020-03-05', '(11) 94444-5555'),
    ]
    motoristas = []
    for cpf, nome, nasc, cnh, cat, venc, exped, tel in dados:
        m, c = Motorista.objects.get_or_create(
            cpf=cpf,
            defaults=dict(
                nome=nome,
                data_nascimento=date.fromisoformat(nasc),
                cnh=cnh,
                categoria_cnh=cat,
                data_vencimento_cnh=date.fromisoformat(venc),
                data_expedicao_cnh=date.fromisoformat(exped),
                telefone=tel,
                status='ativo',
                empresa=empresa,
            )
        )
        motoristas.append(m)
        print(f"  [+] {nome}")
    return motoristas

def criar_veiculos(empresa, motoristas):
    print("\n[...] Criando veículos...")
    dados = [
        ('ABC1234', motoristas[0], 'proprio',   'Volvo FH 460',     2022, 'bau',       28000, 28),
        ('DEF5678', motoristas[1], 'proprio',   'Scania R450',      2020, 'sider',     27500, 27),
        ('GHI9012', motoristas[2], 'terceiro',  'Mercedes Actros',  2019, 'bau',       25000, 25),
        ('JKL3D45', motoristas[3], 'agregado',  'Volvo VM 270',     2021, 'grade_baixa', 14000, 14),
        ('MNO6E78', motoristas[4], 'proprio',   'DAF XF 480',       2023, 'bau',       29000, 29),
    ]
    veiculos = []
    for placa, mot, vinculo, modelo, ano, carroceria, cap, paletes in dados:
        v, c = Veiculo.objects.get_or_create(
            placa=placa,
            defaults=dict(
                motorista=mot,
                tipo_vinculo=vinculo,
                modelo=modelo,
                ano=ano,
                tipo_carroceria=carroceria,
                capacidade_carga=Decimal(str(cap)),
                qtd_palete=paletes,
                status='ativo',
                empresa=empresa,
            )
        )
        veiculos.append(v)
        print(f"  [+] {placa} - {modelo}")
    return veiculos

def criar_clientes(empresa):
    print("\n[...] Criando clientes...")
    dados = [
        ('FEMSA BEBIDAS LESTE', 'Mercado São João',   'carreta', 'mecanica', 2, 'por_palete',      Decimal('85.00')),
        ('FEMSA BEBIDAS OESTE', 'Supermercado ABC',   'truck',   'manual',   3, 'por_palete',      Decimal('75.00')),
        ('FEMSA NORTE SP',      'Atacadão Norte',     'carreta', 'mecanica', 4, 'carga_cheia',     Decimal('1800.00')),
        ('FEMSA SUL SP',        'Distribuidora Sul',  'toco',    'manual',   2, 'por_palete',      Decimal('65.00')),
        ('FEMSA CENTRO',        'Atacarejo Centro',   'carreta', 'mecanica', 0, 'carga_cheia',     Decimal('2200.00')),
        ('FEMSA CAMPINAS',      'Mercadão Campinas',  'truck',   'ambos',    2, 'por_palete',      Decimal('90.00')),
        ('FEMSA RIBEIRÃO',      'Supermix Ribeirão',  'carreta', 'mecanica', 3, 'descarga_direto', Decimal('950.00')),
    ]
    clientes = []
    for nome_f, nome_m, equip, desc, chapas, v_tipo, v_pallet in dados:
        c = Cliente(
            nome_femsa=nome_f,
            nome_mercado=nome_m,
            tipo_equipamento=equip,
            tipo_descarga=desc,
            qtd_chapas=chapas,
            valor_tipo=v_tipo,
            valor_pallet=v_pallet,
            empresa=empresa,
        )
        c.save()  # signal gera o codigo_cliente
        clientes.append(c)
        print(f"  [+] {c.codigo_cliente} - {nome_f}")
    return clientes

def criar_descargas(empresa):
    print("\n[...] Criando empresas de descarga...")
    dados = [
        ('99.111.111/0001-11', 'Descarga Rápida Ltda',     'Descargas RR',  '(11) 3333-1111'),
        ('99.222.222/0001-22', 'Logística de Descarga SA', 'LD Express',    '(11) 3333-2222'),
        ('99.333.333/0001-33', 'Operações Logísticas ME',  'OpLog',         '(11) 3333-3333'),
    ]
    descargas = []
    for cnpj, nome, fantasia, tel in dados:
        d, c = EmpresaDescarga.objects.get_or_create(
            cnpj_cpf=cnpj,
            defaults=dict(nome=nome, nome_fantasia=fantasia, telefone=tel, empresa=empresa)
        )
        descargas.append(d)
        print(f"  [+] {fantasia}")
    return descargas

def criar_transportes(empresa, motoristas, veiculos, clientes, descargas):
    print("\n[...] Criando transportes com entregas...")
    hoje = date.today()

    cenarios = [
        # (dias_delta, veiculo_i, motorista_i, status_t, status_p, doc,
        #  [(cliente_i, pallets, descarga_i), ...], desconto, acrescimo, adiantamento, frete_terceiro)
        (  0, 0, 0, 'programado',   'pendente', 'NF-001234',
           [(0, 28, 0), (1, 15, 1)],           0, 0,      0,   0),

        (  0, 1, 1, 'em_andamento', 'pendente', 'NF-001235',
           [(2,  0, 1), (3, 20, 2)],         100, 0,    200,   0),

        ( -1, 2, 2, 'entregue',     'pago',     'NF-001230',
           [(4,  0, 0), (0, 25, 0)],           0, 50,   150, 200),

        ( -1, 3, 3, 'entregue',     'pago',     'NF-001231',
           [(1, 18, 2), (5, 22, 1)],          80, 0,    100,   0),

        ( -2, 4, 4, 'entregue',     'pago',     'NF-001225',
           [(6,  0, 1)],                        0, 0,      0,   0),

        ( -2, 0, 0, 'entregue',     'pendente', 'NF-001226',
           [(3, 12, 0), (5, 18, 2), (1, 10, 1)], 50, 0, 300,   0),

        (  1, 1, 1, 'programado',   'pendente', 'NF-001240',
           [(0, 28, 0)],                        0, 0,      0,   0),

        (  1, 2, 2, 'programado',   'pendente', 'NF-001241',
           [(2,  0, 1), (4,  0, 2)],            0, 0,      0,   0),

        ( -3, 3, 3, 'cancelado',    'cancelado','NF-001220',
           [(1, 15, 0)],                        0, 0,      0,   0),

        (  0, 4, 4, 'programado',   'pendente', 'NF-001236',
           [(5, 30, 2), (6,  0, 0)],            0, 120,   0,   150),
    ]

    transportes = []
    for (delta, vi, mi, st, sp, doc, entregas_data,
         desc, acr, adi, frete) in cenarios:

        data_t = hoje + timedelta(days=delta)
        t = Transporte(
            documento_transporte=doc,
            data_transporte=data_t,
            veiculo=veiculos[vi],
            motorista=motoristas[mi],
            status_transporte=st,
            status_pagamento=sp,
            desconto=Decimal(str(desc)),
            acrescimo=Decimal(str(acr)),
            adiantamento=Decimal(str(adi)),
            frete_terceiro=Decimal(str(frete)),
            empresa=empresa,
        )
        t.save()  # signal gera numero_transporte

        for ordem, (ci, pallets, di) in enumerate(entregas_data, start=1):
            cliente = clientes[ci]
            valor_p = cliente.valor_pallet
            e = Entrega(
                transporte=t,
                cliente=cliente,
                pallets=pallets,
                valor_pallet=valor_p,
                ordem_entrega=ordem,
                empresa_descarga=descargas[di],
            )
            e.save()  # save() calcula valor_total automaticamente

        total = t.total_final
        print(f"  [+] {t.numero_transporte} | {data_t.strftime('%d/%m/%Y')} | "
              f"{motoristas[mi].nome[:20]:<20} | {st:<12} | "
              f"R$ {total:>9.2f} | {len(entregas_data)} entrega(s)")
        transportes.append(t)

    return transportes

def imprimir_resumo(transportes):
    print("\n" + "=" * 65)
    print("RESUMO DOS DADOS GERADOS")
    print("=" * 65)

    total_pago     = sum(t.total_final for t in transportes if t.status_pagamento == 'pago')
    total_pendente = sum(t.total_final for t in transportes if t.status_pagamento == 'pendente')
    total_geral    = sum(t.total_final for t in transportes if t.status_pagamento != 'cancelado')

    print(f"  Transportes criados : {len(transportes)}")
    print(f"  Total pago          : R$ {total_pago:>10.2f}")
    print(f"  Total pendente      : R$ {total_pendente:>10.2f}")
    print(f"  Total geral         : R$ {total_geral:>10.2f}")
    print("=" * 65)
    print("\nAcesse:")
    print("  Programacao : http://localhost:8000/transportes/")
    print("  Financeiro  : http://localhost:8000/financeiro/")
    print("  Dashboard   : http://localhost:8000/")
    print("=" * 65)

def main():
    print("=" * 65)
    print("ERP Logistica - Carga de Dados de Teste")
    print("=" * 65 + "\n")

    empresa = Empresa.objects.first()
    if not empresa:
        print("[ERRO] Nenhuma empresa encontrada. Rode setup_inicial.py primeiro.")
        return

    print(f"Empresa: {empresa.nome_empresa}\n")

    limpar_dados_teste()
    motoristas = criar_motoristas(empresa)
    veiculos   = criar_veiculos(empresa, motoristas)
    clientes   = criar_clientes(empresa)
    descargas  = criar_descargas(empresa)
    transportes = criar_transportes(empresa, motoristas, veiculos, clientes, descargas)
    imprimir_resumo(transportes)

if __name__ == '__main__':
    main()
