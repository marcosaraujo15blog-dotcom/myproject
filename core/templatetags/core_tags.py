"""Template tags e filtros customizados do sistema."""

from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter
def brl(value):
    """Formata valor como moeda brasileira: R$ 1.234,56"""
    try:
        return f'R$ {number_format(value, decimal_pos=2, use_l10n=True)}'
    except (ValueError, TypeError):
        return 'R$ 0,00'


@register.filter
def cpf_format(value):
    """Formata CPF: 000.000.000-00"""
    v = str(value).strip().replace('.', '').replace('-', '')
    if len(v) == 11:
        return f'{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}'
    return value


@register.filter
def cnpj_format(value):
    """Formata CNPJ: 00.000.000/0001-00"""
    v = str(value).strip().replace('.', '').replace('/', '').replace('-', '')
    if len(v) == 14:
        return f'{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}'
    return value


@register.simple_tag(takes_context=True)
def active_menu(context, url_name):
    """Retorna 'active' se a URL atual corresponde ao menu item."""
    request = context.get('request')
    if request and hasattr(request, 'resolver_match'):
        current = request.resolver_match.url_name or ''
        current_ns = request.resolver_match.namespace or ''
        full = f'{current_ns}:{current}' if current_ns else current
        if url_name in full or full.startswith(url_name.split(':')[0]):
            return 'active'
    return ''
