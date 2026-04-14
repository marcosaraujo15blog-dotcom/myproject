from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empresas_descarga', '0002_empresadescarga_id_alter_empresadescarga_cnpj_cpf'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='empresadescarga',
            index=models.Index(fields=['nome'], name='empdescar_nome_idx'),
        ),
        migrations.AddIndex(
            model_name='empresadescarga',
            index=models.Index(fields=['cnpj_cpf'], name='empdescar_cnpj_cpf_idx'),
        ),
        migrations.AddIndex(
            model_name='empresadescarga',
            index=models.Index(fields=['empresa'], name='empdescar_empresa_idx'),
        ),
    ]
