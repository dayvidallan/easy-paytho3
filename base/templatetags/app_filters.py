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


import math

# Tokens from 1000 and up
_PRONOUNCE = [
    'vigintillion',
    'novemdecillion',
    'octodecillion',
    'septendecillion',
    'sexdecillion',
    'quindecillion',
    'quattuordecillion',
    'tredecillion',
    'duodecillion',
    'undecillion',
    'decillion',
    'nonillion',
    'octillion',
    'septillion',
    'sextillion',
    'quintillion',
    'quadrillion',
    'trillion',
    'billion',
    'million',
    'milhões',
    ''
]

# Tokens up to 90
_SMALL = {
    '0' : '',
    '1' : 'um',
    '2' : 'dois',
    '3' : 'três',
    '4' : 'quatro',
    '5' : 'cinco',
    '6' : 'seis',
    '7' : 'sete',
    '8' : 'oito',
    '9' : 'nove',
    '10' : 'dez',
    '11' : 'onze',
    '12' : 'dose',
    '13' : 'treze',
    '14' : 'quatorze',
    '15' : 'quinze',
    '16' : 'dezesseis',
    '17' : 'dezessete',
    '18' : 'dezoito',
    '19' : 'dezenove',
    '20' : 'vinte',
    '30' : 'trinta',
    '40' : 'quarenta',
    '50' : 'cinquenta',
    '60' : 'sessenta',
    '70' : 'setenta',
    '80' : 'oitenta',
    '90' : 'noventa'
}

def get_num(num):
    '''Get token <= 90, return '' if not matched'''
    return _SMALL.get(num, '')

def triplets(l):
    '''Split list to triplets. Pad last one with '' if needed'''
    res = []
    for i in range(int(math.ceil(len(l) / 3.0))):
        sect = l[i * 3 : (i + 1) * 3]
        if len(sect) < 3: # Pad last section
            sect += [''] * (3 - len(sect))
        res.append(sect)
    return res

def norm_num(num):
    """Normelize number (remove 0's prefix). Return number and string"""
    n = int(num)
    return n, str(n)

def small2eng(num):
    '''English representation of a number <= 999'''
    n, num = norm_num(num)
    hundred = ''
    ten = ''
    if len(num) == 3: # Got hundreds
        hundred = get_num(num[0]) + ' hundred'
        num = num[1:]
        n, num = norm_num(num)
    if (n > 20) and (n != (n / 10 * 10)): # Got ones
        tens = get_num(num[0] + '0')
        ones = get_num(num[1])
        ten = tens + ' ' + ones
    else:
        ten = get_num(num)
    if hundred and ten:
        return hundred + ' ' + ten
        #return hundred + ' and ' + ten
    else: # One of the below is empty
        return hundred + ten

def num2eng(num):
    '''English representation of a number'''
    num = str(long(num)) # Convert to string, throw if bad number
    if (len(num) / 3 >= len(_PRONOUNCE)): # Sanity check
        raise ValueError('Number too big')

    if num == '0': # Zero is a special case
        return 'zero '

    # Create reversed list
    x = list(num)
    x.reverse()
    pron = [] # Result accumolator
    ct = len(_PRONOUNCE) - 1 # Current index
    for a, b, c in triplets(x): # Work on triplets
        p = small2eng(c + b + a)
        if p:
            pron.append(p + ' ' + _PRONOUNCE[ct])
        ct -= 1
    # Create result
    pron.reverse()
    return ', '.join(pron)

if __name__ == '__main__':

    numbers = [1.37, 0.07, 123456.00, 987654.33]
    for number in numbers:
        dollars, cents = [int(num) for num in str(number).split(".")]

        dollars = num2eng(dollars)
        if dollars.strip() == "um":
            dollars = dollars + "real e "
        else:
            dollars = dollars + "reais e "

        cents = num2eng(cents) + "centavos"
        print dollars + cents


@register.filter(is_safe=True)
def format_numero_extenso(num):
    dollars, cents = str(num).split(".")
    dollars = num2eng(dollars)
    if dollars.strip() == "um":
        dollars = dollars + "real e "
    else:
        dollars = dollars + "reais e "

    cents = num2eng(cents) + "centavos"
    return dollars + cents

