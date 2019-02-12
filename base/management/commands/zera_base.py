# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from base.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):

        sql1= u'''
        TRUNCATE TABLE base_aditivo, base_aditivoitemcontrato, base_anexoataregistropreco, base_anexocontrato, base_anexocredenciamento, base_anexopregao,
        base_logdownloadarquivo, base_historicopregao, base_itemataregistropreco, base_pedidoataregistropreco, base_transferenciaitemarp, base_itempesquisamercadologica,
        base_itemquantidadesecretaria, base_itemlote, base_ordemcompra, base_itemsolicitacaolicitacao, base_itemataregistropreco, base_movimentosolicitacao,
        base_ataregistropreco, base_solicitacaolicitacaotmp, base_documentosolicitacao, base_pesquisamercadologica, base_solicitacaolicitacao_interessados,
        base_credenciamento, base_pedidocredenciamento, base_itemcredenciamento, base_solicitacaolicitacao, base_pedidocontrato, base_itemcontrato, base_contrato,
        base_participantepregao, base_visitantepregao, base_pregao, base_lanceitemrodadapregao, base_participanteitempregao, base_propostaitempregao, base_rodadapregao,
        base_resultadoitempregao, base_certidaocrc, base_cnaesecundario, base_comissaolicitacao, base_membrocomissaolicitacao, base_dotacaoorcamentaria,
        base_feriado, base_fornecedorcrc, base_interessadoedital, base_modeloata, base_modelodocumento, base_motivosuspensaopregao, base_pessoafisica, base_processo,
        base_setor, base_secretaria, base_sociocrc, auth_user, base_itempregao, base_configuracao, auth_user_groups, auth_user_user_permissions, django_admin_log,
        easyaudit_crudevent, easyaudit_loginevent;
        '''





        from django.db import connection
        cur = connection.cursor()
        cur.execute(sql1)
        connection._commit()

        secretaria = Secretaria.objects.get_or_create(nome=u'Secretaria de Planejamento', sigla=u'SEMPLA')[0]
        setor_licitacao = Setor.objects.get_or_create(nome=u'Setor de Licitação', sigla=u'SECLIC', secretaria=secretaria)[0]
        root = User.objects.get_or_create(username=u'admin',is_active=True,is_superuser=True, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        pessoa = PessoaFisica()
        pessoa.nome = u'Administrador'
        pessoa.cpf = u'12345678900'
        pessoa.sexo = PessoaFisica.SEXO_MASCULINO
        pessoa.setor = setor_licitacao
        pessoa.user = root
        pessoa.save()