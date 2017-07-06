from django import template

register = template.Library()

def split_thousands(value, sep='.'):
    """
    split_thousands('1000000000') -> '1.000.000.000'
    """
    if not isinstance(value, basestring):
        value = str(value)
    negativo = False
    if '-' in value:
        value = value.replace('-','')
        negativo = True
    if len(value) <= 3:
        if negativo:
            return '-' + value
        else:
            return value
    if negativo:
        return '-' + split_thousands(value[:-3], sep) + sep + value[-3:]
    else:
        return split_thousands(value[:-3], sep) + sep + value[-3:]

@register.filter(is_safe=True)
def format_money(value):
    """
    format_money(1) -> '1,00'
    format_money(1000) -> '1.000,00'
    format_money(1000.99) -> '1.000,99'
    """
    value = str(value)
    if value == u'None':
        return u'-'
    if '.' in value:
        reais, centavos = value.split('.')
        if len(centavos) > 2:
            centavos = centavos[0:2]
    else:
        reais = value
        centavos = '00'
    reais = split_thousands(reais)
    return unicode(reais + ',' + centavos)


@register.filter(is_safe=True)
def format_quantidade(value):
    """
    format_money(1) -> '1,00'
    format_money(1000) -> '1.000,00'
    format_money(1000.99) -> '1.000,99'
    """
    value = str(value)

    if value == u'None':
        return u'-'
    if '.' in value:
        reais, centavos = value.split('.')
        if centavos != '00':
            return unicode(reais + ',' + centavos)
        else:
            return unicode(reais)
    return u'-'

