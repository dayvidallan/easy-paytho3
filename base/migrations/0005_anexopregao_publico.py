# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20170105_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='anexopregao',
            name='publico',
            field=models.BooleanField(default=False, help_text='Se sim, este documento ser\xe1 exibido publicamente', verbose_name='Documento P\xfablico'),
        ),
    ]
