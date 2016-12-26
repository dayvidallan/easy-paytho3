# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_pregao_ordenador_despesa'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregao',
            name='eh_ata_registro_preco',
            field=models.BooleanField(default=True, verbose_name='Ata de Registro de Pre\xe7o?'),
        ),
    ]
