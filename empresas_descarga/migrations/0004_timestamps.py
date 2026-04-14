import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas_descarga', '0003_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresadescarga',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Criado em',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='empresadescarga',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
    ]
