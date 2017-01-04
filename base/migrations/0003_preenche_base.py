# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import Group
from base.models import ModalidadePregao, CriterioPregao, TipoPregao, User, PessoaFisica, Setor, Secretaria


def preenche_base(apps, schema_editor):
    grupo_secretaria = Group.objects.get_or_create(name=u'Secretaria')[0]
    grupo_pregao = Group.objects.get_or_create(name=u'Licitação')[0]
    grupo_compras = Group.objects.get_or_create(name=u'Compras')[0]
    grupo_juridico = Group.objects.get_or_create(name=u'Jurídico')[0]
    grupo_protocolo = Group.objects.get_or_create(name=u'Protocolo')[0]


    modalidade = ModalidadePregao.objects.get_or_create(nome=u'Pregão Presencial')[0]
    #modalidade = ModalidadePregao.objects.get_or_create(nome=u'Pregão Eletrônico')[0]
    modalidade = ModalidadePregao.objects.get_or_create(nome=u'Carta Convite')[0]
    modalidade = ModalidadePregao.objects.get_or_create(nome=u'Tomada de Preço')[0]
    modalidade = ModalidadePregao.objects.get_or_create(nome=u'Concorrência Pública')[0]

    criterio1 = CriterioPregao.objects.get_or_create(nome=u'Por Item')[0]
    criterio2 = CriterioPregao.objects.get_or_create(nome=u'Por Lote')[0]
    #criterio3 = CriterioPregao.objects.get_or_create(nome=u'Por Grupo de Itens')[0]

    tipo1 = TipoPregao.objects.get_or_create(nome=u'Menor Preço')[0]
    #tipo2 = TipoPregao.objects.get_or_create(nome=u'Maior Desconto')[0]

    secretaria = Secretaria.objects.get_or_create(nome=u'Secretaria de Planejamento', sigla=u'SEMPLA')[0]
    setor_licitacao = Setor.objects.get_or_create(nome=u'Setor de Licitação', sigla=u'SECLIC', secretaria=secretaria)[0]
    root = User.objects.get_or_create(username=u'admin',is_active=True,is_superuser=True, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
    pessoa = PessoaFisica()
    pessoa.nome = u'Administrador'
    pessoa.cpf = u'12345678900'
    pessoa.sexo = PessoaFisica.SEXO_MASCULINO
    pessoa.setor = setor_licitacao
    pessoa.user = root
    pessoa.save()

        #PessoaFisica.objects.create(nome=u'Administrador', cpf=u'12345678900',sexo=PessoaFisica.SEXO_MASCULINO, setor=setor_licitacao, user=root)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_popula_estado_e_municipio'),
    ]

    operations = [
        migrations.RunPython(preenche_base),
    ]







