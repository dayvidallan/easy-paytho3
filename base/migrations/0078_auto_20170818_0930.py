# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-18 09:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0077_participantepregao_credenciado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pregao',
            name='situacao',
            field=models.CharField(choices=[('Publicado', 'Publicado'), ('Deserto', 'Deserto'), ('Fracassado', 'Fracassado'), ('Suspenso', 'Suspenso'), ('Adjudicado', 'Adjudicado'), ('Homologado', 'Homologado'), ('Revogado', 'Revogado')], default='Publicado', max_length=50, verbose_name='Situa\xe7\xe3o'),
        ),
    ]