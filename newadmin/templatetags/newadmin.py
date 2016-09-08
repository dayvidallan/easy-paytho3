# coding: utf-8

import os

from django import template
from django.template.defaultfilters import filesizeformat
from django.utils.safestring import mark_safe
from bootstrapform.templatetags.bootstrap import bootstrap_inline as bootstrapform_bootstrap_inline
from bootstrapform.templatetags.bootstrap import bootstrap_horizontal as bootstrapform_bootstrap_horizontal
from django.utils.translation import ugettext as _

register = template.Library()


def _convert_selects_to_bootstrap(out):
    if '<select' in out and 'form-control' not in out:
        out = out.replace(
            '<select ',
            '<select class="form-control" ')
    elif 'class="vIntegerField form-control"' in out and 'type="number"' not in out:
        out = out.replace(
            'class="vIntegerField form-control"',
            'class="vIntegerField form-control" type="number"')
    return out


@register.filter
def bootstrap_inline(element):  # inlines
    return mark_safe(_convert_selects_to_bootstrap(bootstrapform_bootstrap_inline(element)))


@register.filter
def bootstrap_horizontal(element):  # change-form
    out = bootstrapform_bootstrap_horizontal(element)
    if hasattr(element, 'field') and element.field.required:  # é um field, e não um form.
        element.field.widget.attrs['class'] = element.field.widget.attrs.get('class', '') + ' required'
        out = out.replace('<label class="', '<label class="required ')
    return mark_safe(_convert_selects_to_bootstrap(out))


@register.filter
def bootstrap_result_item(element):
    if '<select' in element and 'form-control' not in element:
        element = element.replace(
            '<select id', 
            '<select class="form-control" id')
    elif 'class="vIntegerField"' in element and 'type="number"' not in element:
        element = element.replace(
            'class="vIntegerField"',
            'class="vIntegerField form-control" type="number"')

    icon_true = u'<img src="/static/admin/img/icon-yes.gif" alt="True" />'
    icon_false = u'<img src="/static/admin/img/icon-no.gif" alt="False" />'
    icon_unknown = u'<img src="/static/admin/img/icon-unknown.gif" alt="None" />'
    if icon_true in element:
        element = element.replace(icon_true, u'<span class="text-success">%s</span>' % _(u'Yes'))
    elif icon_false in element:
        element = element.replace(icon_false, u'<span class="text-danger">%s</span>' % _(u'No'))
    elif icon_unknown in element:
        element = element.replace(icon_unknown, u'<span class="text-muted">Vazio</span>')
    
    return mark_safe(element)


@register.filter
def format(element):
    icon_true = u'<img src="/static/admin/img/icon-yes.gif" alt="True" />'
    icon_false = u'<img src="/static/admin/img/icon-no.gif" alt="False" />'
    icon_unknown = u'<img src="/static/admin/img/icon-unknown.gif" alt="None" />'
    if icon_true in element:
        element = element.replace(icon_true, u'<span class="label label-success">%s</span>' % _(u'Yes'))
    elif icon_false in element:
        element = element.replace(icon_false, u'<span class="label label-danger">%s</span>' % _(u'No'))
    elif icon_unknown in element:
        element = element.replace(icon_unknown, u'<span class="label label-default">%s</span>' % _(u'Unknown'))
    return mark_safe(element)


@register.filter
def filename(path):
    return os.path.split(path)[-1]

@register.filter
def field_filesizeformat(field):
    """Filter criado para evitar OSError quando não existe o arquivo em disco, o que é comum no ambiente de
    desenvolvimento"""
    try:
        return filesizeformat(field.size)
    except OSError:
        return u''


@register.filter
def getval(value, key):
    try:
        return value[key]
    except TypeError:
        return getattr(value, key)


@register.filter
def show_version_diff(version):
    import json
    import reversion
    try:
        previous_version = reversion.get_for_object(version.object).filter(
            revision__date_created__lt=version.revision.date_created).order_by('-revision__date_created')[0]
    except IndexError:
        return u'Versão inicial'

    old = json.loads(previous_version.serialized_data)[0]['fields']
    new = json.loads(version.serialized_data)[0]['fields']

    out = [u'<ul>']
    keys = set(old.keys() + new.keys())
    for key in sorted(keys):
        old_value, new_value = old.get(key, ''), new.get(key, '')
        if old_value != new_value:
            out.append(u'<li><strong class="text-muted">%s:</strong> <span class="text-danger">%s</span> &rarr; '
                       u'<span class="text-success">%s</span></li>' % (key, old_value, new_value))
    out.append(u'</ul>')
    return mark_safe(u''.join(out))

@register.filter
def validjs_symbol(str):
    return str.replace("-", "")