import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='empresa',
            old_name='data_criacao',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='empresa',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['status'], name='empresa_status_idx'),
        ),
        migrations.AddIndex(
            model_name='empresa',
            index=models.Index(fields=['cnpj'], name='empresa_cnpj_idx'),
        ),
    ]
