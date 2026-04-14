import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportes', '0002_remove_transporte_empresa_descarga_and_more'),
    ]

    operations = [
        # Renomeia timestamps de Transporte para o padrão BaseModel
        migrations.RenameField(
            model_name='transporte',
            old_name='criado_em',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='transporte',
            old_name='atualizado_em',
            new_name='updated_at',
        ),
        # Adiciona timestamps em Entrega (herda TimeStampedModel)
        migrations.AddField(
            model_name='entrega',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Criado em',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='entrega',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
        # Indexes de Transporte
        migrations.AddIndex(
            model_name='transporte',
            index=models.Index(fields=['data_transporte'], name='transp_data_idx'),
        ),
        migrations.AddIndex(
            model_name='transporte',
            index=models.Index(fields=['status_transporte'], name='transp_status_idx'),
        ),
        migrations.AddIndex(
            model_name='transporte',
            index=models.Index(fields=['status_pagamento'], name='transp_status_pag_idx'),
        ),
        migrations.AddIndex(
            model_name='transporte',
            index=models.Index(fields=['empresa', 'data_transporte'], name='transp_empresa_data_idx'),
        ),
        migrations.AddIndex(
            model_name='transporte',
            index=models.Index(fields=['empresa', 'status_pagamento'], name='transp_empresa_pag_idx'),
        ),
        # Indexes de Entrega
        migrations.AddIndex(
            model_name='entrega',
            index=models.Index(fields=['transporte', 'ordem_entrega'], name='entrega_transp_ordem_idx'),
        ),
        migrations.AddIndex(
            model_name='entrega',
            index=models.Index(fields=['cliente'], name='entrega_cliente_idx'),
        ),
    ]
