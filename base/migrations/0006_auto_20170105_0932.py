# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20170105_0908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='elemento_despesa_descricao',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='elemento_despesa_num',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='fonte_descricao',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='fonte_num',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='programa_descricao',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='programa_num',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='projeto_atividade_descricao',
        ),
        migrations.RemoveField(
            model_name='dotacaoorcamentaria',
            name='projeto_atividade_num',
        ),
        migrations.RemoveField(
            model_name='ordemcompra',
            name='dotacao_orcamentaria',
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='elemento_despesa_descricao',
            field=models.CharField(max_length=200, null=True, verbose_name='Descri\xe7\xe3o do Elemento de Despesa', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='elemento_despesa_num',
            field=models.CharField(max_length=200, null=True, verbose_name='N\xfamero do Elemento de Despesa', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='fonte_descricao',
            field=models.CharField(max_length=200, null=True, verbose_name='Descri\xe7\xe3o da Fonte', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='fonte_num',
            field=models.CharField(max_length=200, null=True, verbose_name='N\xfamero da Fonte', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='programa_descricao',
            field=models.CharField(max_length=200, null=True, verbose_name='Descri\xe7\xe3o do Programa', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='programa_num',
            field=models.CharField(max_length=200, null=True, verbose_name='N\xfamero do Programa', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='projeto_atividade_descricao',
            field=models.CharField(max_length=200, null=True, verbose_name='Descri\xe7\xe3o do Projeto de Atividade', blank=True),
        ),
        migrations.AddField(
            model_name='ordemcompra',
            name='projeto_atividade_num',
            field=models.CharField(max_length=200, null=True, verbose_name='N\xfamero do Projeto de Atividade', blank=True),
        ),
    ]
