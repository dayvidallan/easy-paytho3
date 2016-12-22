# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.AddField(
            model_name='lanceitemrodadapregao',
            name='ordem_lance',
            field=models.IntegerField(default=1, verbose_name='Ordem'),
            preserve_default=False,
        ),
    ]
