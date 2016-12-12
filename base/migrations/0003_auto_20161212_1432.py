# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_popula_estado_e_municipio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaolicitacao',
            name='prazo_aberto',
            field=models.NullBooleanField(default=False, verbose_name='Aberto para Recebimento de Pesquisa'),
        ),
    ]
