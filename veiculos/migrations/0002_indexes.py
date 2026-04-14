from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veiculos', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='veiculo',
            index=models.Index(fields=['status'], name='veiculo_status_idx'),
        ),
        migrations.AddIndex(
            model_name='veiculo',
            index=models.Index(fields=['modelo'], name='veiculo_modelo_idx'),
        ),
        migrations.AddIndex(
            model_name='veiculo',
            index=models.Index(fields=['empresa', 'status'], name='veiculo_empresa_status_idx'),
        ),
    ]
