# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from base.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):

        sql1= u'''
        delete from base_aditivo;
        delete from base_aditivoitemcontrato;
        delete from base_anexoataregistropreco;
        delete from base_anexocontrato;
        delete from base_anexocredenciamento;
        delete from base_logdownloadarquivo;
        delete from base_anexopregao;
        delete from base_historicopregao;

        delete from base_transferenciaitemarp;
        delete from base_pedidoataregistropreco;
        delete from base_itemataregistropreco;

        delete from base_itempesquisamercadologica;
        delete from base_itemquantidadesecretaria;
        delete from base_lanceitemrodadapregao;
        delete from base_participanteitempregao;
        delete from base_propostaitempregao;
        delete from base_resultadoitempregao;
        delete from base_rodadapregao;
        delete from base_itemlote;
        delete from base_itemcredenciamento;
        delete from base_ordemcompra;
        delete from base_itemsolicitacaolicitacao;
        delete from base_movimentosolicitacao;
        delete from base_ataregistropreco;
        delete from base_solicitacaolicitacaotmp;
        delete from base_documentosolicitacao;
        delete from base_pesquisamercadologica;
        delete from base_solicitacaolicitacao_interessados;

        delete from base_credenciamento;
        delete from base_solicitacaolicitacao;
        delete from base_pedidocontrato;
        delete from base_itemcontrato;
        delete from base_contrato;
        delete from base_participantepregao;
        delete from base_visitantepregao;
        delete from base_pregao;


        '''
        AditivoItemContrato.objects.all().delete()

        AnexoAtaRegistroPreco.objects.all().delete()

        AnexoContrato.objects.all().delete()

        AnexoCredenciamento.objects.all().delete()

        Pregao.objects.all().delete()

        AnexoPregao.objects.all().delete()

        AtaRegistroPreco.objects.all().delete()

        CertidaoCRC.objects.all().delete()

        CnaeSecundario.objects.all().delete()
        ComissaoLicitacao.objects.all().delete()
        Contrato.objects.all().delete()
        Credenciamento.objects.all().delete()
        DocumentoSolicitacao.objects.all().delete()
        DotacaoOrcamentaria.objects.all().delete()
        Feriado.objects.all().delete()
        FornecedorCRC.objects.all().delete()
        HistoricoPregao.objects.all().delete()
        InteressadoEdital.objects.all().delete()
        ItemAtaRegistroPreco.objects.all().delete()
        ItemContrato.objects.all().delete()
        ItemCredenciamento.objects.all().delete()
        ItemLote.objects.all().delete()
        ItemPesquisaMercadologica.objects.all().delete()
        ItemPregao.objects.all().delete()
        ItemQuantidadeSecretaria.objects.all().delete()
        ItemSolicitacaoLicitacao.objects.all().delete()
        LanceItemRodadaPregao.objects.all().delete()
        LogDownloadArquivo.objects.all().delete()
        MembroComissaoLicitacao.objects.all().delete()
        ModeloAta.objects.all().delete()
        ModeloDocumento.objects.all().delete()
        MotivoSuspensaoPregao.objects.all().delete()
        MovimentoSolicitacao.objects.all().delete()
        OrdemCompra.objects.all().delete()
        ParticipanteItemPregao.objects.all().delete()
        ParticipantePregao.objects.all().delete()
        PedidoAtaRegistroPreco.objects.all().delete()
        PedidoContrato.objects.all().delete()
        PedidoCredenciamento.objects.all().delete()
        PesquisaMercadologica.objects.all().delete()
        PessoaFisica.objects.all().delete()

        Processo.objects.all().delete()
        PropostaItemPregao.objects.all().delete()
        ResultadoItemPregao.objects.all().delete()
        RodadaPregao.objects.all().delete()
        Secretaria.objects.all().delete()
        Setor.objects.all().delete()
        SocioCRC.objects.all().delete()
        SolicitacaoLicitacao.objects.all().delete()
        SolicitacaoLicitacaoTmp.objects.all().delete()
        TransferenciaItemARP.objects.all().delete()
        User.objects.all().delete()
        VisitantePregao.objects.all().delete()

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

        from django.db import connection
        cur = connection.cursor()
        cur.execute(sql1)
        connection._commit()