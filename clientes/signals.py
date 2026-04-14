"""Signal para gerar o código do cliente automaticamente."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Cliente


@receiver(pre_save, sender=Cliente)
def gerar_codigo_cliente(sender, instance, **kwargs):
    """Gera código sequencial CLI00001 se não informado."""
    if not instance.codigo_cliente:
        ultimo = Cliente.objects.order_by('codigo_cliente').last()
        if ultimo:
            try:
                numero = int(ultimo.codigo_cliente.replace('CLI', '')) + 1
            except (ValueError, AttributeError):
                numero = 1
        else:
            numero = 1
        instance.codigo_cliente = f'CLI{numero:05d}'
