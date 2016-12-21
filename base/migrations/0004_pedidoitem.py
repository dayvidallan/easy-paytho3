# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_preenche_base'),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.IntegerField(verbose_name='Quantidade')),
                ('pedido_em', models.DateTimeField(verbose_name='Pedido em')),
                ('item', models.ForeignKey(to='base.ItemSolicitacaoLicitacao')),
                ('pedido_por', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('resultado', models.ForeignKey(to='base.ResultadoItemPregao')),
                ('setor', models.ForeignKey(to='base.Setor')),
            ],
            options={
                'verbose_name': 'Pedido do Item',
                'verbose_name_plural': 'Pedidos do Item',
            },
        ),
    ]
