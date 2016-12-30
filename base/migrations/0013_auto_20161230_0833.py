# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_solicitacaolicitacao_liberada_compra'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aditivo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordem', models.PositiveSmallIntegerField(default=0)),
                ('numero', models.CharField(help_text='No formato: 99999/9999', max_length=100, verbose_name='N\xfamero')),
                ('valor', models.DecimalField(null=True, max_digits=9, decimal_places=2, blank=True)),
                ('data_inicio', models.DateField(null=True, verbose_name='Data de In\xedcio', db_column='data_inicio', blank=True)),
                ('data_fim', models.DateField(null=True, verbose_name='Data de Vencimento', db_column='data_fim', blank=True)),
                ('de_prazo', models.BooleanField(default=False, verbose_name='Aditivo de Prazo')),
                ('de_valor', models.BooleanField(default=False, verbose_name='Aditivo de Valor')),
                ('de_fiscal', models.BooleanField(default=False, verbose_name='Aditivo de Fiscal')),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero', models.CharField(help_text='No formato: 99999/9999', max_length=100, verbose_name='N\xfamero')),
                ('valor', models.DecimalField(max_digits=12, decimal_places=2)),
                ('data_inicio', models.DateField(null=True, verbose_name='Data de In\xedcio')),
                ('data_fim', models.DateField(null=True, verbose_name='Data de Vencimento', db_column='data_fim')),
                ('continuado', models.BooleanField(default=False)),
                ('concluido', models.BooleanField(default=False)),
                ('suspenso', models.BooleanField(default=False)),
                ('cancelado', models.BooleanField(default=False)),
                ('motivo_cancelamento', models.TextField(blank=True)),
                ('dh_cancelamento', models.DateTimeField(null=True, blank=True)),
                ('pregao', models.ForeignKey(to='base.Pregao')),
                ('solicitacao', models.ForeignKey(to='base.SolicitacaoLicitacao')),
                ('usuario_cancelamento', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='aditivo',
            name='contrato',
            field=models.ForeignKey(to='base.Contrato'),
        ),
    ]
