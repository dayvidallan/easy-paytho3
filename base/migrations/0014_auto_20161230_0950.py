# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20161230_0833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contrato',
            name='data_fim',
            field=models.DateField(null=True, verbose_name='Data de Vencimento'),
        ),
    ]
