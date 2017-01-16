# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20170116_1307'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itempesquisamercadologica',
            old_name='situacao',
            new_name='ativo',
        ),
    ]
