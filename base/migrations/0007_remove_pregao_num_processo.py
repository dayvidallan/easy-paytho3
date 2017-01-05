# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20170105_0932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pregao',
            name='num_processo',
        ),
    ]
