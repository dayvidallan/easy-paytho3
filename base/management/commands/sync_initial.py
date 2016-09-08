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
    kwargs.setdefault('interactive', True)
    # print termcolors.make_style(fg='cyan', opts=('bold',))('>>> %s %s%s' \
    #     % (command,
    #        ' '.join(args),
    #        ' '.join(['%s=%s' % (k, v) for k, v in kwargs.items()])))
    call_command(command, *args, **kwargs)


class Command(BaseCommand):

    def handle(self, *args, **options):
        print_and_call_command('reset_db')
        print_and_call_command('syncdb', load_initial_data=False, interactive = False)
        print_and_call_command('migrate')
        print_and_call_command('loaddata', 'initial_data', skip_validation=True)
        print_and_call_command('sync_permissions')
        print_and_call_command('collectstatic', clear=True, verbosity=0, interactive=False)
        print_and_call_command('criar_base_teste')