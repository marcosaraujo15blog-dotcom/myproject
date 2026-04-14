"""Signal para geração automática do número do transporte (TR00001)."""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Transporte


@receiver(pre_save, sender=Transporte)
def gerar_numero_transporte(sender, instance, **kwargs):
    """Gera número sequencial TR00001 para novos transportes."""
    if not instance.numero_transporte:
        ultimo = Transporte.objects.order_by('numero_transporte').last()
        if ultimo and ultimo.numero_transporte:
            try:
                numero = int(ultimo.numero_transporte.replace('TR', '')) + 1
            except (ValueError, AttributeError):
                numero = 1
        else:
            numero = 1
        instance.numero_transporte = f'TR{numero:05d}'
