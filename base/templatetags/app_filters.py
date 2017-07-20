# -*- coding: utf-8 -*-
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


# -*- coding: utf-8 -*-


# Autor: Fabiano Weimar dos Santos (xiru)
# Correcao em 20080407: Gustavo Henrique Cervi (100:"cento") => (1:"cento')
# Correcao em 20100311: Luiz Fernando B. Vital adicionado {0:""} ao ext[0], pois dava KeyError: 0 em números como 200, 1200, 300, etc.
# Modificação para tradução de moeda

import sys

ext = [{1:"um", 2:"dois", 3:"três", 4:"quatro", 5:"cinco", 6:"seis", 7:"sete", 8:"oito", 9:"nove", 10:"dez", 11:"onze", 12:"doze",13:"treze", 14:"quatorze", 15:"quinze",
16:"dezesseis", 17:"dezessete", 18:"dezoito", 19:"dezenove"},
{2:"vinte", 3:"trinta", 4:"quarenta", 5:"cinquenta", 6:"sessenta", 7:"setenta", 8:"oitenta", 9:"noventa"},
{1:"cento", 2:"duzentos", 3:"trezentos", 4:"quatrocentos", 5:"quinhentos", 6:"seiscentos", 7:"setecentos", 8:"oitocentos", 9:"novecentos"}]

und = ['', ' mil', (' milhão', ' milhões'), (' bilhão', ' bilhões'), (' trilhão', ' trilhões')]

def cent(s, grand):
    s = '0' * (3 - len(s)) + s
    if s == '000':
        return ''
    if s == '100':
        return 'cem'
    ret = ''
    dez = s[1] + s[2]
    if s[0] != '0':
        ret += ext[2][int(s[0])]
        if dez != '00':
            ret += ' e '
        else:
            return ret + (type(und[grand]) == type(()) and (int(s) > 1 and und[grand][1] or und[grand][0]) or und[grand])
    if int(dez) < 20:
        ret += ext[0][int(dez)]
    else:
        if s[1] != '0':
            ret += ext[1][int(s[1])]
            if s[2] != '0':
                ret += ' e ' + ext[0][int(s[2])]

    return ret + (type(und[grand]) == type(()) and (int(s) > 1 and und[grand][1] or und[grand][0]) or und[grand])

def extenso(reais,centavos):
    ret = []
    grand = 0
    if (int(centavos)==0):
        ret.append('zero centavos')
    elif (int(centavos)==1):
        ret.append('um centavo')
    else:
        ret.append(cent(centavos,0)+' centavos')
    if (int(reais)==0):
        ret.append('zero reais')
        ret.reverse()
        return ' e '.join([r for r in ret if r])
    elif (int(reais)==1):
        ret.append('um real')
        ret.reverse()
        return ' e '.join([r for r in ret if r])
    while reais:
        s = reais[-3:]
        reais = reais[:-3]
        if (grand == 0):
            ret.append(cent(s, grand)+' reais')
        else:
            ret.append(cent(s, grand))
        grand += 1
    ret.reverse()
    print ">>>>>>>>>>>", ret
    lista = list()
    contador = 1

    total = len(ret)
    for item in ret:
        if item != 'zero centavos':
            lista.append(item)
        if contador == 2 and len(item) == 6:
            pass
        else:
            if total == contador or item != 'zero centavos' or item == ' reais':
                pass
            else:
                lista.append('e')
        contador += 1
    print ' e '.join(lista)
    return ' e '.join(lista)

    return ' e '.join([r for r in ret if r])



@register.filter(is_safe=True)
def format_numero_extenso(num):
    n = str(format_money(num))
    try:
        reais,centavos = n.split(',')
        reais = reais.replace('.', '')
    except:
        print 'Erro ao parsear o numero informado!'

    print n
    return extenso(reais,centavos)

