# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20161229_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaolicitacao',
            name='liberada_compra',
            field=models.BooleanField(default=False, verbose_name='Liberada para Compra'),
        ),
    ]
