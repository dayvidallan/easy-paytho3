# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import ItemAtaRegistroPreco
import datetime

class Command(BaseCommand):

    def handle(self, *args, **options):
        for item_da_ata in ItemAtaRegistroPreco.objects.all():
            ata = item_da_ata.ata
            if item_da_ata.get_quantidade_disponivel(total=True) <= 0:
                item_da_ata.data_esgotamento = datetime.datetime.now().date()
                item_da_ata.save()
                if not ItemAtaRegistroPreco.objects.filter(ata=ata, data_esgotamento__isnull=True).exists():
                    ata.data_esgotamento = datetime.datetime.now().date()
                    ata.save()
