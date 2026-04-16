from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transportes', '0003_basemodel_timestamps'),
    ]

    operations = [
        migrations.AddField(
            model_name='transporte',
            name='cef_pagamento',
            field=models.CharField(
                blank=True, default='', max_length=10, verbose_name='CEF - Pagamento'
            ),
        ),
    ]
