# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidoitem',
            name='proposta',
            field=models.ForeignKey(to='base.PropostaItemPregao', null=True),
        ),
        migrations.AddField(
            model_name='propostaitempregao',
            name='valor_item_lote',
            field=models.DecimalField(default=1, verbose_name='Valor do Item do Lote', max_digits=12, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pedidoitem',
            name='resultado',
            field=models.ForeignKey(to='base.ResultadoItemPregao', null=True),
        ),
    ]
