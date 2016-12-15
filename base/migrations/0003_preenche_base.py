# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import Group
from base.models import ModalidadePregao, CriterioPregao, TipoPregao


def preenche_base(apps, schema_editor):
    grupo_secretaria = Group.objects.get_or_create(name=u'Secretaria')[0]
    grupo_pregao = Group.objects.get_or_create(name=u'Licitação')[0]
    grupo_compras = Group.objects.get_or_create(name=u'Compras')[0]
    grupo_juridico = Group.objects.get_or_create(name=u'Jurídico')[0]
    grupo_protocolo = Group.objects.get_or_create(name=u'Protocolo')[0]


    modalidade = ModalidadePregao.objects.get_or_create(nome=u'Presencial')[0]

    criterio1 = CriterioPregao.objects.get_or_create(nome=u'Por Item')[0]
    criterio2 = CriterioPregao.objects.get_or_create(nome=u'Por Lote')[0]

    tipo1 = TipoPregao.objects.get_or_create(nome=u'Menor Preço')[0]
    tipo2 = TipoPregao.objects.get_or_create(nome=u'Maior Desconto')[0]

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_popula_estado_e_municipio'),
    ]

    operations = [
        migrations.RunPython(preenche_base),
    ]







