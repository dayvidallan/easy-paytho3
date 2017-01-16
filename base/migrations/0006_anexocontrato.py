# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_anexopregao_publico'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnexoContrato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=500, verbose_name='Nome')),
                ('data', models.DateField(verbose_name='Data')),
                ('arquivo', models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/')),
                ('cadastrado_em', models.DateTimeField(verbose_name='Cadastrado em')),
                ('publico', models.BooleanField(default=False, help_text='Se sim, este documento ser\xe1 exibido publicamente', verbose_name='Documento P\xfablico')),
                ('cadastrado_por', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('contrato', models.ForeignKey(to='base.Contrato')),
            ],
            options={
                'verbose_name': 'Anexo do Contrato',
                'verbose_name_plural': 'Anexos do Contrato',
            },
        ),
    ]
