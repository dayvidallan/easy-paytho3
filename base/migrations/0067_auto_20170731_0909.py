# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-31 09:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0066_auto_20170731_0843'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aditivo',
            options={'verbose_name': 'Aditivo de Contrato', 'verbose_name_plural': 'Aditivos de Contrato'},
        ),
        migrations.RemoveField(
            model_name='aditivo',
            name='de_fiscal',
        ),
        migrations.AddField(
            model_name='aditivo',
            name='indice',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='\xcdndice de Reajuste'),
        ),
        migrations.AddField(
            model_name='aditivo',
            name='tipo',
            field=models.CharField(blank=True, choices=[('Acr\xe9scimo de Quantitativos', 'Acr\xe9scimo de Quantitativos'), ('Acr\xe9scimo de Valor', 'Acr\xe9scimo de Valor'), ('Reajuste Econ\xf4mico-financeiro', 'Reajuste Econ\xf4mico-financeiro'), ('Supress\xe3o de Quantitativo', 'Supress\xe3o de Quantitativo'), ('Supress\xe3o de Valor', 'Supress\xe3o de Valor')], max_length=50, null=True, verbose_name='Tipo de Aditivo'),
        ),
        migrations.AlterField(
            model_name='aditivo',
            name='contrato',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aditivos_set', to='base.Contrato'),
        ),
        migrations.AlterField(
            model_name='aditivo',
            name='data_fim',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Vencimento'),
        ),
        migrations.AlterField(
            model_name='aditivo',
            name='data_inicio',
            field=models.DateField(blank=True, null=True, verbose_name='Data de In\xedcio'),
        ),
        migrations.AlterField(
            model_name='aditivo',
            name='valor',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
