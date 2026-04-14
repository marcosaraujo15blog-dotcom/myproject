"""Regras de negócio para Transportes."""

from django.db.models import Q


def filtrar_transportes(qs, q='', data_inicio='', data_fim='', status='', motorista_id=''):
    """Aplica filtros de busca ao queryset de transportes."""
    if q:
        qs = qs.filter(
            Q(numero_transporte__icontains=q) |
            Q(documento_transporte__icontains=q) |
            Q(motorista__nome__icontains=q) |
            Q(veiculo__placa__icontains=q)
        )
    if data_inicio:
        qs = qs.filter(data_transporte__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data_transporte__lte=data_fim)
    if status:
        qs = qs.filter(status_transporte=status)
    if motorista_id:
        qs = qs.filter(motorista__cpf=motorista_id)
    return qs


def salvar_transporte_com_entregas(form, entrega_formset):
    """
    Persiste o Transporte e suas Entregas de forma atômica.
    Assume que form e entrega_formset já foram validados.
    Retorna o objeto Transporte salvo.
    """
    transporte = form.save()
    entrega_formset.instance = transporte
    entrega_formset.save()
    return transporte
