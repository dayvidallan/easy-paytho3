# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import PedidoCredenciamento, PedidoAtaRegistroPreco, PedidoContrato, Pregao, ItemAtaRegistroPreco, ItemContrato, ItemCredenciamento


class Command(BaseCommand):

    def handle(self, *args, **options):
        # for pedido in PedidoAtaRegistroPreco.objects.all():
        #     pedido.valor = pedido.item.valor
        #     pedido.save()
        #
        # for pedido in PedidoCredenciamento.objects.all():
        #     pedido.valor = pedido.item.valor
        #     pedido.save()
        #
        # for pedido in PedidoContrato.objects.all():
        #     pedido.valor = pedido.item.valor
        #     pedido.save()
        #
        #
        # for pregao in Pregao.objects.all():
        #     if pregao.situacao == u'Cadastrado':
        #         if pregao.data_homologacao:
        #             pregao.situacao = u'Homologado'
        #         else:
        #             pregao.situacao = u'Publicado'
        #         pregao.save()
        #
        # for item in ItemAtaRegistroPreco.objects.all():
        #     if item.item:
        #         item.ordem = item.item.item
        #         item.save()

        for item in ItemContrato.objects.all():
            if item.item:
                item.ordem = item.item.item
                item.save()

        for item in ItemCredenciamento.objects.all():
            if item.item:
                item.ordem = item.item.item
                item.save()
