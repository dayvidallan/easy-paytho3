# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_anexocontrato'),
    ]

    operations = [
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='motivo_rejeicao',
            field=models.CharField(max_length=1000, null=True, verbose_name='Motivo da Rejei\xe7\xe3o', blank=True),
        ),
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='rejeitado_em',
            field=models.DateTimeField(null=True, verbose_name='Rejeitado em'),
        ),
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='rejeitado_por',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='itempesquisamercadologica',
            name='situacao',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
    ]
