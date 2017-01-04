# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_auto_20170104_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaolicitacao',
            name='tipo_aquisicao',
            field=models.CharField(default='Licita\xe7\xe3o', max_length=50, verbose_name='Tipo de Aquisi\xe7\xe3o', choices=[('Licita\xe7\xe3o', 'Licita\xe7\xe3o'), ('Dispensa', 'Dispensa'), ('Inexigibilidade', 'Inexigibilidade')]),
        ),
    ]
