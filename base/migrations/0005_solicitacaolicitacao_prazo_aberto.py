# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_pregao_cabecalho_ata'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaolicitacao',
            name='prazo_aberto',
            field=models.BooleanField(default=False, verbose_name='Aberto para Recebimento de Pesquisa'),
        ),
    ]
