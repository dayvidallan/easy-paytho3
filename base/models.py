# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from newadmin.utils import CepModelField
from decimal import Decimal
from django.db.models import Sum
import datetime
from ckeditor.fields import RichTextField
from base.templatetags.app_filters import format_money
TWOPLACES = Decimal(10) ** -2
import os


def get_tl():
    """
    Retorna threadlocals.
    """
    tl = None
    exec 'from base.middleware import threadlocals as tl'
    return tl

tl = get_tl()

class User(AbstractUser):

    class Meta:
        db_table = 'auth_user'

        permissions = (
            ('pode_cadastrar_solicitacao', u'Pode Cadastrar Solicitação'),
            ('pode_cadastrar_pregao', u'Pode Cadastrar Pregão'),
            ('pode_cadastrar_pesquisa_mercadologica', u'Pode Cadastrar Pesquisa Mercadológica'),
            ('pode_ver_minuta', u'Pode Ver Minuta'),
            ('pode_avaliar_minuta', u'Pode Avaliar Minuta'),
            ('pode_abrir_processo', u'Pode Abrir Processo'),
            ('pode_gerenciar_contrato', u'Pode Gerenciar Contrato')
        )

class Secretaria(models.Model):
    nome = models.CharField(u'Nome', max_length=80)
    sigla = models.CharField(u'Sigla', max_length=20, null=True, blank=True)
    responsavel = models.ForeignKey('base.PessoaFisica', verbose_name=u'Responsável', null=True, blank=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Secretaria'
        verbose_name_plural = u'Secretarias'


class Setor(models.Model):
    nome = models.CharField(u'Nome', max_length=80)
    sigla = models.CharField(u'Sigla', max_length=20, null=True, blank=True)
    secretaria = models.ForeignKey(Secretaria, verbose_name=u'Secretaria')

    def __unicode__(self):
        if self.sigla and self.secretaria.sigla:
            return u'%s / %s' % (self.sigla, self.secretaria.sigla)
        return u'%s / %s' % (self.nome, self.secretaria)

    class Meta:
        verbose_name = u'Setor'
        verbose_name_plural = u'Setores'


class ModalidadePregao(models.Model):
    nome = models.CharField(u'Nome', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Modalidade de Pregão'
        verbose_name_plural = u'Modalidades de Pregão'


class CriterioPregao(models.Model):
    ITEM = 1
    LOTE = 2
    GRUPO_ITENS = 3
    nome = models.CharField(u'Nome', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Critério de Julgamento do Pregão'
        verbose_name_plural = u'Critérios de Julgamento de Pregão'

class TipoPregao(models.Model):

    MENOR_PRECO = 1
    DESCONTO = 2

    nome = models.CharField(u'Nome', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Tipo de Pregão'
        verbose_name_plural = u'Tipos de Pregão'


class TipoUnidade(models.Model):
    nome = models.CharField(u'Unidade', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ('nome', )
        verbose_name = u'Tipo de Unidade'
        verbose_name_plural = u'Tipos de Unidade'


class Processo(models.Model):
    STATUS_EM_TRAMITE = 1
    STATUS_FINALIZADO = 2
    STATUS_ARQUIVADO = 3

    PROCESSO_STATUS = [
        [STATUS_EM_TRAMITE, u'Em trâmite'],
        [STATUS_FINALIZADO, u'Finalizado'],
        [STATUS_ARQUIVADO, u'Arquivado']
    ]

    TIPO_MEMORANDO = 1
    TIPO_OFICIO = 2
    TIPO_REQUERIMENTO = 3

    PROCESSO_TIPO = [
        [TIPO_MEMORANDO, u'Memorando'],
        [TIPO_OFICIO, u'Ofício'],
        [TIPO_REQUERIMENTO, u'Requerimento'],
    ]

    data_cadastro = models.DateTimeField(auto_now_add=True)
    pessoa_cadastro = models.ForeignKey(User, related_name='pessoa_cadastro_set')
    numero = models.CharField(u'Número do Processo', max_length=25, unique=True)
    objeto = models.CharField(max_length=1500)
    tipo = models.PositiveIntegerField(choices=PROCESSO_TIPO)
    status = models.PositiveIntegerField(u'Situação', choices=PROCESSO_STATUS, default=STATUS_EM_TRAMITE)
    setor_origem = models.ForeignKey(Setor, verbose_name=u"Setor de Origem")
    palavras_chave = models.TextField(u'Palavras-chave', null=True)
    data_finalizacao = models.DateTimeField(editable=False, null=True)
    pessoa_finalizacao = models.ForeignKey(User, related_name='pessoa_finalizacao_set', null=True)
    observacao_finalizacao = models.TextField(u'Despacho', null=True, blank=True)

    def __unicode__(self):
        return self.numero

    class Meta:
        verbose_name = u'Processo'
        verbose_name_plural = u'Processos'


    def get_memorando(self):
        return SolicitacaoLicitacao.objects.filter(processo=self)[0]



class SolicitacaoLicitacao(models.Model):

    CADASTRADO = u'Cadastrado'
    DEVOLVIDO = u'Devolvido'
    RECEBIDO = u'Recebido'
    ENVIADO_LICITACAO = u'Enviado para Licitação'
    ENVIADO_COMPRA = u'Enviado para Compra'
    ENVIADO = u'Aguardando Recebimento'
    EM_LICITACAO = u'Em Licitação'
    NEGADA = u'Negada'

    SITUACAO_CHOICES = (
        (CADASTRADO, CADASTRADO),
        (ENVIADO, ENVIADO),
        (RECEBIDO, RECEBIDO),
        (DEVOLVIDO, DEVOLVIDO),
        (ENVIADO_LICITACAO, ENVIADO_LICITACAO),
        (EM_LICITACAO, EM_LICITACAO),
        (NEGADA, NEGADA),
    )

    COMPRA = u'Compra'
    LICITACAO = u'Licitação'
    ADESAO_ARP = u'Adesão à ARP'
    TIPO_CHOICES = (
        (COMPRA, COMPRA),
        (LICITACAO, LICITACAO),

    )

    TIPO_AQUISICAO_LICITACAO = u'Licitação'
    TIPO_AQUISICAO_DISPENSA = u'Dispensa'
    TIPO_AQUISICAO_INEXIGIBILIDADE = u'Inexigibilidade'
    TIPO_AQUISICAO_COMPRA = u'Compra'
    TIPO_AQUISICAO_ADESAO_ARP = u'Adesão à ARP'

    TIPO_AQUISICAO_CHOICES = (
        (TIPO_AQUISICAO_LICITACAO, TIPO_AQUISICAO_LICITACAO),
        (TIPO_AQUISICAO_DISPENSA, TIPO_AQUISICAO_DISPENSA),
        (TIPO_AQUISICAO_INEXIGIBILIDADE, TIPO_AQUISICAO_INEXIGIBILIDADE),
    )
    num_memorando = models.CharField(u'Número do Memorando', max_length=80)
    objeto = models.TextField(u'Descrição do Objeto')
    objetivo = models.TextField(u'Objetivo')
    justificativa = models.TextField(u'Justificativa')
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    tipo = models.CharField(u'Tipo', max_length=50, choices=TIPO_CHOICES, default=LICITACAO)
    tipo_aquisicao = models.CharField(u'Tipo de Aquisição', max_length=50, choices=TIPO_AQUISICAO_CHOICES, default=TIPO_AQUISICAO_LICITACAO)
    data_cadastro = models.DateTimeField(u'Cadastrada em')
    cadastrado_por = models.ForeignKey(User, null=True, blank=True)
    obs_negacao = models.CharField(u'Justificativa da Negação', max_length=1500, null=True, blank=True)
    data_inicio_pesquisa = models.DateField(u'Início das Pesquisas', null=True, blank=True)
    data_fim_pesquisa = models.DateField(u'Fim das Pesquisas', null=True, blank=True)
    interessados = models.ManyToManyField(Secretaria)
    prazo_resposta_interessados = models.DateField(u'Prazo para retorno dos interessados', null=True, blank=True)
    setor_origem = models.ForeignKey(Setor, verbose_name=u'Setor de Origem', related_name='setor_origem', null=True, blank=True)
    setor_atual = models.ForeignKey(Setor, verbose_name=u'Setor Atual', related_name='setor_atual', null=True, blank=True)
    arquivo_minuta = models.FileField(u'Arquivo da Minuta', null=True, blank=True, upload_to=u'upload/minutas/')
    minuta_aprovada = models.BooleanField(u'Minuta Aprovada', default=False)
    data_avaliacao_minuta = models.DateTimeField(u'Minuta Aprovada em', null=True, blank=True)
    minuta_avaliada_por = models.ForeignKey(User, verbose_name=u'Minuta Aprovada Por', related_name=u'aprova_minuta', null=True, blank=True)
    obs_avaliacao_minuta = models.CharField(u'Observação - Minuta', max_length=1500, null=True, blank=True)
    arquivo_parecer_minuta = models.FileField(u'Arquivo com o Parecer', null=True, blank=True, upload_to=u'upload/minutas/')
    prazo_aberto = models.NullBooleanField(u'Aberto para Recebimento de Pesquisa', default=False)
    processo = models.ForeignKey(Processo, null=True)


    def __unicode__(self):
        return u'Solicitação N°: %s' % self.num_memorando

    class Meta:
        verbose_name = u'Solicitação de Licitação'
        verbose_name_plural = u'Solicitações de Licitação'

    def get_proximo_item(self, eh_lote=False):
        if not self.itemsolicitacaolicitacao_set.exists():
            return u'1'
        else:
            if eh_lote:
                if self.itemsolicitacaolicitacao_set.filter(eh_lote=True).exists():
                    ultimo = self.itemsolicitacaolicitacao_set.filter(eh_lote=True).order_by('-item')[0]
                    return int(ultimo.item) + 1
                return u'1'
            else:
                if self.itemsolicitacaolicitacao_set.filter(eh_lote=False).exists():
                    ultimo = self.itemsolicitacaolicitacao_set.filter(eh_lote=False).order_by('-item')[0]
                    return int(ultimo.item) + 1
                return u'1'

    def get_ata(self):
        return AtaRegistroPreco.objects.filter(solicitacao=self)[0]

    def eh_dispensa(self):
        return self.tipo_aquisicao in [SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA, SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE]

    def tem_proposta(self):
        for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self):
            if not ItemPesquisaMercadologica.objects.filter(item=item).exists():
                return False
        return True

    def get_pedidos_secretarias(self):
        ids= list()
        ids_secretaria = list()
        for item in ItemQuantidadeSecretaria.objects.filter(solicitacao=self):
            if item.secretaria.id not in ids_secretaria:
                ids.append(item.id)
                ids_secretaria.append(item.secretaria.id)

        return ItemQuantidadeSecretaria.objects.filter(id__in=ids)


    def pode_enviar_para_compra(self):
        return self.situacao == SolicitacaoLicitacao.CADASTRADO and self.tem_item_cadastrado()

    def recebido_pelo_setor(self):
        if MovimentoSolicitacao.objects.filter(solicitacao=self).exists():
            return MovimentoSolicitacao.objects.filter(solicitacao=self).latest('id')
        return False

    def recebida(self):
        if MovimentoSolicitacao.objects.filter(solicitacao=self).exists():
            return MovimentoSolicitacao.objects.filter(solicitacao=self).latest('id').data_recebimento
        return False

    def eh_apta(self):
        return not (self.situacao == SolicitacaoLicitacao.NEGADA)

    def get_data_recebimento(self):
        movimentos = MovimentoSolicitacao.objects.filter(solicitacao=self)
        if movimentos.exists():
            return movimentos.latest('id').data_recebimento
        return None

    def get_interessados(self):
        texto=u''
        for item in self.interessados.all():
            texto = texto + u' %s,' % item
        return texto[:-1]

    def dentro_prazo_resposta(self):
        hoje = datetime.date.today()
        if self.prazo_resposta_interessados:
            if self.prazo_resposta_interessados >= hoje:
                return True
        return False

    def tem_movimentacao(self):
        return MovimentoSolicitacao.objects.filter(solicitacao=self).exists()

    def tem_item_cadastrado(self):
        return ItemSolicitacaoLicitacao.objects.filter(solicitacao=self).exists()

    def tem_pedidos_outras_secretarias(self):
        return ItemQuantidadeSecretaria.objects.filter(solicitacao=self).count() > 1

    def tem_pedidos_pendentes(self):
        return ItemQuantidadeSecretaria.objects.filter(solicitacao=self, avaliado_em__isnull=True).exists()

    def tem_pedidos_compra(self):
        return PedidoContrato.objects.filter(solicitacao=self, ativo=True).exists() or PedidoAtaRegistroPreco.objects.filter(solicitacao=self, ativo=True).exists()

    def get_pregao(self):
        if Pregao.objects.filter(solicitacao=self).exists():
            return Pregao.objects.filter(solicitacao=self)[0]
        return False

    def eh_maior_desconto(self):
        return self.get_pregao().tipo.id == TipoPregao.DESCONTO

    def eh_lote(self):
        if self.get_pregao():
            return self.get_pregao().criterio.id == CriterioPregao.LOTE
        return False

    def tem_pregao_cadastrado(self):
        return Pregao.objects.filter(solicitacao=self).exists()

    def get_proximo_pregao(self):
        if Pregao.objects.exists():
            pregao = Pregao.objects.order_by('-id')[0]
            return int(pregao.id)+1

        return u'1'

    def get_resultado(self, vencedor=None):
        id_item = list()
        vencedores = list()

        if self.eh_lote():


            resultados = ResultadoItemPregao.objects.filter(item__solicitacao=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('item', 'ordem')

        else:
            resultados = ResultadoItemPregao.objects.filter(item__solicitacao=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('item', 'ordem')

        for resultado in resultados:
            if resultado.item.id not in id_item:
                id_item.append(resultado.item.id)
                if vencedor:
                    if vencedor == resultado.participante:
                        vencedores.append(resultado)
                else:
                    vencedores.append(resultado)
        return vencedores

    def get_lotes(self):
        return ItemSolicitacaoLicitacao.objects.filter(solicitacao=self, eh_lote=True)

    def tem_ordem_compra(self):
        return OrdemCompra.objects.filter(solicitacao=self).exists()

    def tem_itens_lote_com_valores(self):
        return PropostaItemPregao.objects.filter(item__solicitacao=self, valor_item_lote__isnull=False).exists()

    def get_situacao(self):
        if self.tipo == SolicitacaoLicitacao.COMPRA:
            if OrdemCompra.objects.filter(solicitacao=self).exists() or PedidoItem.objects.filter(solicitacao=self, ativo=False).exists():
                return u'Finalizada'
            else:
                return u'Aguardando Ordem de Compra'
        else:
            return u'Cadastrada'

    def get_documentos_contrato(self):
        if Contrato.objects.filter(solicitacao=self).exists():
            contrato = Contrato.objects.filter(solicitacao=self)[0]
            return AnexoContrato.objects.filter(contrato=contrato)
        return False

    def get_contrato(self):
        if Contrato.objects.filter(solicitacao=self).exists():
            return Contrato.objects.filter(solicitacao=self)[0]
        return False

    def get_valor_total(self):
        total = 0
        if PedidoAtaRegistroPreco.objects.filter(solicitacao=self).exists():
            for pedido in PedidoAtaRegistroPreco.objects.filter(solicitacao=self):
                total += pedido.item.valor * pedido.quantidade
            return total
        else:
            for pedido in PedidoContrato.objects.filter(solicitacao=self):
                total += pedido.item.valor * pedido.quantidade
            return total

        return total



class ItemSolicitacaoLicitacao(models.Model):
    CADASTRADO = u'Cadastrado'
    DESERTO = u'Deserto'
    FRACASSADO = u'Fracassado'
    CONCLUIDO = u'Concluído'


    SITUACAO_CHOICES = (
        (CADASTRADO, CADASTRADO),
        (DESERTO, DESERTO),
        (FRACASSADO, FRACASSADO),
        (CONCLUIDO, CONCLUIDO),
    )

    solicitacao = models.ForeignKey('base.SolicitacaoLicitacao', verbose_name=u'Solicitação')
    item = models.IntegerField(u'Item')
    material = models.ForeignKey('base.MaterialConsumo', null=True)
    unidade = models.ForeignKey(TipoUnidade, verbose_name=u'Unidade', null=True)
    quantidade = models.PositiveIntegerField(u'Quantidade')
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(u'Total', decimal_places=2, max_digits=10, null=True, blank=True)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    obs = models.CharField(u'Observação', max_length=3000, null=True, blank=True)
    ativo = models.BooleanField(u'Ativo', default=True)
    eh_lote = models.BooleanField(u'Lote', default=False)

    def __unicode__(self):

        if ItemLote.objects.filter(item=self).exists() and not self.eh_lote:
            id_lote = ItemLote.objects.filter(item=self)[0].lote.item
            num_item = ItemLote.objects.filter(item=self)[0].numero_item
            return u'Item: %s.%s' % (id_lote, num_item)
        elif not self.eh_lote:
            return u'Item: %s' % self.item
        else:
            return u'Lote: %s' % self.item


    class Meta:
        ordering = ['item']
        verbose_name = u'Item da Solicitação de Licitação'
        verbose_name_plural = u'Itens da Solicitação de Licitação'


    def get_valor_unitario_proposto(self):
        if ItemLote.objects.filter(item=self).exists():
            lote = ItemLote.objects.filter(item=self)[0].lote
            if lote.get_vencedor():
                vencedor = lote.get_vencedor().participante
                if vencedor:
                    if PropostaItemPregao.objects.filter(item=self, participante=vencedor).exists():
                        return PropostaItemPregao.objects.filter(item=self, participante=vencedor)[0].valor
        return False

    def get_valor_total_proposto(self):
        if ItemLote.objects.filter(item=self).exists():
            lote = ItemLote.objects.filter(item=self)[0].lote
            if lote.get_vencedor():
                vencedor = lote.get_vencedor().participante
                if vencedor:
                    total=0
                    for item in PropostaItemPregao.objects.filter(item=self, participante=vencedor):
                        total = total + (item.valor * item.item.quantidade)
                        return total
        return False


    def get_item_tipo_contrato(self):
        if ItemAtaRegistroPreco.objects.filter(item=self).exists():
            return ItemAtaRegistroPreco.objects.filter(item=self)[0]
        elif ItemContrato.objects.filter(item=self).exists():
            return ItemContrato.objects.filter(item=self)[0]

    def ganhou_com_valor_acima(self):
        vencedor = self.get_vencedor()
        if vencedor and vencedor.valor > self.valor_medio:
            return True
        return False

    def get_id_lote(self):
        return ItemLote.objects.filter(item=self)[0].lote.item

    def tem_lance_registrado(self):
        return LanceItemRodadaPregao.objects.filter(item=self).exists()

    def get_lance_minimo(self):
        eh_maior_desconto = self.solicitacao.eh_maior_desconto()
        melhor_proposta = None
        melhor_lance = None
        if eh_maior_desconto:
            propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, desistencia=False, desclassificado=False).order_by('-valor')
        else:
            propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, desistencia=False, desclassificado=False).order_by('valor')
        if propostas.exists():
            melhor_proposta =  propostas[0]
        if eh_maior_desconto:
            rodadas = LanceItemRodadaPregao.objects.filter(declinio=False, item=self).order_by('-valor')
        else:
            rodadas = LanceItemRodadaPregao.objects.filter(declinio=False, item=self).order_by('valor')
        if rodadas.exists():
            melhor_lance = rodadas[0]
        if melhor_proposta:
            if melhor_lance:
                if eh_maior_desconto:
                    if melhor_lance.valor > melhor_proposta.valor:
                        return melhor_lance
                    else:
                        return melhor_proposta

                else:
                    if melhor_lance.valor < melhor_proposta.valor:
                        return melhor_lance
                    else:
                        return melhor_proposta

            else:
                return melhor_proposta
        elif melhor_lance:
            return melhor_lance
        return False

    def get_lance_minimo_valor(self):
        if self.get_lance_minimo():
            return self.get_lance_minimo().valor
        return None
    def get_lance_minimo_participante(self):
        if self.get_lance_minimo():
            return self.get_lance_minimo().participante
        return None


    def get_reducao_empresa(self):
        lance_minimo = self.get_lance_minimo()
        if lance_minimo:
            preco = PropostaItemPregao.objects.filter(participante=lance_minimo.participante, item=self)
            if preco:
                reducao = self.get_lance_minimo_valor() / preco[0].valor
                ajuste= 1-reducao

                return u'%s%%' % (ajuste.quantize(TWOPLACES) * 100)
            return None

    def get_marca_vencedora(self):
        lance_minimo = self.get_lance_minimo()
        if lance_minimo:
            preco = PropostaItemPregao.objects.filter(participante=lance_minimo.participante, item=self)
            if preco.exists():
                return preco[0].marca
        return None


    def get_reducao_total(self):
        if self.get_lance_minimo_valor():
            reducao = self.get_lance_minimo_valor() / self.valor_medio
            ajuste= 1-reducao
            return u'%s%%' % (ajuste.quantize(TWOPLACES) * 100)
        return None

    def get_total_lance_ganhador(self):
        if self.get_vencedor():
            return self.get_vencedor().valor*self.quantidade
        else:
            return None

    def get_empresa_vencedora(self):
        if self.get_lance_minimo():
            return self.get_lance_minimo().participante

    def get_licitacao(self):
        return Pregao.objects.filter(solicitacao=self.solicitacao)[0]

    def get_participante_desempate(self):
        if self.tem_empate_beneficio():
            return ParticipantePregao.objects.get(id=self.tem_empate_beneficio().id)


    def get_proximo_lance(self):
        # if self.tem_empate_beneficio():
        #     return ParticipantePregao.objects.get(id=self.tem_empate_beneficio().id)
        pregao = self.get_licitacao()
        rodada_atual = RodadaPregao.objects.filter(item=self, pregao=pregao, atual=True)[0]
        ja_deu_lance=LanceItemRodadaPregao.objects.filter(declinio=False, rodada=rodada_atual, item=self).values_list('participante',flat=True)
        eh_maior_desconto = pregao.solicitacao.eh_maior_desconto()

        if int(rodada_atual.rodada) > 1:
            rodada_anterior = int(rodada_atual.rodada) - 1
            if eh_maior_desconto:
                participantes_por_ordem = LanceItemRodadaPregao.objects.filter(declinio=False, item=self, rodada__rodada=rodada_anterior).exclude(participante__in=ja_deu_lance).order_by('valor')
            else:
                participantes_por_ordem = LanceItemRodadaPregao.objects.filter(declinio=False, item=self, rodada__rodada=rodada_anterior).exclude(participante__in=ja_deu_lance).order_by('-valor')
        elif LanceItemRodadaPregao.objects.filter(declinio=False, item=self).exists():
            if eh_maior_desconto:
                participantes_por_ordem = PropostaItemPregao.objects.filter(item=self, concorre=True).exclude(participante__in=ja_deu_lance).order_by('valor')
            else:
                participantes_por_ordem = PropostaItemPregao.objects.filter(item=self, concorre=True).exclude(participante__in=ja_deu_lance).order_by('-valor')

        else:
            if eh_maior_desconto:
                participantes_por_ordem = PropostaItemPregao.objects.filter(item=self, concorre=True).order_by('valor')
            else:
                participantes_por_ordem = PropostaItemPregao.objects.filter(item=self, concorre=True).order_by('-valor')
        deu_preco = PropostaItemPregao.objects.filter(item=self).values_list('participante',flat=True)
        declinados = LanceItemRodadaPregao.objects.filter(item=self, declinio=True).values_list('participante',flat=True)
        participantes_por_ordem = participantes_por_ordem.exclude(participante__in=declinados)
        if participantes_por_ordem and ParticipantePregao.objects.filter(id__in=deu_preco).exclude(id__in=ja_deu_lance).exclude(id__in=declinados).exists():
            return ParticipantePregao.objects.filter(id__in=deu_preco).filter(id__in=self.get_podem_dar_lance()).exclude(id__in=ja_deu_lance).exclude(id__in=declinados).filter(id = participantes_por_ordem[0].participante.id)[0]
        else:
            return None


    def get_rodada_atual(self):
        return RodadaPregao.objects.filter(item=self, pregao=self.get_licitacao(), atual=True)[0]

    def get_valor_medio_pesquisa(self):
        registros = ItemPesquisaMercadologica.objects.filter(item=self, rejeitado_por__isnull=True)
        if registros.exists():
            total_registros = registros.count()
            soma = registros.aggregate(Sum('valor_maximo'))
            return soma['valor_maximo__sum']/total_registros
        return None

    def get_valor_medio_envio_pesquisa(self):
        registros = ItemPesquisaMercadologica.objects.filter(item=self, rejeitado_por__isnull=True).exclude(pesquisa__arquivo__isnull=True).exclude(pesquisa__arquivo="")
        if registros.exists():
            total_registros = registros.count()
            soma = registros.aggregate(Sum('valor_maximo'))
            return soma['valor_maximo__sum']/total_registros
        return None

    def tem_empate_beneficio(self):
        if self.get_lance_minimo() and not self.get_lance_minimo().participante.me_epp:
            valor_lance = self.get_lance_minimo().valor
            limite_lance = valor_lance + (valor_lance*5)/100
            lances_da_rodada = LanceItemRodadaPregao.objects.filter(declinio=False, item=self).order_by('valor')
            for item in lances_da_rodada:
                if item.participante.me_epp and item.valor <= limite_lance and LanceItemRodadaPregao.objects.filter(item=self, participante=item.participante).count() <= LanceItemRodadaPregao.objects.filter(item=self, participante=self.get_lance_minimo().participante).count():
                    return item.participante

            propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, desistencia=False, desclassificado=False)
            for proposta in propostas:

                if proposta.participante.me_epp and proposta.valor <= limite_lance and (LanceItemRodadaPregao.objects.filter(item=self, participante=proposta.participante).count() <= LanceItemRodadaPregao.objects.filter(item=self, participante=self.get_lance_minimo().participante).count()):
                    return proposta.participante
        return False

    def get_podem_dar_lance(self):
        return PropostaItemPregao.objects.filter(item=self, concorre=True).values_list('participante', flat=True)

    def tem_lance(self):
        return PropostaItemPregao.objects.filter(item=self, concorre=True).exists()

    def get_participantes_do_item(self):
        return ParticipanteItemPregao.objects.filter(item=self).order_by('concorre','desclassificado','desistencia').values_list('participante', flat=True)

    def get_excluidos_do_item(self):
        return ParticipanteItemPregao.objects.filter(item=self, concorre=False).values_list('participante', flat=True)

    def get_lista_participantes(self, ativos=None, inativos=None):
        if ativos:
            return PropostaItemPregao.objects.filter(item=self, concorre=True).order_by('-concorre', 'desclassificado','desistencia', 'valor')
        if inativos:
            return PropostaItemPregao.objects.filter(item=self, concorre=False, desclassificado=False, desistencia=False).order_by('-concorre', 'desclassificado','desistencia', 'valor')
        return PropostaItemPregao.objects.filter(item=self).order_by('-concorre', 'desclassificado','desistencia', 'valor')

    def get_lista_excluidos(self):
        return PropostaItemPregao.objects.filter(item=self, participante__in = self.get_excluidos_do_item())

    def filtrar_por_10_porcento(self):
        participantes = self.get_lista_participantes()
        if participantes.count()<=3:
            return
        else:
            melhor_valor = participantes[0].valor
            ordenado = participantes.order_by('-valor')
            for item in ordenado:
                if ordenado.filter(concorre=True).count()<=3:
                    continue
                if item.valor > (melhor_valor + (10*melhor_valor)/100):
                    item.concorre = False
                    item.save()
            return

    def filtrar_todos_ativos(self):
        participantes = self.get_lista_participantes()
        participantes.filter(desclassificado=False, desistencia=False).update(concorre=True)
        return

    def ja_recebeu_lance(self):
        return LanceItemRodadaPregao.objects.filter(item=self).exists()

    def get_vencedor(self):
        if ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).exists():
            return ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0]
        return None




    def pode_gerar_resultado(self):
        return LanceItemRodadaPregao.objects.filter(item=self).exists() or PropostaItemPregao.objects.filter(item=self).exists()

    def tem_empate(self):
        return ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, empate=True)


    def get_marca_item_lote(self):
        tt = ItemLote.objects.filter(item=self)
        if ResultadoItemPregao.objects.filter(item=tt[0].lote, situacao=ResultadoItemPregao.CLASSIFICADO).exists():
            resultado = ResultadoItemPregao.objects.filter(item=tt[0].lote, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0]
            return PropostaItemPregao.objects.filter(item=self, participante=resultado.participante)[0].marca
        return None


    def tem_item_anterior(self):
        if self.item > 1:
            anterior = self.item - 1
            eh_lote = Pregao.objects.filter(solicitacao=self.solicitacao)[0].criterio.id == CriterioPregao.LOTE
            if eh_lote:
                if ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao, eh_lote=True).exists():
                    return ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao, eh_lote=True)[0].id

            else:
                if ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao, eh_lote=False).exists():
                    return ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao, eh_lote=False)[0].id
        return False


    def tem_proximo_item(self):
        proximo = self.item + 1
        eh_lote = Pregao.objects.filter(solicitacao=self.solicitacao)[0].criterio.id == CriterioPregao.LOTE

        if eh_lote:
            if ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao, eh_lote=True).exists():
                return ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao, eh_lote=True)[0].id

        else:
            if ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao, eh_lote=False).exists():
                return ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao, eh_lote=False)[0].id
        return False

    def get_valor_item_lote(self):
        if ItemLote.objects.filter(item=self).exists():
            lote = ItemLote.objects.filter(item=self)[0].lote
            if PropostaItemPregao.objects.filter(item=self, participante=lote.get_empresa_vencedora()).exists():
                return PropostaItemPregao.objects.filter(item=self, participante=lote.get_empresa_vencedora())[0].valor_item_lote

    def get_valor_unitario_final(self):
        if self.get_valor_item_lote():
            return self.get_valor_item_lote() / self.quantidade
        return

    def get_proposta_item_lote(self):
        if ItemLote.objects.filter(item=self).exists():
            lote = ItemLote.objects.filter(item=self)[0].lote
            if PropostaItemPregao.objects.filter(item=self, participante=lote.get_empresa_vencedora()).exists():
                return PropostaItemPregao.objects.filter(item=self, participante=lote.get_empresa_vencedora())[0]

    def gerar_resultado(self, apaga=False):
        if apaga:
            ResultadoItemPregao.objects.filter(item=self).delete()
        if ResultadoItemPregao.objects.filter(item=self).exists():
            return
        ids_participantes = []
        finalistas = []
        if self.eh_ativo():
            eh_lote = Pregao.objects.filter(solicitacao=self.solicitacao)[0].criterio.id == CriterioPregao.LOTE
            if PropostaItemPregao.objects.filter(item=self, concorre=True).exists():

                if self.solicitacao.eh_maior_desconto():
                    if eh_lote:
                        propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, item__eh_lote=True).order_by('-valor')
                    else:
                        propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, item__eh_lote=False).order_by('-valor')
                    for lance in propostas:
                        if lance.participante.id not in ids_participantes:
                            valor_registrado = lance.valor
                            if LanceItemRodadaPregao.objects.filter(item=self, participante=lance.participante, valor__isnull=False).exists():
                                melhor_lance_participante = LanceItemRodadaPregao.objects.filter(item=self, participante=lance.participante, valor__isnull=False).order_by('-valor')[0].valor
                                if melhor_lance_participante > valor_registrado:
                                    valor_registrado = melhor_lance_participante
                            ids_participantes.append(lance.participante.id)
                            finalistas.append((lance, valor_registrado))
                    ordenado =  sorted(finalistas, key=lambda x:x[1], reverse=True)
                    for idx, opcao in enumerate(ordenado, 1):
                        novo_resultado = ResultadoItemPregao()
                        novo_resultado.item = self
                        novo_resultado.participante = opcao[0].participante
                        novo_resultado.valor = opcao[1]
                        novo_resultado.marca = opcao[0].marca
                        novo_resultado.ordem = idx
                        novo_resultado.situacao = ResultadoItemPregao.CLASSIFICADO
                        novo_resultado.save()

                    for resultado in ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('-valor'):
                        if ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, valor=resultado.valor).exclude(id=resultado.id).exists():
                            ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, valor=resultado.valor).update(empate=True)


                else:
                    if eh_lote:
                        propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, item__eh_lote=True).order_by('valor')
                    else:
                        propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, item__eh_lote=False).order_by('valor')
                    for lance in propostas:
                        if lance.participante.id not in ids_participantes:
                            valor_registrado = lance.valor
                            if LanceItemRodadaPregao.objects.filter(item=self, participante=lance.participante, valor__isnull=False).exists():
                                melhor_lance_participante = LanceItemRodadaPregao.objects.filter(item=self, participante=lance.participante).order_by('valor')[0].valor
                                if melhor_lance_participante < valor_registrado:
                                    valor_registrado = melhor_lance_participante
                            ids_participantes.append(lance.participante.id)
                            finalistas.append((lance, valor_registrado))
                    ordenado =  sorted(finalistas, key=lambda x:x[1])
                    for idx, opcao in enumerate(ordenado, 1):
                        novo_resultado = ResultadoItemPregao()
                        novo_resultado.item = self
                        novo_resultado.participante = opcao[0].participante
                        novo_resultado.valor = opcao[1]
                        novo_resultado.marca = opcao[0].marca
                        novo_resultado.ordem = idx
                        novo_resultado.situacao = ResultadoItemPregao.CLASSIFICADO
                        novo_resultado.save()

                    for resultado in ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('valor'):
                        if ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, valor=resultado.valor).exclude(id=resultado.id).exists():
                            ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, valor=resultado.valor).update(empate=True)
            return

    def eh_ativo(self):
        return self.situacao not in [ItemSolicitacaoLicitacao.FRACASSADO, ItemSolicitacaoLicitacao.DESERTO]

    def eh_fracassado(self):
        return self.situacao == Pregao.FRACASSADO


    def tem_rodada_aberta(self):
        return RodadaPregao.objects.filter(item=self, atual=True).exists()

    def sem_fornecedor_habilitado(self):
       return not ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).exists()

    def tem_resultado(self):
        return ResultadoItemPregao.objects.filter(item=self).exists()

    def get_itens_do_lote(self):
        itens = ItemLote.objects.filter(lote=self)
        return ItemSolicitacaoLicitacao.objects.filter(id__in=itens.values_list('item', flat=True))

    def tem_pesquisa_registrada(self):
        return ItemPesquisaMercadologica.objects.filter(item=self).exists()

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoItem.objects.filter(item=self, ativo=True)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        else:

            if ItemQuantidadeSecretaria.objects.filter(item=self, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                valor_total = ItemQuantidadeSecretaria.objects.filter(item=self, secretaria=usuario.pessoafisica.setor.secretaria)[0].quantidade
                pedidos = PedidoItem.objects.filter(item=self, ativo=True, setor=usuario.pessoafisica.setor)
                if pedidos.exists():
                    return valor_total - pedidos.aggregate(soma=Sum('quantidade'))['soma']
                else:
                    return valor_total
        return 0


    def get_empresa_item_lote(self):
        lote = ItemLote.objects.filter(item=self)[0].lote
        return lote.get_empresa_vencedora()

    def get_total(self):
        if self.valor_medio:
            return self.quantidade * self.valor_medio
        return 0

class ItemLote(models.Model):
    lote = models.ForeignKey('base.ItemSolicitacaoLicitacao', related_name=u'lote')
    item = models.ForeignKey('base.ItemSolicitacaoLicitacao', related_name=u'item_do_lote')
    numero_item = models.IntegerField(u'Número do Item')

    class Meta:
        verbose_name = u'Item do Lote'
        verbose_name_plural = u'Itens dos Lotes'



def upload_path_termo_homologacao(instance, filename):
    return os.path.join('upload/homologacoes/%s/' % instance.id, filename)

class Pregao(models.Model):
    CADASTRADO = u'Cadastrado'
    DESERTO = u'Deserto'
    FRACASSADO = u'Fracassado'
    CONCLUIDO = u'Concluído'
    SUSPENSO = u'Suspenso'


    SITUACAO_CHOICES = (
        (CADASTRADO, CADASTRADO),
        (DESERTO, DESERTO),
        (FRACASSADO, FRACASSADO),
        (SUSPENSO, SUSPENSO),
        (CONCLUIDO, CONCLUIDO),
    )


    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    num_pregao = models.CharField(u'Número do Pregão', max_length=255)
    modalidade = models.ForeignKey(ModalidadePregao, verbose_name=u'Modalidade')
    tipo = models.ForeignKey(TipoPregao, verbose_name=u'Tipo')
    criterio = models.ForeignKey(CriterioPregao, verbose_name=u'Critério de Julgamento')
    data_inicio = models.DateField(u'Data de Início da Retirada das Propostas', null=True)
    data_termino = models.DateField(u'Data de Término da Retirada das Propostas', null=True)
    data_abertura = models.DateField(u'Data de Abertura das Propostas', null=True)
    hora_abertura = models.TimeField(u'Hora de Abertura das Propostas', null=True)
    local = models.CharField(u'Local', max_length=1500)
    responsavel = models.CharField(u'Responsável', max_length=255)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    obs = models.CharField(u'Observação', max_length=3000, null=True, blank=True)
    data_adjudicacao = models.DateField(u'Data da Adjudicação', null=True)
    data_homologacao = models.DateField(u'Data da Homologação', null=True)
    ordenador_despesa = models.ForeignKey('base.PessoaFisica', verbose_name=u'Ordenador de Despesa', null=True)
    eh_ata_registro_preco = models.BooleanField(u'Ata de Registro de Preço?', default=True)
    arquivo_homologacao = models.FileField(u'Termo de Homologação', null=True, upload_to=upload_path_termo_homologacao)
    pode_homologar = models.BooleanField(u'Pode Homologar', default=False)
    comissao = models.ForeignKey('base.ComissaoLicitacao', verbose_name=u'Comissão de Licitação', null=True )


    class Meta:
        verbose_name = u'Pregão'
        verbose_name_plural = u'Pregões'

    def __unicode__(self):
        return u'%s N° %s' % (self.modalidade, self.num_pregao)
    def get_titulo(self):
        return u'%s N° %s' % (self.modalidade, self.num_pregao)

    def tem_download(self):
        return LogDownloadArquivo.objects.filter(arquivo__pregao=self).exists()

    def eh_ativo(self):
        return self.situacao not in [Pregao.FRACASSADO, Pregao.DESERTO, Pregao.CONCLUIDO, Pregao.SUSPENSO]

    def tem_empate_ficto(self):
        pregao = self
        if pregao.eh_pregao():
            return False

        tabela = {}
        for proposta in PropostaItemPregao.objects.filter(pregao=pregao):
            chave= '%s' %  proposta.participante.id
            tabela[chave] = dict(total = 0)
        for proposta in PropostaItemPregao.objects.filter(pregao=pregao):
            chave= '%s' %  proposta.participante.id

            tabela[chave]['total'] += proposta.valor
        resultado = sorted(tabela.items(), key=lambda x: x[1])
        total = len(resultado)
        indice = 0

        tem_empate_ficto = False
        total_global_vencedor = 0.00
        ganhador_eh_beneficiario = False

        while indice < total:
            fornecedor = ParticipantePregao.objects.get(id=resultado[indice][0])
            if indice == 0:
                total_global_vencedor = int(resultado[indice][0])
                ganhador_eh_beneficiario = fornecedor.me_epp

            elif not tem_empate_ficto and not ganhador_eh_beneficiario:
                if fornecedor.me_epp:
                    limite_lance = total_global_vencedor + (total_global_vencedor*10)/100
                    if int(resultado[indice][0]) < limite_lance:
                        tem_empate_ficto = True
            indice += 1

        return tem_empate_ficto

    def eh_suspenso(self):
        return self.situacao in [Pregao.SUSPENSO]

    def eh_pregao(self):
        return self.modalidade.nome == u'Pregão Presencial'

    def tem_resultado(self):
        return ResultadoItemPregao.objects.filter(item__solicitacao=self.solicitacao).exists()

    def tem_proposta(self):
        return PropostaItemPregao.objects.filter(pregao=self).exists()

    def get_contrato(self):
        if Contrato.objects.filter(pregao=self).exists():
            return Contrato.objects.filter(pregao=self)[0]
        return False

    def tem_item_sem_lote(self):
        itens_em_lotes = ItemLote.objects.filter(item__solicitacao=self.solicitacao)
        return ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False).exclude(id__in=itens_em_lotes.values_list('item', flat=True))

    def tem_lance_registrado(self):
        return LanceItemRodadaPregao.objects.filter(rodada__pregao=self).exists()

    def tem_ocorrencia(self):
        return HistoricoPregao.objects.filter(pregao=self).exists()

    def get_valor_total(self):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
        total = 0
        for item in itens_pregao:
            if item.get_total_lance_ganhador():
                total = total + item.get_total_lance_ganhador()
        return total

    def get_vencedora_global(self):
        if ResultadoItemPregao.objects.filter(participante__pregao=self, situacao=ResultadoItemPregao.CLASSIFICADO).exists():
            return ResultadoItemPregao.objects.filter(participante__pregao=self, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0].participante.fornecedor
        return None

    def get_total_global(self):
        total = 0
        if ResultadoItemPregao.objects.filter(participante__pregao=self, situacao=ResultadoItemPregao.CLASSIFICADO).exists():
            for resultado in ResultadoItemPregao.objects.filter(participante__pregao=self, situacao=ResultadoItemPregao.CLASSIFICADO):
                total += resultado.valor * resultado.item.quantidade

        return total

    def get_arquivos_publicos(self):
        return AnexoPregao.objects.filter(pregao=self, publico=True)


