# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_documentosolicitacao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fornecedor',
            name='ramo_atividade',
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='agencia',
            field=models.CharField(max_length=50, null=True, verbose_name='Ag\xeancia', blank=True),
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='banco',
            field=models.CharField(max_length=200, null=True, verbose_name='Banco', blank=True),
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='conta',
            field=models.CharField(max_length=200, null=True, verbose_name='Conta', blank=True),
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='email',
            field=models.EmailField(default='sss@ff.com', max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='telefones',
            field=models.CharField(default='2000-5588', max_length=300, verbose_name='Telefones'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='RamoAtividade',
        ),
    ]
