# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.TextField(max_length=500, verbose_name='Nome do Arquivo')),
                ('cadastrado_em', models.DateTimeField(null=True, verbose_name='Cadastrado Em', blank=True)),
                ('documento', models.FileField(upload_to=base.models.upload_path_documento, null=True, verbose_name='Documento', blank=True)),
                ('cadastrado_por', models.ForeignKey(related_name='documento_cadastrado_por', to=settings.AUTH_USER_MODEL, null=True)),
                ('solicitacao', models.ForeignKey(verbose_name='Solicita\xe7\xe3o', to='base.SolicitacaoLicitacao')),
            ],
            options={
                'verbose_name': 'Documento da Solicita\xe7\xe3o',
                'verbose_name_plural': 'Documentos da Solicita\xe7\xe3o',
            },
        ),
    ]
