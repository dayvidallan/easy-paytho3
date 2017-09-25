# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-25 13:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0093_aditivo_valor_atual'),
    ]

    operations = [
        migrations.AddField(
            model_name='aditivo',
            name='indice_total_contrato',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='\xcdndice Total'),
        ),
    ]
