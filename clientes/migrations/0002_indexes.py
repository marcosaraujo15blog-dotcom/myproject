from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['nome_femsa'], name='cliente_nome_femsa_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['nome_mercado'], name='cliente_nome_mercado_idx'),
        ),
        migrations.AddIndex(
            model_name='cliente',
            index=models.Index(fields=['empresa', 'valor_tipo'], name='cliente_empresa_tipo_idx'),
        ),
    ]
