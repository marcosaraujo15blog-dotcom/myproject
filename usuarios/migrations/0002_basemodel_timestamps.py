import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
        ('empresas', '0002_basemodel_timestamps'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='data_criacao',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='usuario',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name='Atualizado em',
            ),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['tipo_usuario'], name='usuario_tipo_idx'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['empresa', 'tipo_usuario'], name='usuario_empresa_tipo_idx'),
        ),
    ]
