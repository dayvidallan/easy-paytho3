# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemcompra',
            name='numero',
            field=models.CharField(max_length=200, verbose_name='N\xfamero da Ordem'),
        ),
        migrations.AlterField(
            model_name='resultadoitempregao',
            name='situacao',
            field=models.CharField(max_length=100, verbose_name='Situa\xe7\xe3o', choices=[('Classificado', 'Classificado'), ('Inabilitado', 'Inabilitado'), ('Desclassificado', 'Desclassificado')]),
        ),
    ]
