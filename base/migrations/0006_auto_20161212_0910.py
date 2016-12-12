# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_solicitacaolicitacao_prazo_aberto'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='aprovado',
            field=models.BooleanField(default=False, verbose_name='Aprovado'),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='avaliado_em',
            field=models.DateTimeField(null=True, verbose_name='Avaliado Em', blank=True),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='avaliado_por',
            field=models.ForeignKey(related_name='pedido_avaliado_por', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='itemquantidadesecretaria',
            name='justificativa_reprovacao',
            field=models.CharField(max_length=1000, null=True, verbose_name='Motivo da Nega\xe7\xe3o do Pedido', blank=True),
        ),
    ]
