# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_popula_estado_e_municipio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemsolicitacaolicitacao',
            name='codigo',
            field=models.ForeignKey(to='base.MaterialConsumo'),
        ),
    ]
