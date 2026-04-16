from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0003_timestamps'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='cod_femsa',
            field=models.CharField(
                blank=True, default='', max_length=10, verbose_name='Cod FEMSA Cliente'
            ),
        ),
    ]
