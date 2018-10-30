# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import SolicitacaoLicitacao
from base.views import get_config
import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):
        for solicitacao in SolicitacaoLicitacao.objects.all():
            solicitacao.ordenador_despesa = get_config().ordenador_despesa
            solicitacao.ordenador_despesa_secretaria = get_config(solicitacao.setor_origem.secretaria).ordenador_despesa
            solicitacao.responsavel_secretaria = get_config(solicitacao.setor_origem.secretaria).responsavel
            solicitacao.save()
