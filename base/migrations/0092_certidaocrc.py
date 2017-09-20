# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-20 09:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0091_auto_20170919_1007'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertidaoCRC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=1000, verbose_name='Nome')),
                ('validade', models.DateField(verbose_name='Validade')),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='upload/crc/', verbose_name='Arquivo')),
                ('crc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.FornecedorCRC', verbose_name='CRC')),
            ],
            options={
                'verbose_name': 'Certid\xe3o CRC',
                'verbose_name_plural': 'Certid\xf5es CRC',
            },
        ),
    ]
