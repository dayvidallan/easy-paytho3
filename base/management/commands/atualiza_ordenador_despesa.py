# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import OrdemCompra
from base.views import get_config
import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):
        for ordem in OrdemCompra.objects.all():
            ordem.ordenador_despesa = get_config().ordenador_despesa
            ordem.ordenador_despesa_secretaria = get_config(ordem.solicitacao.setor_origem.secretaria).ordenador_despesa
            ordem.responsavel_secretaria = get_config(ordem.solicitacao.setor_origem.secretaria).responsavel
            ordem.save()
