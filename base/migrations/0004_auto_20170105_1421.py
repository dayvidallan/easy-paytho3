# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fornecedor',
            name='cnpj',
            field=models.CharField(help_text='Utilize pontos e tra\xe7os.', unique=True, max_length=255, verbose_name='CNPJ/CPF'),
        ),
    ]