#TODO usar esta estrutura para pregão por lote
class ItemPregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    material = models.ForeignKey('base.MaterialConsumo')
    unidade = models.CharField(u'Unidade de Medida', max_length=500)
    quantidade = models.PositiveIntegerField(u'Quantidade')
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=12, decimal_places=2)
    total = models.DecimalField(u'Total', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = u'Item do Pregão'
        verbose_name_plural = u'Itens do Pregão'
        ordering = ['pregao','id']

    def __unicode__(self):
        return u'%s - %s' % (self.material, self.pregao)

class Fornecedor(models.Model):
    cnpj = models.CharField(u'CNPJ/CPF', max_length=255, help_text=u'Utilize pontos e traços.', unique=True)
    razao_social = models.CharField(u'Razão Social', max_length=255)
    endereco = models.CharField(u'Endereço', max_length=255)
    telefones = models.CharField(u'Telefones', max_length=300)
    email = models.EmailField(u'Email')
    banco = models.CharField(u'Banco', max_length=200, null=True, blank=True)
    agencia = models.CharField(u'Agência', max_length=50, null=True, blank=True)
    conta = models.CharField(u'Conta', max_length=200, null=True, blank=True)


    class Meta:
        verbose_name = u'Fornecedor'
        verbose_name_plural = u'Fornecedores'

    def __unicode__(self):
        return u'%s - %s' % (self.razao_social, self.cnpj)

    def get_dados_bancarios(self):
        if self.banco:
            return u'Banco: %s<br>Agência: %s<br> Conta: %s' % (self.banco, self.agencia, self.conta)
        else:
            return u'Nenhuma conta bancária cadastrada.'


class ParticipantePregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    fornecedor = models.ForeignKey(Fornecedor, verbose_name=u'Fornecedor')
    nome_representante = models.CharField(u'Nome do Representante', max_length=255, null=True, blank=True)
    rg_representante = models.CharField(u'RG do Representante', max_length=255, null=True, blank=True)
    cpf_representante = models.CharField(u'CPF do Representante', max_length=255, null=True, blank=True)
    obs_ausencia_participante = models.CharField(u'Motivo da Ausência do Representante', max_length=1500, null=True, blank=True)
    me_epp = models.BooleanField(u'Micro Empresa/Empresa de Peq.Porte')
    desclassificado = models.BooleanField(u'Desclassificado', default=False)
    motivo_desclassificacao = models.CharField(u'Motivo da Desclassificação', max_length=2000, null=True, blank=True)
    arquivo_propostas = models.FileField(u'Arquivo com as Propostas', null=True, blank=True, upload_to=u'upload/propostas/')
    class Meta:
        verbose_name = u'Participante do Pregão'
        verbose_name_plural = u'Participantes do Pregão'
        ordering = ['desclassificado', 'fornecedor__razao_social']

    def __unicode__(self):
        return self.fornecedor.razao_social

    def pode_remover(self):
        return not ParticipanteItemPregao.objects.filter(participante=self).exists() and  not PropostaItemPregao.objects.filter(participante=self).exists()


class ParticipanteItemPregao(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Item')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')


    class Meta:
        verbose_name = u'Participante do Item do Pregão'
        verbose_name_plural = u'Participantes do Item do Pregão'

    def __unicode__(self):
        return self.item.fornecedor.razao_social

class PropostaItemPregao(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Solicitação')
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')
    valor = models.DecimalField(u'Valor', max_digits=12, decimal_places=2)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    desclassificado = models.BooleanField(u'Desclassificado', default=False)
    motivo_desclassificacao = models.CharField(u'Motivo da Desclassificação', max_length=2000, null=True, blank=True)
    desistencia = models.BooleanField(u'Desistência', default=False)
    motivo_desistencia= models.CharField(u'Motivo da Desistência', max_length=2000, null=True, blank=True)
    concorre = models.BooleanField(u'Concorre', default=True)
    valor_item_lote = models.DecimalField(u'Valor do Item do Lote', max_digits=12, decimal_places=2, null=True, blank=True)


    class Meta:
        verbose_name = u'Valor do Item do Pregão'
        verbose_name_plural = u'Valores do Item do Pregão'

    def __unicode__(self):
        return u'%s - %s' % (self.item, self.participante)

    def get_situacao_valor(self):
        valor_maximo = self.item.valor_medio
        if valor_maximo:
            if self.valor > valor_maximo + (10*valor_maximo)/100:
                return u'<font color="green"><b>Acima dos 10%</b></font>'
            else:
                return u'<b>Dentro dos 10%</b>'
        else:
            return u'<font color=red>Valor Máximo não informado.</font>'


class RodadaPregao(models.Model):
    rodada = models.IntegerField(verbose_name=u'Rodada de Lances')
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Item da Solicitação')
    atual = models.BooleanField(u'Rodada Atual', default=False)

    class Meta:
        verbose_name = u'Rodada do Pregão'
        verbose_name_plural = u'Rodadas do Pregão'

    def eh_rodada_atual(self):
        return self.atual

    def get_rodada_anterior(self):
        num= self.rodada - 1
        if RodadaPregao.objects.filter(item=self.item, rodada=num).exists():
            return RodadaPregao.objects.filter(item=self.item, rodada=num)[0]
        return None

    def get_ordem_lance(self):
        if LanceItemRodadaPregao.objects.filter(rodada=self).exists():
           atual = LanceItemRodadaPregao.objects.filter(rodada=self).order_by('-ordem_lance')[0].ordem_lance
           return atual+1
        return 1


class AtivosManager(models.Manager):
    def get_queryset(self):
        qs = super(AtivosManager, self).get_queryset()
        return qs.filter(declinio=False)

class LanceItemRodadaPregao(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Item da Solicitação')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')
    rodada = models.ForeignKey(RodadaPregao,verbose_name=u'Rodada')
    valor = models.DecimalField(u'Valor', max_digits=12, decimal_places=2, null=True, blank=True)
    declinio = models.BooleanField(u'Declínio', default=False)
    ordem_lance = models.IntegerField(u'Ordem')


    objects = models.Manager()


    class Meta:
        verbose_name = u'Lance da Rodada do Pregão'
        verbose_name_plural = u'Lances da Rodada do Pregão'
        ordering = ['-valor']

    def get_marca(self):
        preco = PropostaItemPregao.objects.filter(participante=self.participante, item=self.item)
        if preco.exists():
            return preco[0].marca
        return None

    def ganhou_desempate(self):
        if (self.participante == self.item.get_lance_minimo().participante) and not self.participante.desclassificado and LanceItemRodadaPregao.objects.filter(rodada=self.rodada, item=self.item, participante=self.participante).count()>1:
            if not self.item.solicitacao.eh_maior_desconto():
                if LanceItemRodadaPregao.objects.filter(rodada=self.rodada, item=self.item, participante=self.participante).order_by('valor')[0].id == self.id:
                    return True
                return False
            else:
                if LanceItemRodadaPregao.objects.filter(rodada=self.rodada, item=self.item, participante=self.participante).order_by('-valor')[0].id == self.id:
                    return True
                return False

        return False

    def get_valor(self):
        if self.item.solicitacao.get_pregao().tipo.id == TipoPregao.DESCONTO:
            return u'%s %%' % self.valor
        else:
            return 'R$ %s' % format_money(self.valor)

    def get_reducao_empresa(self):
        if not self.declinio:
            lance = self.valor

            if PropostaItemPregao.objects.filter(participante=self.participante, item=self.item).exists():
                valor = PropostaItemPregao.objects.filter(participante=self.participante, item=self.item)[0].valor
                return Decimal(100 - ((lance * 100) / valor)).quantize(Decimal(10) ** -2)
        return 0


class PessoaFisica(models.Model):
    SEXO_MASCULINO  = u'M'
    SEXO_FEMININO = u'F'
    SEXO_CHOICES = (
                    (SEXO_MASCULINO, u'Masculino'),
                    (SEXO_FEMININO, u'Feminino'),
                    )

    user = models.OneToOneField(User, null=True, blank=True)
    nome = models.CharField(max_length=80)
    cpf = models.CharField(u'CPF',max_length=15, help_text=u'Digite o CPF com pontos e traços.')
    sexo = models.CharField(u'Sexo', max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField(u'Data de Nascimento', null=True)
    telefones = models.CharField(u'Telefone', max_length=60, null=True, blank=True)
    celulares = models.CharField(u'Celular', max_length=60, null=True, blank=True)
    email = models.CharField(u'Email', max_length=80, null=True, blank=True)
    cep = CepModelField(u'CEP', null=True, blank=True)
    logradouro = models.CharField(u'Logradouro', max_length=80, null=True, blank=True)
    numero = models.CharField(u'Número', max_length=10, null=True, blank=True)
    complemento = models.CharField(u'Complemento', max_length=80, null=True, blank=True)
    bairro = models.CharField(u'Bairro', max_length=80, null=True, blank=True)
    municipio = models.ForeignKey('base.Municipio', null=True, blank=True)

    setor = models.ForeignKey(Setor,verbose_name=u'Setor')

    class Meta:
        verbose_name = u'Pessoa'
        verbose_name_plural = u'Pessoas'

    def __unicode__(self):
        return u'%s (%s) - %s' % (self.nome, self.cpf, self.setor)

    def get_endereco(self):
        texto = u''
        if self.logradouro:
            texto = texto + self.logradouro

        if self.numero:
            texto = texto + ', '+self.numero

        if self.complemento:
            texto = texto + ' - '+self.complemento

        if self.bairro:
            texto = texto + '. '+self.bairro

        if self.cep:
            texto = texto + '. '+self.cep

        if self.municipio:
            texto = texto + self.municipio.get_sigla_estado()

        return texto

    def save(self):
        cpf = self.cpf
        self.cpf = cpf.replace('-','').replace('.','')
        if self.pk:
            self.user.username = self.cpf
            self.user.save()
        super(PessoaFisica, self).save()




class Estado(models.Model):
    nome = models.CharField(u'Nome', max_length=80)
    sigla = models.CharField(u'Sigla', max_length=2)

    def __unicode__(self):
        return self.sigla


class Municipio(models.Model):
    codigo = models.CharField(u'Código IBGE', max_length=7)
    nome = models.CharField(u'Nome', max_length=80)
    estado = models.ForeignKey(Estado)


    class Meta:
        verbose_name = u'Município'
        verbose_name_plural = u'Municípios'
        ordering = ('nome', )

    def __unicode__(self):
        return u'%s / %s' % (self.nome, self.estado.sigla)


class ComissaoLicitacao(models.Model):
    nome = models.CharField(u'Portaria', max_length=80)
    secretaria = models.ForeignKey('base.Secretaria', null=True)


    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Comissão de Licitação'
        verbose_name_plural = u'Comissões de Licitação'

class MembroComissaoLicitacao(models.Model):

    APOIO = u'Apoio'
    PREGOEIRO = u'Pregoeiro'
    MEMBRO_EQUIPE = u'Membro da Equipe do Pregão'
    PRESIDENTE = u'Presidente'
    MEMBRO_CPL = u'Membro da CPL'
    FUNCAO_CHOICES = (
        (APOIO, APOIO),
        (MEMBRO_CPL, MEMBRO_CPL),
        (MEMBRO_EQUIPE, MEMBRO_EQUIPE),
        (PREGOEIRO, PREGOEIRO),
        (PRESIDENTE, PRESIDENTE),
    )
    comissao = models.ForeignKey(ComissaoLicitacao)
    membro = models.ForeignKey(PessoaFisica)
    matricula = models.CharField(u'Matrícula', max_length=100)
    funcao = models.CharField(u'Função', max_length=100, choices=FUNCAO_CHOICES, default=MEMBRO_CPL)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Membro da Comissão de Licitação'
        verbose_name_plural = u'Membros da Comissão de Licitação'


class InteressadoEdital(models.Model):
    PARTICIPANTE = u'Participante'
    INTERESSADO = u'Interessado'

    INTERESSE_CHOICES = (
        (PARTICIPANTE, u'Participar da Licitação'),
        (INTERESSADO, u'Apenas Consulta'),
    )

    pregao = models.ForeignKey(Pregao)
    responsavel = models.CharField(u'Responsável', max_length=200)
    nome_empresarial = models.CharField(u'Nome Empresarial', max_length=200)
    cpf = models.CharField(u'CPF', max_length=80)
    cnpj = models.CharField(u'CNPK', max_length=80)
    endereco = models.CharField(u'Endereço', max_length=80)
    municipio = models.ForeignKey(Municipio, verbose_name=u'Município')
    telefone = models.CharField(u'Telefone', max_length=80)
    email = models.CharField(u'Email', max_length=80)
    interesse = models.CharField(u'Interesse', choices=INTERESSE_CHOICES, max_length=80)
    data_acesso = models.DateTimeField(u'Data de Acesso')


    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Interessado na Licitação'
        verbose_name_plural = u'Interessados na Licitação'


class PesquisaMercadologica(models.Model):

    ATA_PRECO = u'Ata de Registro de Preço'
    FORNECEDOR = u'Fornecedor'

    ORIGEM_CHOICES = (
        (ATA_PRECO, ATA_PRECO),
        (FORNECEDOR, FORNECEDOR),
    )

    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    razao_social = models.CharField(u'Razão Social', max_length=255, null=True,blank=True)
    cnpj = models.CharField(u'CNPJ', max_length=255, null=True,blank=True)
    endereco = models.CharField(u'Endereço', max_length=255, null=True,blank=True)
    ie = models.CharField(u'Inscrição Estadual', max_length=255, null=True,blank=True)
    telefone = models.CharField(u'Telefone', max_length=255, null=True,blank=True)
    email = models.CharField(u'Email', max_length=255, null=True,blank=True)
    nome_representante = models.CharField(u'Representante Legal', max_length=255, null=True,blank=True)
    cpf_representante = models.CharField(u'CPF do Representante Legal', max_length=255, null=True,blank=True)
    rg_representante = models.CharField(u'RG do Representante Legal', max_length=255, null=True,blank=True)
    endereco_representante = models.CharField(u'Endereço do Representante Legal', max_length=255, null=True,blank=True)
    validade_proposta = models.IntegerField(u'Dias de Validade da Proposta', null=True,blank=True)
    cadastrada_em = models.DateTimeField(u'Data de Envio da Proposta', null=True,blank=True)
    arquivo = models.FileField(u'Arquivo da Proposta', upload_to=u'upload/pesquisas/', null=True,blank=True)
    numero_ata = models.CharField(u'Número da Ata', max_length=255, null=True, blank=True)
    vigencia_ata = models.DateField(u'Vigência da Ata', null=True, blank=True)
    orgao_gerenciador_ata = models.CharField(u'Órgão Gerenciador da Ata', max_length=255, null=True, blank=True)
    origem = models.CharField(u'Origem', max_length=100, choices=ORIGEM_CHOICES, null=True, blank=True)

    def get_itens(self):
        return ItemPesquisaMercadologica.objects.filter(pesquisa=self).order_by('item__item')

    def get_total(self):
        total=0
        for item in ItemPesquisaMercadologica.objects.filter(pesquisa=self).order_by('item__item'):
            total += item.valor_maximo * item.item.quantidade
        return total


class ItemPesquisaMercadologica(models.Model):
    pesquisa = models.ForeignKey(PesquisaMercadologica, verbose_name=u'Pesquisa')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    marca = models.CharField(u'Marca', max_length=255)
    valor_maximo = models.DecimalField(u'Valor Máximo', max_digits=10, decimal_places=2, null=True, blank=True)
    ativo = models.BooleanField(u'Ativo', default=True)
    motivo_rejeicao = models.CharField(u'Motivo da Rejeição', max_length=1000, null=True, blank=True)
    rejeitado_por = models.ForeignKey(User, null=True)
    rejeitado_em = models.DateTimeField(u'Rejeitado em', null=True)


    def get_total(self):
        return self.valor_maximo * self.item.quantidade

    def save(self):
        super(ItemPesquisaMercadologica, self).save()
        registros = ItemPesquisaMercadologica.objects.filter(item=self.item, rejeitado_por__isnull=True)
        if registros:
            total_registros = registros.count()
            soma = registros.aggregate(Sum('valor_maximo'))
            self.item.valor_medio = soma['valor_maximo__sum']/total_registros
            self.item.total = self.item.valor_medio * self.item.quantidade
            self.item.save()



class ResultadoItemPregao(models.Model):
    CLASSIFICADO = u'Classificado'
    INABILITADO = u'Inabilitado'
    DESCLASSIFICADO = u'Desclassificado'
    RESULTADO_CHOICES = (
        (CLASSIFICADO, CLASSIFICADO),
        (INABILITADO, INABILITADO),
        (DESCLASSIFICADO, DESCLASSIFICADO),
    )

    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Solicitação')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')
    valor = models.DecimalField(u'Valor', max_digits=12, decimal_places=2)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    ordem = models.IntegerField(u'Classificação')
    situacao = models.CharField(u'Situação', max_length=100, choices=RESULTADO_CHOICES)
    observacoes = models.CharField(u'Observação', max_length=5000, null=True, blank=True)
    empate = models.BooleanField(u'Empate', default=False)

    class Meta:
        verbose_name = u'Resultado da Licitação'
        verbose_name_plural = u'Resultados da Licitação'


    def pode_alterar(self):
        return self.situacao == ResultadoItemPregao.CLASSIFICADO

    def get_valor(self):
        if self.item.solicitacao.get_pregao().tipo.id == TipoPregao.DESCONTO:
            return u'%s %%' % self.valor
        else:
            return 'R$ %s' % format_money(self.valor)


class AnexoPregao(models.Model):
    pregao = models.ForeignKey(Pregao)
    nome = models.CharField(u'Nome', max_length=500)
    data = models.DateField(u'Data')
    arquivo = models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/')
    cadastrado_por = models.ForeignKey(User)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')
    publico = models.BooleanField(u'Documento Público', help_text=u'Se sim, este documento será exibido publicamente', default=False)

    class Meta:
        verbose_name = u'Anexo do Pregão'
        verbose_name_plural = u'Anexos do Pregão'

    def __unicode__(self):
        return '%s - %s' % (self.nome, self.pregao)


class AnexoContrato(models.Model):
    contrato = models.ForeignKey('base.Contrato')
    nome = models.CharField(u'Nome', max_length=500)
    data = models.DateField(u'Data')
    arquivo = models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/')
    cadastrado_por = models.ForeignKey(User)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')
    publico = models.BooleanField(u'Documento Público', help_text=u'Se sim, este documento será exibido publicamente', default=False)

    class Meta:
        verbose_name = u'Anexo do Contrato'
        verbose_name_plural = u'Anexos do Contrato'

    def __unicode__(self):
        return '%s - %s' % (self.nome, self.contrato)



class AnexoAtaRegistroPreco(models.Model):
    ata = models.ForeignKey('base.AtaRegistroPreco')
    nome = models.CharField(u'Nome', max_length=500)
    data = models.DateField(u'Data')
    arquivo = models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/')
    cadastrado_por = models.ForeignKey(User)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')
    publico = models.BooleanField(u'Documento Público', help_text=u'Se sim, este documento será exibido publicamente', default=False)

    class Meta:
        verbose_name = u'Anexo da ARP'
        verbose_name_plural = u'Anexos da ARP'

    def __unicode__(self):
        return '%s - %s' % (self.nome, self.ata)

class LogDownloadArquivo(models.Model):
    PARTICIPAR = u'Participar da Licitação'
    CONSULTA = u'Apenas Consulta'
    INTERESSE_CHOICES = (
        (PARTICIPAR, PARTICIPAR),
        (CONSULTA, CONSULTA),

    )
    nome = models.CharField(u'Nome Empresarial', max_length=500)
    responsavel = models.CharField(u'Nome do Responsável', max_length=500)
    cpf = models.CharField(u'CPF', max_length=500)
    cnpj = models.CharField(u'CNPJ Empresarial', max_length=500)
    endereco = models.CharField(u'Endereço', max_length=500)
    municipio = models.ForeignKey(Municipio, verbose_name=u'Cidade')
    telefone = models.CharField(u'Telefone', max_length=500)
    email =models.CharField(u'Email', max_length=500)
    interesse = models.CharField(u'Interesse', max_length=100, choices=INTERESSE_CHOICES)
    arquivo = models.ForeignKey(AnexoPregao)
    baixado_em = models.DateTimeField(u'Baixado em', auto_now_add=True, null=True)

    class Meta:
        verbose_name = u'Log de Download de Arquivo'
        verbose_name_plural = u'Logs de Download de Arquivo'


class HistoricoPregao(models.Model):
    pregao = models.ForeignKey(Pregao)
    data = models.DateTimeField(u'Data')
    obs = models.CharField(u'Observação', max_length=2500, null=True, blank=True)

    class Meta:
        verbose_name = u'Histórico do Pregão'
        verbose_name_plural = u'Históricos do Pregão'
        ordering = ['data']


class MovimentoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    data_envio = models.DateTimeField(u'Enviado Em', null=True, blank=True)
    enviado_por = models.ForeignKey(User, related_name=u'movimentacao_enviado_por')
    data_recebimento= models.DateTimeField(u'Recebido Em', null=True, blank=True)
    recebido_por = models.ForeignKey(User, related_name=u'movimentacao_recebido_por', null=True)
    setor_origem = models.ForeignKey(Setor, related_name=u'movimentacao_setor_origem')
    setor_destino = models.ForeignKey(Setor, related_name=u'movimentacao_setor_destino', null=True)
    obs = models.CharField(u'Observação', max_length=5000, null=True, blank=True)

    class Meta:
        verbose_name = u'Movimento da Solicitação'
        verbose_name_plural = u'Movimentos da Solicitação'

def upload_path_documento(instance, filename):
    return os.path.join('upload/documentos_solicitacao/%s/' % instance.solicitacao.id, filename)

class DocumentoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    nome = models.TextField(u'Nome do Arquivo', max_length=500)
    cadastrado_em = models.DateTimeField(u'Cadastrado Em', null=True, blank=True)
    cadastrado_por = models.ForeignKey(User, related_name=u'documento_cadastrado_por', null=True)
    documento = models.FileField(u'Documento', null=True, blank=True, upload_to=upload_path_documento)

    class Meta:
        verbose_name = u'Documento da Solicitação'
        verbose_name_plural = u'Documentos da Solicitação'


class ItemQuantidadeSecretaria(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    secretaria = models.ForeignKey(Secretaria)
    quantidade = models.IntegerField(u'Quantidade')
    aprovado = models.BooleanField(u'Aprovado', default=False)
    justificativa_reprovacao = models.CharField(u'Motivo da Negação do Pedido', null=True, blank=True, max_length=1000)
    avaliado_em = models.DateTimeField(u'Avaliado Em', null=True, blank=True)
    avaliado_por = models.ForeignKey(User, related_name=u'pedido_avaliado_por', null=True)

    def get_total(self):
        return self.quantidade * self.item.valor_medio



class MaterialConsumo(models.Model):
    nome = models.TextField(u'Nome')
    observacao = models.CharField(u'Observação', max_length=500, null=True, blank=True)
    codigo = models.CharField(u"Código", max_length=6, blank=True)

    class Meta:
        verbose_name = u'Material de Consumo'
        verbose_name_plural = u'Materiais de Consumo'


    def __unicode__(self):
        return '%s (Cód: %s)' % (self.nome, self.codigo)

    def save(self):
        if not self.pk:
            if MaterialConsumo.objects.exists():
                id = MaterialConsumo.objects.latest('id')
                self.id = id.pk+1
                self.codigo = id.pk+1
            else:
                self.id = 1
                self.codigo = 1

        super(MaterialConsumo, self).save()

class Configuracao(models.Model):
    nome = models.CharField(u'Nome', max_length=200, null=True)
    endereco = models.CharField(u'Endereço', max_length=2000, null=True)
    municipio = models.ForeignKey('base.Municipio', null=True)
    email = models.CharField(u'Email', max_length=200, null=True)
    telefones = models.CharField(u'Telefones', max_length=1000, null=True, help_text=u'Separar os telefones usando /')
    logo = models.ImageField(u'Logo', null=True, blank=True, upload_to=u'upload/logo/')
    ordenador_despesa = models.ForeignKey(PessoaFisica, verbose_name=u'Ordenador de Despesa', null=True)
    cnpj = models.CharField(u'CNPJ', max_length=200, null=True)


    class Meta:
        verbose_name = u'Variável de Configuração'
        verbose_name_plural = u'Variáveis de Configuração'


class PedidoItem(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    resultado = models.ForeignKey(ResultadoItemPregao, null=True)
    proposta = models.ForeignKey(PropostaItemPregao, null=True)
    quantidade = models.IntegerField(u'Quantidade')
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Pedido do Item'
        verbose_name_plural = u'Pedidos do Item'


    def get_total(self):
        if self.resultado:
            return self.quantidade * self.resultado.valor
        else:
            return self.quantidade * self.item.get_valor_item_lote()

class DotacaoOrcamentaria(models.Model):


    class Meta:
        verbose_name = u'Dotação Orçamentária'
        verbose_name_plural = u'Dotações Orçamentárias'

    def __unicode__(self):
        return 'Dotação: Programa %s - Elemento de Despesa: %s' % (self.programa_num, self.elemento_despesa_num)

class OrdemCompra(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    numero = models.CharField(u'Número da Ordem', max_length=200)
    data = models.DateField(u'Data')
    projeto_atividade_num = models.CharField(u'Número do Projeto de Atividade', max_length=200, null=True, blank=True)
    projeto_atividade_descricao = models.CharField(u'Descrição do Projeto de Atividade', max_length=200, null=True, blank=True)
    programa_num = models.CharField(u'Número do Programa', max_length=200, null=True, blank=True)
    programa_descricao = models.CharField(u'Descrição do Programa', max_length=200, null=True, blank=True)
    fonte_num = models.CharField(u'Número da Fonte', max_length=200, null=True, blank=True)
    fonte_descricao = models.CharField(u'Descrição da Fonte', max_length=200, null=True, blank=True)
    elemento_despesa_num = models.CharField(u'Número do Elemento de Despesa', max_length=200, null=True, blank=True)
    elemento_despesa_descricao = models.CharField(u'Descrição do Elemento de Despesa', max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = u'Ordem de Compra'
        verbose_name_plural = u'Ordens de Compra'

class AtaRegistroPreco(models.Model):
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=12, null=True)
    data_inicio = models.DateField(verbose_name=u'Data de Início', null=True)
    data_fim = models.DateField(verbose_name=u'Data de Vencimento', null=True)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, null=True)
    pregao = models.ForeignKey(Pregao, null=True)
    secretaria = models.ForeignKey(Secretaria, null=True)
    adesao = models.BooleanField(u'Adesão', default=False)
    concluido = models.BooleanField(default=False)
    suspenso = models.BooleanField(default=False)
    cancelado = models.BooleanField(default=False)
    motivo_cancelamento = models.TextField(blank=True)
    dh_cancelamento = models.DateTimeField(blank=True, null=True)
    usuario_cancelamento = models.ForeignKey('base.User', null=True, blank=True)
    orgao_origem = models.CharField(u'Órgão de Origem', null=True, max_length=100)
    num_oficio = models.CharField(u'Número do Ofício', null=True, max_length=100)
    objeto = models.TextField(u'Objeto', null=True)
    liberada_compra = models.BooleanField(u'Liberada para Compra', default=False)

    def __unicode__(self):
        return 'ARP N° %s' % (self.numero)

    def get_situacao(self):
        if self.concluido:
            return u'Concluído'
        elif self.suspenso:
            return u'Suspenso'
        elif self.cancelado:
            return u'Cancelado'
        else:
            return u'Ativo'


class Contrato(models.Model):
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=12)
    data_inicio = models.DateField(verbose_name=u'Data de Início', null=True)
    data_fim = models.DateField(verbose_name=u'Data de Vencimento', null=True)
    continuado = models.BooleanField(default=False)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    pregao = models.ForeignKey(Pregao, null=True)
    concluido = models.BooleanField(default=False)
    suspenso = models.BooleanField(default=False)
    cancelado = models.BooleanField(default=False)
    motivo_cancelamento = models.TextField(blank=True)
    dh_cancelamento = models.DateTimeField(blank=True, null=True)
    usuario_cancelamento = models.ForeignKey('base.User', null=True, blank=True)
    liberada_compra = models.BooleanField(u'Liberada para Compra', default=False)

    def __unicode__(self):
        return 'Contrato N° %s' % (self.numero)

    def get_situacao(self):
        if self.concluido:
            return u'Concluído'
        elif self.suspenso:
            return u'Suspenso'
        elif self.cancelado:
            return u'Cancelado'
        else:
            return u'Ativo'

    def get_carater_continuado(self):
        if self.continuado:
            return u'Sim'
        return u'Não'

    def get_data_fim(self):
        if not Aditivo.objects.filter(contrato=self).exists():
            return self.data_fim
        else:
            return Aditivo.objects.filter(contrato=self).order_by('-data_fim')[0].data_fim

    def get_proximo_aditivo(self):
        if not Aditivo.objects.filter(contrato=self).exists():
            return 1
        return Aditivo.objects.filter(contrato=self).order_by('-ordem')[0].ordem + 1

    def eh_registro_preco(self):
        return self.pregao.eh_ata_registro_preco

    def get_arquivos_publicos(self):
        return AnexoContrato.objects.filter(contrato=self, publico=True)



class Aditivo(models.Model):
    contrato = models.ForeignKey(Contrato)
    ordem = models.PositiveSmallIntegerField(default=0)
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=9, null=True, blank=True)
    data_inicio = models.DateField(db_column='data_inicio', verbose_name=u'Data de Início', null=True, blank=True)
    data_fim = models.DateField(db_column='data_fim', verbose_name=u'Data de Vencimento', null=True, blank=True)
    de_prazo = models.BooleanField(verbose_name=u'Aditivo de Prazo', default=False)
    de_valor = models.BooleanField(verbose_name=u'Aditivo de Valor', default=False)
    de_fiscal = models.BooleanField(verbose_name=u'Aditivo de Fiscal', default=False)


class ItemContrato(models.Model):
    contrato = models.ForeignKey(Contrato)
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    participante = models.ForeignKey(ParticipantePregao)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    quantidade = models.IntegerField(u'Quantidade')

    class Meta:
        ordering = ['item__item']
        verbose_name = u'Item do Contrato'
        verbose_name_plural = u'Itens do Contrato'

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoContrato.objects.filter(item=self, ativo=True)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        else:

            pedidos = PedidoContrato.objects.filter(item=self, ativo=True, setor=usuario.pessoafisica.setor)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        return 0


class PedidoContrato(models.Model):
    contrato = models.ForeignKey(Contrato)
    item = models.ForeignKey(ItemContrato)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    quantidade = models.IntegerField(u'Quantidade')
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Pedido do Contrato'
        verbose_name_plural = u'Pedidos do Contrato'


    def get_total(self):
        return self.quantidade * self.item.valor





class ItemAtaRegistroPreco(models.Model):
    ata = models.ForeignKey(AtaRegistroPreco)
    item = models.ForeignKey(ItemSolicitacaoLicitacao, null=True)
    participante = models.ForeignKey(ParticipantePregao, null=True)
    fornecedor = models.ForeignKey(Fornecedor, null=True)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    quantidade = models.IntegerField(u'Quantidade')
    material = models.ForeignKey('base.MaterialConsumo', null=True)

    class Meta:
        ordering = ['item__item']
        verbose_name = u'Item da ARP'
        verbose_name_plural = u'Itens da ARP'

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        else:

            if not self.ata.adesao:
                if ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                    valor_total = ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria)[0].quantidade
                    pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True, setor=usuario.pessoafisica.setor)
                    if pedidos.exists():
                        return valor_total - pedidos.aggregate(soma=Sum('quantidade'))['soma']
                    else:
                        return valor_total
            else:

                pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True, setor=usuario.pessoafisica.setor)
                if pedidos.exists():
                    return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
                else:
                    return self.quantidade


        return 0




class PedidoAtaRegistroPreco(models.Model):
    ata = models.ForeignKey(AtaRegistroPreco)
    item = models.ForeignKey(ItemAtaRegistroPreco)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    quantidade = models.IntegerField(u'Quantidade')
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Pedido da ARP'
        verbose_name_plural = u'Pedidos da ARP'


    def get_total(self):
        return self.quantidade * self.item.valor