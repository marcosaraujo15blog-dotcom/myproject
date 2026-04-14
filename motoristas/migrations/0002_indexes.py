from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motoristas', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='motorista',
            index=models.Index(fields=['nome'], name='motorista_nome_idx'),
        ),
        migrations.AddIndex(
            model_name='motorista',
            index=models.Index(fields=['status'], name='motorista_status_idx'),
        ),
        migrations.AddIndex(
            model_name='motorista',
            index=models.Index(fields=['empresa', 'status'], name='motorista_empresa_status_idx'),
        ),
    ]
