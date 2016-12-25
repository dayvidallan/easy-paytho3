# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_pregao_data_homologacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregao',
            name='ordenador_despesa',
            field=models.ForeignKey(verbose_name='Ordenador de Despesa', to='base.PessoaFisica', null=True),
        ),
    ]
