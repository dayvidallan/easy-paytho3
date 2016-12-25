# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20161225_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregao',
            name='data_homologacao',
            field=models.DateField(null=True, verbose_name='Data da Homologa\xe7\xe3o'),
        ),
    ]
