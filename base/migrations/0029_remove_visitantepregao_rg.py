# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-05 11:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_visitantepregao'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitantepregao',
            name='rg',
        ),
    ]
