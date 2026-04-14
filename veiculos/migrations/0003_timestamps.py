import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('veiculos', '0002_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='veiculo',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Criado em',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='veiculo',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
    ]
