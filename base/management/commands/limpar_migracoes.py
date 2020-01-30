# -*- coding: utf-8 -*-
import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    def handle(self, *args, **options):
        os.system('./bin/clean_pyc.sh')
        call_command('collectstatic')
        print('Limpando a tabela de migrações')
        cur = connection.cursor()
        sql = 'TRUNCATE TABLE django_migrations;'
        cur.execute(sql)
        print('Executando fake em todas as migrações')
        os.system('python manage.py migrate contenttypes --fake')
        os.system('python manage.py migrate auth --fake')
        os.system('python manage.py migrate base 0001_initial --fake')
        os.system('python manage.py migrate easyaudit 0001_initial --fake')
        os.system('python manage.py migrate easyaudit 0002_auto_20170125_0759 --fake')
        os.system('python manage.py migrate easyaudit 0003_auto_20170228_1505 --fake')
        os.system('python manage.py migrate admin --fake')
        os.system('python manage.py migrate sessions --fake')
        os.system('python manage.py migrate easyaudit')

