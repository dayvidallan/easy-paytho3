# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20161223_1012'),
    ]

    operations = [
        migrations.CreateModel(
            name='DotacaoOrcamentaria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('projeto_atividade_num', models.TextField(verbose_name='N\xfamero do Projeto de Atividade')),
                ('projeto_atividade_descricao', models.TextField(verbose_name='Descri\xe7\xe3o do Projeto de Atividade')),
                ('programa_num', models.TextField(verbose_name='N\xfamero do Programa')),
                ('programa_descricao', models.TextField(verbose_name='Descri\xe7\xe3o do Programa')),
                ('fonte_num', models.TextField(verbose_name='N\xfamero da Fonte')),
                ('fonte_descricao', models.TextField(verbose_name='Descri\xe7\xe3o da Fonte')),
                ('elemento_despesa_num', models.TextField(verbose_name='N\xfamero do Elemento de Despesa')),
                ('elemento_despesa_descricao', models.TextField(verbose_name='Descri\xe7\xe3o do Elemento de Despesa')),
            ],
            options={
                'verbose_name': 'Dota\xe7\xe3o Or\xe7ament\xe1ria',
                'verbose_name_plural': 'Dota\xe7\xf5es Or\xe7ament\xe1rias',
            },
        ),
        migrations.CreateModel(
            name='OrdemCompra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.IntegerField(verbose_name='N\xfamero da Ordem')),
                ('data', models.DateField(verbose_name='Data')),
                ('dotacao_orcamentaria', models.ForeignKey(to='base.DotacaoOrcamentaria', null=True)),
                ('solicitacao', models.ForeignKey(to='base.SolicitacaoLicitacao')),
            ],
            options={
                'verbose_name': 'Ordem de Compra',
                'verbose_name_plural': 'Ordens de Compra',
            },
        ),
    ]
