# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20161223_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propostaitempregao',
            name='valor_item_lote',
            field=models.DecimalField(null=True, verbose_name='Valor do Item do Lote', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
