# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import PedidoCredenciamento, PedidoAtaRegistroPreco, PedidoContrato


class Command(BaseCommand):

    def handle(self, *args, **options):
        for pedido in PedidoAtaRegistroPreco.objects.all():
            pedido.valor = pedido.item.valor
            pedido.save()

        for pedido in PedidoCredenciamento.objects.all():
            pedido.valor = pedido.item.valor
            pedido.save()

        for pedido in PedidoContrato.objects.all():
            pedido.valor = pedido.item.valor
            pedido.save()
