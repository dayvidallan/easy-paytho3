# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-17 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_contrato_aplicacao_artigo_57'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='garantia_execucao_objeto',
            field=models.CharField(blank=True, help_text='Limitado a 5%. Deixar em branco caso n\xe3o se aplique.', max_length=50, null=True, verbose_name='Garantia de Execu\xe7\xe3o do Objeto'),
        ),
    ]
