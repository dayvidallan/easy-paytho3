# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_dotacaoorcamentaria_ordemcompra'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracao',
            name='ordenador_despesa',
            field=models.ForeignKey(verbose_name='Ordenador de Despesa', to='base.PessoaFisica', null=True),
        ),
        migrations.AddField(
            model_name='pregao',
            name='data_adjudicacao',
            field=models.DateField(null=True, verbose_name='Data da Adjudica\xe7\xe3o'),
        ),
    ]
