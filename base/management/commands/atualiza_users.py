# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from base.models import PessoaFisica

class Command(BaseCommand):

    def handle(self, *args, **options):
        for pessoa in PessoaFisica.objects.all():
            pessoa.user.first_name = pessoa.nome[:30]
            if pessoa.email:
                pessoa.user.email = pessoa.email
            pessoa.user.save()
