# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_popula_estado_e_municipio'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('pode_cadastrar_solicitacao', 'Pode Cadastrar Solicita\xe7\xe3o'), ('pode_cadastrar_pregao', 'Pode Cadastrar Preg\xe3o'), ('pode_cadastrar_pesquisa_mercadologica', 'Pode Cadastrar Pesquisa Mercadol\xf3gica'), ('pode_ver_minuta', 'Pode Ver Minuta'), ('pode_avaliar_minuta', 'Pode Avaliar Minuta'))},
        ),
    ]
