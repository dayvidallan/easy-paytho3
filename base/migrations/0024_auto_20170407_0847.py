# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-07 08:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_configuracao_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membrocomissaolicitacao',
            name='funcao',
            field=models.CharField(choices=[('Apoio', 'Apoio'), ('Membro da Equipe do Preg\xe3o', 'Membro da Equipe do Preg\xe3o'), ('Pregoeiro', 'Pregoeiro'), ('Presidente', 'Presidente')], default='Apoio', max_length=100, verbose_name='Fun\xe7\xe3o'),
        ),
    ]
