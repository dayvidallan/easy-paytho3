# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-01-24 08:37
from __future__ import unicode_literals

import base.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0115_auto_20190111_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaolicitacao',
            name='termo_referencia',
            field=models.FileField(blank=True, null=True, upload_to=base.models.upload_path_documento, verbose_name='Termo de Refer\xeancia'),
        ),
    ]