# -*- coding: utf-8 -*-

'''
Comando que deve ser executado após atualizar os fontes do SISMATELE.
'''
import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import termcolors
from django.conf import settings

def print_and_call_command(command, *args, **kwargs):
    print((termcolors.make_style(fg='cyan', opts=('bold',))('>>> {} {}{}'.format(command, ' '.join(args), ' '.join(['{}={}'.format(k, v) for k, v in list(kwargs.items())])))))
    call_command(command, *args, **kwargs)

class Command(BaseCommand):

    def handle(self, *args, **options):
        #print_and_call_command('syncdb', load_initial_data=False, interactive = False)
        print_and_call_command('migrate')
        print_and_call_command('loaddata', 'initial_data', skip_checks=True, ignore=True)
        print_and_call_command('sync_permissions')
        print_and_call_command('collectstatic', clear=True, verbosity=0, interactive=False)
