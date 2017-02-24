# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-24 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20170224_1403'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitacaolicitacao',
            name='liberada_compra',
        ),
        migrations.AddField(
            model_name='ataregistropreco',
            name='liberada_compra',
            field=models.BooleanField(default=False, verbose_name='Liberada para Compra'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='liberada_compra',
            field=models.BooleanField(default=False, verbose_name='Liberada para Compra'),
        ),
    ]
