# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20160727_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregao',
            name='cabecalho_ata',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Cabe\xe7alho da Ata de Registro de Pre\xe7o', blank=True),
        ),
    ]
