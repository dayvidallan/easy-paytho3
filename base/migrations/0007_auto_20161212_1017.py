# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20161212_0910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('numero', models.CharField(unique=True, max_length=25, verbose_name='N\xfamero do Processo')),
                ('objeto', models.CharField(max_length=100)),
                ('tipo', models.PositiveIntegerField(choices=[[1, 'Memorando'], [2, 'Of\xedcio'], [3, 'Requerimento']])),
                ('status', models.PositiveIntegerField(default=1, verbose_name='Situa\xe7\xe3o', choices=[[1, 'Em tr\xe2mite'], [2, 'Finalizado'], [3, 'Arquivado']])),
                ('palavras_chave', models.TextField(null=True, verbose_name='Palavras-chave')),
                ('data_finalizacao', models.DateTimeField(null=True, editable=False)),
                ('observacao_finalizacao', models.TextField(null=True, verbose_name='Despacho', blank=True)),
            ],
            options={
                'verbose_name': 'Processo',
                'verbose_name_plural': 'Processos',
            },
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('pode_cadastrar_solicitacao', 'Pode Cadastrar Solicita\xe7\xe3o'), ('pode_cadastrar_pregao', 'Pode Cadastrar Preg\xe3o'), ('pode_cadastrar_pesquisa_mercadologica', 'Pode Cadastrar Pesquisa Mercadol\xf3gica'), ('pode_ver_minuta', 'Pode Ver Minuta'), ('pode_avaliar_minuta', 'Pode Avaliar Minuta'), ('pode_abrir_processo', 'Pode Abrir Processo'))},
        ),
        migrations.AddField(
            model_name='processo',
            name='pessoa_cadastro',
            field=models.ForeignKey(related_name='pessoa_cadastro_set', editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='processo',
            name='pessoa_finalizacao',
            field=models.ForeignKey(related_name='pessoa_finalizacao_set', editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='processo',
            name='setor_origem',
            field=models.ForeignKey(verbose_name='Setor de Origem', to='base.Setor'),
        ),
        migrations.AddField(
            model_name='solicitacaolicitacao',
            name='processo',
            field=models.ForeignKey(to='base.Processo', null=True),
        ),
    ]
