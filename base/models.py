# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.utils.safestring import mark_safe

from newadmin.utils import CepModelField
from decimal import Decimal
from django.db.models import Sum, Q
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
    cnpj = models.CharField(u'CNPJ', max_length=200, null=True)
    responsavel = models.ForeignKey('base.PessoaFisica', verbose_name=u'Responsável', null=True, blank=True, related_name=u'secretaria_responsavel')
    endereco = models.CharField(u'Endereço', max_length=2000, null=True)
    email = models.CharField(u'Email', max_length=200, null=True)
    telefones = models.CharField(u'Telefones', max_length=1000, null=True, help_text=u'Separar os telefones usando /')
    logo = models.ImageField(u'Logo', null=True, blank=True, upload_to=u'upload/logo/')
    eh_ordenadora_despesa = models.BooleanField(u'O responsável pela Secretaria é o Ordenador de Despesa?', default=True)
    ordenador_despesa = models.ForeignKey('base.PessoaFisica', verbose_name=u'Ordenador de Despesa', related_name=u'secretaria_ordenador', null=True)
    cpf_ordenador_despesa = models.CharField(u'CPF do Ordenador de Despesa', max_length=200, null=True)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
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
        ordering = ['nome']
        verbose_name = u'Setor'
        verbose_name_plural = u'Setores'


class ModalidadePregao(models.Model):
    PREGAO_SRP = 10
    CONCORRENCIA_SRP = 11
    CARTA_CONVITE = 1
    CONCORRENCIA = 2
    CONCURSO = 3
    PREGAO = 4
    TOMADA_PRECO = 5
    CREDENCIAMENTO = 6
    CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR = 7
    CHAMADA_PUBLICA_OUTROS = 8
    CHAMADA_PUBLICA_PRONATER = 9


    nome = models.CharField(u'Nome', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
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

class SolicitacaoLicitacaoTmp(models.Model):

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
    DISPENSA_LICITACAO_ATE_8MIL = u'Dispensa de Licitação (Até R$ 8.000,00)'
    DISPENSA_LICITACAO_ATE_15MIL = u'Dispensa de Licitação (Até R$ 15.000,00)'
    CREDENCIAMENTO = u'Credenciamento'
    CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR = u'Chamada Pública - Alimentação Escolar'
    CHAMADA_PUBLICA_OUTROS = u'Chamada Pública - Outros'
    CHAMADA_PUBLICA_PRONATER = u'Chamada Pública - PRONATER'
    TIPO_AQUISICAO_CHOICES = (
        (TIPO_AQUISICAO_LICITACAO, TIPO_AQUISICAO_LICITACAO),
        (TIPO_AQUISICAO_DISPENSA, u'Dispensa de Licitação (Outros)'),
        (DISPENSA_LICITACAO_ATE_8MIL, u'Dispensa de Licitação (Até R$ 8.000,00 - Aquisição de Bens ou Serviços Comuns)'),
        (DISPENSA_LICITACAO_ATE_15MIL, u'Dispensa de Licitação (Até R$ 15.000,00 - Obras ou Serviços de Engenharia)'),
        (TIPO_AQUISICAO_INEXIGIBILIDADE, u'Inexigibilidade de Licitação'),
        (CREDENCIAMENTO, CREDENCIAMENTO),
        (CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR),
        (CHAMADA_PUBLICA_OUTROS, CHAMADA_PUBLICA_OUTROS),
        (CHAMADA_PUBLICA_PRONATER, CHAMADA_PUBLICA_PRONATER),
    )
    num_memorando = models.CharField(u'Número do Memorando', max_length=80)
    objeto = models.TextField(u'Descrição do Objeto')
    objetivo = models.TextField(u'Objetivo')

    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    tipo = models.CharField(u'Tipo', max_length=50, choices=TIPO_CHOICES, default=LICITACAO)
    tipo_aquisicao = models.CharField(u'Tipo de Aquisição', max_length=50, choices=TIPO_AQUISICAO_CHOICES, default=TIPO_AQUISICAO_LICITACAO)
    data_cadastro = models.DateTimeField(u'Cadastrada em')
    cadastrado_por = models.ForeignKey(User, null=True, blank=True)
    setor_origem = models.ForeignKey(Setor, verbose_name=u'Setor de Origem', related_name='setor_origem_tmp', null=True, blank=True)
    setor_atual = models.ForeignKey(Setor, verbose_name=u'Setor Atual', related_name='setor_atual_tmp', null=True, blank=True)
    arp_origem = models.ForeignKey('base.AtaRegistroPreco', null=True, related_name=u'arp_da_solicitacao_tmp')
    contrato_origem = models.ForeignKey('base.Contrato', null=True, related_name=u'contrato_da_solicitacao_tmp')
    credenciamento_origem = models.ForeignKey('base.Credenciamento', null=True, related_name=u'credenciamento_da_solicitacao_tmp')


    def __unicode__(self):
        return u'Solicitação Temp N°: %s' % self.num_memorando

    class Meta:
        verbose_name = u'Solicitação Temp'
        verbose_name_plural = u'Solicitações temp'


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
    DISPENSA_LICITACAO_ATE_8MIL = u'Dispensa de Licitação (Até R$ 8.000,00)'
    DISPENSA_LICITACAO_ATE_15MIL = u'Dispensa de Licitação (Até R$ 15.000,00)'
    CREDENCIAMENTO = u'Credenciamento'
    CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR = u'Chamada Pública - Alimentação Escolar'
    CHAMADA_PUBLICA_OUTROS = u'Chamada Pública - Outros'
    CHAMADA_PUBLICA_PRONATER = u'Chamada Pública - PRONATER'


    TIPO_AQUISICAO_CHOICES = (
        (TIPO_AQUISICAO_LICITACAO, TIPO_AQUISICAO_LICITACAO),
        (TIPO_AQUISICAO_DISPENSA, u'Dispensa de Licitação (Outros)'),
        (DISPENSA_LICITACAO_ATE_8MIL, u'Dispensa de Licitação (Até R$ 8.000,00 - Aquisição de Bens ou Serviços Comuns)'),
        (DISPENSA_LICITACAO_ATE_15MIL, u'Dispensa de Licitação (Até R$ 15.000,00 - Obras ou Serviços de Engenharia)'),
        (TIPO_AQUISICAO_INEXIGIBILIDADE, u'Inexigibilidade de Licitação'),
        (CREDENCIAMENTO, CREDENCIAMENTO),
        (CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR),
        (CHAMADA_PUBLICA_OUTROS, CHAMADA_PUBLICA_OUTROS),
        (CHAMADA_PUBLICA_PRONATER, CHAMADA_PUBLICA_PRONATER),
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
    liberada_para_pedido = models.BooleanField(u'Liberada para Pedido', default=False)
    arp_origem = models.ForeignKey('base.AtaRegistroPreco', null=True, related_name=u'arp_da_solicitacao')
    contrato_origem = models.ForeignKey('base.Contrato', null=True, related_name=u'contrato_da_solicitacao')
    credenciamento_origem = models.ForeignKey('base.Credenciamento', null=True, related_name=u'credenciamento_da_solicitacao')
    termo_inexigibilidade = models.FileField(u'Termo de Inexigibilidade', null=True, blank=True, upload_to=u'upload/minutas/')



    def __unicode__(self):
        return u'Solicitação N°: %s' % self.num_memorando

    class Meta:
        verbose_name = u'Solicitação de Licitação'
        verbose_name_plural = u'Solicitações de Licitação'


    def tem_empate_propostas(self):
        valores = list()
        for pesquisa in PesquisaMercadologica.objects.filter(solicitacao=self):
            total = Decimal(0.00)
            for item in ItemPesquisaMercadologica.objects.filter(pesquisa=pesquisa):
                total += item.valor_maximo * item.item.quantidade
            valores.append(total)
        valores.sort()
        if len(valores) > 1 and valores[0] == valores[1]:
            return True
        return False

    def tem_valor_acima_permitido(self):

        if self.tipo_aquisicao == self.TIPO_AQUISICAO_LICITACAO:
            return False
        if self.tem_item_cadastrado() and ItemPesquisaMercadologica.objects.filter(pesquisa__solicitacao=self).exists():
            if self.tipo_aquisicao == self.DISPENSA_LICITACAO_ATE_8MIL and self.get_valor_da_solicitacao_dispensa() > 8000:
                return True
            elif self.tipo_aquisicao == self.DISPENSA_LICITACAO_ATE_15MIL and self.get_valor_da_solicitacao_dispensa() > 15000:
                return True
        return False

    def pode_cadastrar_pesquisa(self):
        if self.tipo_aquisicao == SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE:
            return not PesquisaMercadologica.objects.filter(solicitacao=self).exists()
        else:
            return True

    def eh_credenciamento(self):
        return self.tipo_aquisicao in [self.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, self.CHAMADA_PUBLICA_OUTROS, self.CHAMADA_PUBLICA_PRONATER, self.CREDENCIAMENTO]

    def recebida_setor(self, setor_do_usuario):
        movimentacao = MovimentoSolicitacao.objects.filter(solicitacao=self)
        if movimentacao.exists():
            ultima_movimentacao = movimentacao.latest('id')
            if ultima_movimentacao.setor_destino == setor_do_usuario and ultima_movimentacao.data_recebimento:
                return True
        elif self.setor_atual == setor_do_usuario:
            itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self)
            if itens.exists() and self.tipo == SolicitacaoLicitacao.LICITACAO:
                return True
            elif self.tipo == SolicitacaoLicitacao.COMPRA or self.tipo == SolicitacaoLicitacao.ADESAO_ARP:
                return True
        return False

    def tem_item_sem_pesquisa(self):
        for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self):
            if not item.recebeu_pesquisa_todos_fornecedores():
                return True
        return False

    def pode_receber_pedidos_secretarias(self):
        if self.prazo_resposta_interessados:
            return self.prazo_resposta_interessados >= datetime.date.today()
        return False

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
        if AtaRegistroPreco.objects.filter(solicitacao=self).exists():
            return AtaRegistroPreco.objects.filter(solicitacao=self)[0]
        return False

    def eh_dispensa(self):
        return self.tipo_aquisicao in [self.TIPO_AQUISICAO_DISPENSA, self.DISPENSA_LICITACAO_ATE_8MIL, self.DISPENSA_LICITACAO_ATE_15MIL]

    def eh_inexigibilidade(self):
        return self.tipo_aquisicao == self.TIPO_AQUISICAO_INEXIGIBILIDADE

    def pode_gerar_ordem(self):
        return  self.eh_inexigibilidade() or self.eh_dispensa()

    def eh_pedido(self):
        return self.arp_origem or self.contrato_origem or self.credenciamento_origem

    def tem_proposta(self):
        for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self):
            if not ItemPesquisaMercadologica.objects.filter(item=item).exists():
                return False
        return True

    def get_pedidos_secretarias(self, secretaria=None):
        ids= list()
        ids_secretaria = list()
        itens = ItemQuantidadeSecretaria.objects.filter(solicitacao=self)
        if secretaria:
            itens = itens.filter(secretaria=secretaria)

        for item in itens:
            if item.secretaria.id not in ids_secretaria:
                ids.append(item.id)
                ids_secretaria.append(item.secretaria.id)

        return ItemQuantidadeSecretaria.objects.filter(id__in=ids)



    def tem_pedidos_outras_secretarias(self):
        return ItemQuantidadeSecretaria.objects.filter(solicitacao=self).distinct('secretaria').count() > 1

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


    def reorganiza_itens(self):
        contador = 1
        for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self).order_by('id'):
            item.item = contador
            item.save()
            contador += 1


    def tem_pedidos_pendentes(self):
        return ItemQuantidadeSecretaria.objects.filter(solicitacao=self, avaliado_em__isnull=True).exists()

    def tem_pedidos_compra(self):
        return PedidoContrato.objects.filter(solicitacao=self, ativo=True).exists() or PedidoAtaRegistroPreco.objects.filter(solicitacao=self, ativo=True).exists() or PedidoCredenciamento.objects.filter(solicitacao=self, ativo=True).exists()

    def get_pregao(self):
        if Pregao.objects.filter(solicitacao=self).exists():
            return Pregao.objects.filter(solicitacao=self)[0]
        return False

    def eh_maior_desconto(self):
        return self.get_pregao().eh_maior_desconto()

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
            if OrdemCompra.objects.filter(solicitacao=self).exists():
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


    def get_valor_da_solicitacao_dispensa(self):
        total = Decimal(0.00)
        menor_proposta = 10000000000000000
        propostas = PesquisaMercadologica.objects.filter(solicitacao=self)
        for proposta in propostas:
            total = 0
            for item in ItemPesquisaMercadologica.objects.filter(pesquisa=proposta):
                total += item.valor_maximo * item.item.quantidade
            if total < menor_proposta:
                menor_proposta = total

        return menor_proposta

    def get_valor_da_solicitacao(self):
        total = Decimal(0.00)
        propostas = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self)
        for proposta in propostas:
            total += proposta.valor_medio * proposta.quantidade

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
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=20, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(u'Total', decimal_places=2, max_digits=20, null=True, blank=True)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    obs = models.CharField(u'Observação', max_length=3000, null=True, blank=True)
    ativo = models.BooleanField(u'Ativo', default=True)
    eh_lote = models.BooleanField(u'Lote', default=False)
    arquivo_referencia_valor_medio = models.FileField(u'Arquivo com a Referência do Valor Médio', null=True, upload_to=u'upload/referencias_valor_medio/')

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

    def get_valor_item_ata(self):
        if ItemAtaRegistroPreco.objects.filter(material=self.material, ata__solicitacao=self.solicitacao).exists():
            return ItemAtaRegistroPreco.objects.filter(material=self.material, ata__solicitacao=self.solicitacao)[0].valor

    def tem_valor_final_preenchido(self):
        itens_lote = ItemLote.objects.filter(lote=self).values_list('item', flat=True)
        return PropostaItemPregao.objects.filter(item__in=itens_lote, valor_item_lote__isnull=False).exists()

    def get_valor_unitario_proposto(self):
        if ItemLote.objects.filter(item=self).exists():
            lote = ItemLote.objects.filter(item=self)[0].lote
            if lote.get_vencedor():
                vencedor = lote.get_vencedor().participante
                if vencedor:
                    if PropostaItemPregao.objects.filter(item=self, participante=vencedor).exists():
                        return PropostaItemPregao.objects.filter(item=self, participante=vencedor)[0].valor
        return False

    def get_melhor_proposta(self):
        tem = ItemPesquisaMercadologica.objects.filter(item=self).order_by('valor_maximo')
        if tem.exists():
            return tem[0].valor_maximo
        return 0

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

    def get_valor_medio_total(self):
        return self.valor_medio*self.quantidade


    def get_valor_final_total(self):
        valor = self.get_vencedor()
        if valor:
            valor = valor.valor
            return valor * self.quantidade
        return 0

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

    def tem_pedidos_outras_secretarias(self):
        return ItemQuantidadeSecretaria.objects.filter(item=self).count() > 1

    def get_pedido_secretaria(self):
        usuario = tl.get_user()
        if ItemQuantidadeSecretaria.objects.filter(secretaria=usuario.pessoafisica.setor.secretaria, item=self).exists():
            return str(ItemQuantidadeSecretaria.objects.filter(secretaria=usuario.pessoafisica.setor.secretaria, item=self)[0].quantidade).replace('.', ',')
        return 0

    def get_id_lote(self):
        return ItemLote.objects.filter(item=self)[0].lote.item

    def get_lote(self):
        return ItemLote.objects.filter(item=self)[0].lote

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
            preco = PropostaItemPregao.objects.filter(participante=lance_minimo.participante, item=self, valor__gt=0)
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

    def recebeu_pesquisa_todos_fornecedores(self):
        return PesquisaMercadologica.objects.filter(solicitacao=self.solicitacao).count() == ItemPesquisaMercadologica.objects.filter(item=self).count()


    def get_reducao_total(self):
        if self.get_lance_minimo_valor():
            reducao = self.get_lance_minimo_valor() / self.valor_medio
            ajuste= 1-reducao
            return u'%s%%' % (ajuste.quantize(TWOPLACES) * 100)
        return None

    def get_reducao_total_final(self):
        if self.get_valor_medio_total() and self.get_valor_final_total():
            reducao = self.get_valor_final_total() / self.get_valor_medio_total()
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

    def get_economizado(self):
        return (self.valor_medio - self.get_vencedor().valor) * self.quantidade

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
        if self.eh_ativo():
            lance_minimo = self.get_lance_minimo()
            if lance_minimo and not lance_minimo.participante.me_epp:
                valor_lance = lance_minimo.valor
                limite_lance = valor_lance + (valor_lance*5)/100
                lances_da_rodada = LanceItemRodadaPregao.objects.filter(declinio=False, item=self).order_by('valor')

                rodada_atual = False
                if RodadaPregao.objects.filter(item=self, atual=True).exists():
                    rodada_atual = RodadaPregao.objects.filter(item=self, atual=True)[0]
                for item in lances_da_rodada:
                    declinou_antes = rodada_atual and LanceItemRodadaPregao.objects.filter(item=self, participante=item.participante, rodada__rodada__lt=rodada_atual.rodada, valor__isnull=True).exists()


                    if item.participante.me_epp and item.valor <= limite_lance and LanceItemRodadaPregao.objects.filter(item=self, participante=item.participante).count() <= LanceItemRodadaPregao.objects.filter(item=self, participante=self.get_lance_minimo().participante).count() and ((declinou_antes and not LanceItemRodadaPregao.objects.filter(item=self, participante=item.participante, rodada=rodada_atual, valor__isnull=True).exists()) or (not declinou_antes and rodada_atual and not LanceItemRodadaPregao.objects.filter(item=self, participante=item.participante, rodada=rodada_atual, valor__isnull=True).count() > 1)):

                        return item.participante

                propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, desistencia=False, desclassificado=False)
                for proposta in propostas:
                    declinou_antes = rodada_atual and LanceItemRodadaPregao.objects.filter(item=self, participante=proposta.participante, rodada__rodada__lt=rodada_atual.rodada, valor__isnull=True).exists()
                    if proposta.participante.me_epp and proposta.valor <= limite_lance and (LanceItemRodadaPregao.objects.filter(item=self, participante=proposta.participante).count() <= LanceItemRodadaPregao.objects.filter(item=self, participante=self.get_lance_minimo().participante).count()) and ((declinou_antes and not LanceItemRodadaPregao.objects.filter(item=self, participante=proposta.participante, rodada=rodada_atual, valor__isnull=True).exists()) or (not declinou_antes and rodada_atual and not LanceItemRodadaPregao.objects.filter(item=self, participante=proposta.participante, rodada=rodada_atual, valor__isnull=True).count() > 1)):
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
        participantes = self.get_lista_participantes(ativos=True)
        valor_maximo_aceito = None
        if participantes.count()<=3:
            return
        else:
            valores = participantes.order_by('valor').values('valor').distinct()
            if len(valores) > 2:
                valor_maximo_aceito = valores[2]['valor']
            melhor_valor = participantes[0].valor
            participantes.update(desclassificado=False, desistencia=False, concorre=True)
            ordenado = participantes.order_by('-valor')

            for item in ordenado:
                # if ordenado.filter(concorre=True).count()<=3:
                #     continue
                if item.valor > (melhor_valor + (10*melhor_valor)/100):
                    if valor_maximo_aceito and item.valor > valor_maximo_aceito:
                        item.concorre = False
                        item.save()
            concorrentes = participantes.filter(concorre=True).count()
            if  concorrentes >= 3:
                return
            else:

                for item in PropostaItemPregao.objects.filter(item=self, concorre=False, desclassificado=False, desistencia=False).order_by('valor'):
                    if concorrentes < 3 or item.valor <= valores[len(valores)-1]['valor']:
                        item.concorre = True
                        item.save()
                        concorrentes += 1
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
        return ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO, participante__excluido_dos_itens=False, participante__desclassificado=False, empate=True)


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
        return 0

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
                        propostas = PropostaItemPregao.objects.filter(item=self, item__eh_lote=True).order_by('valor')
                    else:
                        propostas = PropostaItemPregao.objects.filter(item=self, item__eh_lote=False).order_by('valor')



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

                        if opcao[1] > self.valor_medio or PropostaItemPregao.objects.filter(participante=opcao[0].participante, item=self, desclassificado=True).exists() or PropostaItemPregao.objects.filter(participante=opcao[0].participante, item=self, desistencia=True).exists():
                            novo_resultado.situacao = ResultadoItemPregao.DESCLASSIFICADO
                        else:
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
        if not ItemLote.objects.filter(item=self).exists():
            return ResultadoItemPregao.objects.filter(item=self).exists()
        else:
            lote = ItemLote.objects.filter(item=self)
            return ResultadoItemPregao.objects.filter(item__in=lote.values_list('lote', flat=True)).exists()

    def get_itens_do_lote(self):
        itens = ItemLote.objects.filter(lote=self)
        return ItemSolicitacaoLicitacao.objects.filter(id__in=itens.values_list('item', flat=True))


    def get_valor_total_item_lote(self):
        total = 0
        itens = self.get_itens_do_lote()
        for item in itens:
            if item.get_valor_item_lote():
                total += item.get_valor_item_lote()
        return total


    def tem_pesquisa_registrada(self):
        return ItemPesquisaMercadologica.objects.filter(item=self).exists()

    def get_item_arp(self):
        return ItemAtaRegistroPreco.objects.filter(item=self)[0]

    def get_item_contrato(self):
        return ItemContrato.objects.filter(item=self)[0]


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

    def __unicode__(self):
        return u'Item %s do Lote: %s' % (self.item, self.lote)

class OpcaoLCN(models.Model):
    descricao = models.CharField(u'Descrição', max_length=5000)

    class Meta:
        verbose_name = u'Opção da LCN'
        verbose_name_plural = u'Opções da LCN'

    def __unicode__(self):
        return self.descricao


def upload_path_termo_homologacao(instance, filename):
    return os.path.join('upload/homologacoes/%s/' % instance.id, filename)

class Pregao(models.Model):
    CADASTRADO = u'Publicado'
    DESERTO = u'Deserto'
    FRACASSADO = u'Fracassado'
    CONCLUIDO = u'Homologado'
    SUSPENSO = u'Suspenso'
    REVOGADO = u'Revogado/Anulado'
    ADJUDICADO = u'Adjudicado'


    SITUACAO_CHOICES = (
        (CADASTRADO, CADASTRADO),
        (DESERTO, DESERTO),
        (FRACASSADO, FRACASSADO),
        (SUSPENSO, SUSPENSO),
        (ADJUDICADO, ADJUDICADO),
        (CONCLUIDO, CONCLUIDO),
        (REVOGADO, REVOGADO),
    )

    COMPRA_MATERIAL_CONSUMO = u'Compra de Material de Consumo'
    COMPRA_MATERIAL_PERMANENTE = u'Compra de Material Permanente'
    OBRAS = u'Obras'
    SERVICOS_ENGENHARIA = u'Serviços de Engenharia'
    SERVICOS_REFORMA_E_EQUIPAMENTO = u'Serviço de Reforma de Edifício ou de Equipamento'
    SERVICOS_OUTRO = u'Serviços – Outros'

    OBJETO_TIPO_CHOICES = (
        (COMPRA_MATERIAL_CONSUMO, COMPRA_MATERIAL_CONSUMO),
        (COMPRA_MATERIAL_PERMANENTE, COMPRA_MATERIAL_PERMANENTE),
        (OBRAS, OBRAS),
        (SERVICOS_ENGENHARIA, SERVICOS_ENGENHARIA),
        (SERVICOS_REFORMA_E_EQUIPAMENTO, SERVICOS_REFORMA_E_EQUIPAMENTO),
        (SERVICOS_OUTRO, SERVICOS_OUTRO),

    )

    CATEGORIA_SUSPENSAO_CHOICES = (
        (u'', '--------------'),
        (u'Análise de Amostras', u'Análise de Amostras'),
        (u'Documentação Complementar', u'Documentação Complementar'),
        (u'Impugnação', u'Impugnação'),
        (u'Parecer Técnico', u'Parecer Técnico'),
        (u'Prazo de Recurso', u'Prazo de Recurso'),
        (u'Proposta Final', u'Proposta Final'),
        (u'Revisão do Processo', u'Revisão do Processo'),
    )
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    num_pregao = models.CharField(u'Número do Pregão', max_length=255)
    modalidade = models.ForeignKey(ModalidadePregao, verbose_name=u'Modalidade / Procedimento')
    objeto = models.TextField(u'Objeto', null=True)
    fundamento_legal = models.CharField(u'Fundamento Legal', max_length=5000, null=True, blank=True)
    tipo = models.ForeignKey(TipoPregao, verbose_name=u'Critério de Julgamento', null=True, blank=True)
    criterio = models.ForeignKey(CriterioPregao, verbose_name=u'Critério de Adjudicação')
    aplicacao_lcn_123_06 = models.ForeignKey(OpcaoLCN, verbose_name=u'MPE – Aplicação Da LCN 123/06 (Lei 123/06)', null=True, blank=True)
    data_inicio = models.DateField(u'Data de Início da Retirada do Edital', null=True, blank=True)
    data_termino = models.DateField(u'Data de Término da Retirada do Edial', null=True, blank=True)
    data_abertura = models.DateField(u'Data de Abertura do Certame', null=True, blank=True)
    hora_abertura = models.TimeField(u'Hora de Abertura do Certame', null=True, blank=True)
    local = models.CharField(u'Local', max_length=1500)
    responsavel = models.CharField(u'Responsável', max_length=255)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    categoria_suspensao = models.CharField(u'Situação', max_length=100, choices=CATEGORIA_SUSPENSAO_CHOICES, null=True, blank=True)
    obs = models.CharField(u'Observação', max_length=3000, null=True, blank=True)
    data_adjudicacao = models.DateField(u'Data da Adjudicação', null=True, blank=True)
    data_homologacao = models.DateField(u'Data da Homologação', null=True, blank=True)
    data_revogacao = models.DateField(u'Data da Revogação', null=True, blank=True)
    data_suspensao = models.DateField(u'Data da Suspensão', null=True, blank=True)
    ordenador_despesa = models.ForeignKey('base.PessoaFisica', verbose_name=u'Ordenador de Despesa', null=True, blank=True)
    eh_ata_registro_preco = models.BooleanField(u'Ata de Registro de Preço?', default=True)
    arquivo_homologacao = models.FileField(u'Termo de Homologação', null=True, blank=True, upload_to=upload_path_termo_homologacao)
    pode_homologar = models.BooleanField(u'Pode Homologar', default=False)
    comissao = models.ForeignKey('base.ComissaoLicitacao', verbose_name=u'Comissão de Licitação', null=True, blank=True)
    data_retorno = models.DateField(u'Data do Retorno', null=True, blank=True)
    sine_die = models.NullBooleanField(u'Sine Die', null=True, blank=True)
    republicado = models.BooleanField(u'Republicado', default=False)
    objeto_tipo = models.CharField(u'Objeto - Tipo', choices=OBJETO_TIPO_CHOICES, max_length=200, null=True, blank=True)
    valor_total = models.CharField(u'Valor Total Orçado', max_length=20, null=True, blank=True)
    recurso_proprio = models.CharField(u'Recurso Próprio', max_length=20, null=True, blank=True)
    recurso_federal = models.CharField(u'Recurso Transferido (Federal)', max_length=20, null=True, blank=True)
    recurso_estadual = models.CharField(u'Recurso Transferido (Estadual)', max_length=20, null=True, blank=True)
    recurso_municipal = models.CharField(u'Recurso Transferido (Municipal)', max_length=20, null=True, blank=True)


    class Meta:
        verbose_name = u'Pregão'
        verbose_name_plural = u'Pregões'
        ordering = ['-data_abertura']



    def __unicode__(self):
        return u'%s N° %s' % (self.modalidade, self.num_pregao)

    def save(self):

        if self.modalidade.id in [ModalidadePregao.PREGAO_SRP, ModalidadePregao.CONCORRENCIA_SRP]:
            self.eh_ata_registro_preco = True
        else:
            self.eh_ata_registro_preco = False
        super(Pregao, self).save()


    def tem_item_deserto_fracassado(self):
        return ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao).filter(Q(situacao=ItemSolicitacaoLicitacao.FRACASSADO) | Q(situacao=ItemSolicitacaoLicitacao.DESERTO)).exists()
    def eh_credenciamento(self):
        return self.modalidade.id in [ModalidadePregao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, ModalidadePregao.CHAMADA_PUBLICA_OUTROS, ModalidadePregao.CHAMADA_PUBLICA_PRONATER, ModalidadePregao.CREDENCIAMENTO]
    def eh_maior_desconto(self):
        if not self.tipo:
            return False
        if self.tipo.id == TipoPregao.DESCONTO:
            return True
        return False
    def get_local(self):
        return u'Dia %s às %s, no(a) %s' % (self.data_abertura.strftime('%d/%m/%y'), self.hora_abertura, self.local)

    def get_titulo(self):
        return u'%s N° %s' % (self.modalidade, self.num_pregao)

    def tem_download(self):
        return LogDownloadArquivo.objects.filter(arquivo__pregao=self).exists()

    def tem_participante_ativo(self):
        return ParticipantePregao.objects.filter(pregao=self, desclassificado=False, excluido_dos_itens=False).exists()

    def eh_ativo(self):
        return self.situacao not in [Pregao.ADJUDICADO, Pregao.FRACASSADO, Pregao.DESERTO, Pregao.CONCLUIDO, Pregao.SUSPENSO]

    def get_situacao(self):
        if self.data_homologacao:
            if self.eh_credenciamento():
                return u'Credenciado em %s' % self.data_homologacao.strftime('%d/%m/%y')
            else:
                return u'Homologado em %s' % self.data_homologacao.strftime('%d/%m/%y')
        elif self.data_adjudicacao:
            return u'Adjudicado em %s' % self.data_adjudicacao.strftime('%d/%m/%y')
        elif self.situacao == self.REVOGADO:
            if self.data_revogacao:
                return u'Revogado em %s' % self.data_revogacao.strftime('%d/%m/%y')
            else:
                return u'Revogado'

        elif self.situacao == self.SUSPENSO:

            if self.data_suspensao:
                texto = u'Suspenso em %s' % self.data_suspensao.strftime('%d/%m/%y')
            else:
                texto = u'Suspenso'

            if self.sine_die:
                texto += u' - Sine die'


            if self.categoria_suspensao:
                texto += u'<br>Motivo: %s ' % self.categoria_suspensao
            return mark_safe(texto)

        else:
            return self.situacao

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
                    if ResultadoItemPregao.objects.filter(participante=fornecedor).exists():
                        valor_resultado = ResultadoItemPregao.objects.filter(participante=fornecedor)[0].valor
                        if valor_resultado < limite_lance:
                            tem_empate_ficto = True

                    elif int(resultado[indice][0]) < limite_lance:
                        tem_empate_ficto = True
            indice += 1

        return tem_empate_ficto and ResultadoItemPregao.objects.filter(participante__pregao=pregao).exists()

    def eh_suspenso(self):
        return self.situacao in [Pregao.SUSPENSO]

    def eh_pregao(self):
        return self.modalidade.id  in [ModalidadePregao.PREGAO_SRP, ModalidadePregao.PREGAO]

    def tem_resultado(self):
        return ResultadoItemPregao.objects.filter(item__solicitacao=self.solicitacao).exists()

    def tem_proposta(self):
        return PropostaItemPregao.objects.filter(pregao=self).exists()

    def get_contrato(self):
        if Contrato.objects.filter(pregao=self).exists():
            return Contrato.objects.filter(pregao=self)[0]
        return False

    def get_arp(self):
        if AtaRegistroPreco.objects.filter(pregao=self).exists():
            return AtaRegistroPreco.objects.filter(pregao=self)[0]
        return False

    def tem_item_sem_lote(self):
        itens_em_lotes = ItemLote.objects.filter(item__solicitacao=self.solicitacao)
        return ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False).exclude(id__in=itens_em_lotes.values_list('item', flat=True))

    def tem_lance_registrado(self):
        return LanceItemRodadaPregao.objects.filter(rodada__pregao=self).exists()

    def tem_ocorrencia(self):
        return HistoricoPregao.objects.filter(pregao=self).exists()

    def get_valor_total(self, ganhador=None):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
        total = 0
        for item in itens_pregao:
            if item.get_total_lance_ganhador():
                if ganhador:
                    if item.get_vencedor().participante == ganhador:
                        total = total + item.get_total_lance_ganhador()
                else:
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

    def get_vencedores(self):
        ids_vencedores = list()
        for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao):
            if item.get_vencedor():
                ids_vencedores.append(item.get_vencedor().participante.id)


        return ParticipantePregao.objects.filter(id__in=ids_vencedores)

    def get_total_previsto(self):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])

        valor = 0

        for item in itens_pregao.order_by('item'):
            if item.get_vencedor():
                valor = valor + (item.valor_medio*item.quantidade)
        return valor

    def get_total_final(self):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])

        valor = 0

        for item in itens_pregao.order_by('item'):
            if item.get_vencedor():
                valor = valor + item.get_total_lance_ganhador()
        return valor

    def get_total_desconto(self):
        if self.get_total_previsto():
            reducao = self.get_total_final() / self.get_total_previsto()
            ajuste= 1-reducao
            total_desconto_geral = u'%s%%' % (ajuste.quantize(TWOPLACES) * 100)
            return total_desconto_geral
        else:
            return 0


    def get_total_economizado(self):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])

        valor = 0
        for item in itens_pregao.order_by('item'):
            if item.get_vencedor():

                valor = valor + item.get_economizado()
        return valor

    def get_economia_alcancada(self):
        eh_lote = self.criterio.id == CriterioPregao.LOTE
        if eh_lote:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).only('valor_medio', 'quantidade')
        else:
            itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).only('valor_medio', 'quantidade')

        previsto = 0
        final = 0
        economizado = 0
        total_desconto_geral = 0
        for item in itens_pregao.order_by('item'):
            if item.get_vencedor():
                previsto = previsto + (item.valor_medio*item.quantidade)
                final = final + item.get_total_lance_ganhador()
                economizado = economizado + item.get_economizado()

        if previsto:
            reducao = final / previsto
            ajuste= 1-reducao
            total_desconto_geral = u'%s%%' % (ajuste.quantize(TWOPLACES) * 100)
        return previsto, final, total_desconto_geral, economizado




#TODO usar esta estrutura para pregão por lote
class ItemPregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    material = models.ForeignKey('base.MaterialConsumo')
    unidade = models.CharField(u'Unidade de Medida', max_length=500)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=20, decimal_places=2)
    total = models.DecimalField(u'Total', max_digits=20, decimal_places=2)

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
    excluido_dos_itens = models.BooleanField(u'Excluído dos Itens', default=False)
    credenciado = models.BooleanField(u'Credenciado', default=True)

    class Meta:
        verbose_name = u'Participante do Pregão'
        verbose_name_plural = u'Participantes do Pregão'
        ordering = ['desclassificado', 'fornecedor__razao_social']

    def __unicode__(self):
        return self.fornecedor.razao_social

    def pode_remover(self):
        return not ParticipanteItemPregao.objects.filter(participante=self).exists() and  not PropostaItemPregao.objects.filter(participante=self).exists()

class VisitantePregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    nome = models.CharField(u'Nome', max_length=255, null=True, blank=True)
    cpf = models.CharField(u'CPF', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = u'Visitante do Pregão'
        verbose_name_plural = u'Visitantes do Pregão'

    def __unicode__(self):
        return self.nome

class ParticipanteItemPregao(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Item')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')


    class Meta:
        verbose_name = u'Participante do Item do Pregão'
        verbose_name_plural = u'Participantes do Item do Pregão'

    def __unicode__(self):
        return self.participante.fornecedor.razao_social

class PropostaItemPregao(models.Model):
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Solicitação')
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    participante = models.ForeignKey(ParticipantePregao,verbose_name=u'Participante')
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    desclassificado = models.BooleanField(u'Desclassificado', default=False)
    motivo_desclassificacao = models.CharField(u'Motivo da Desclassificação', max_length=2000, null=True, blank=True)
    desistencia = models.BooleanField(u'Desistência', default=False)
    motivo_desistencia= models.CharField(u'Motivo da Desistência', max_length=2000, null=True, blank=True)
    concorre = models.BooleanField(u'Concorre', default=True)
    valor_item_lote = models.DecimalField(u'Valor do Item do Lote', max_digits=20, decimal_places=2, null=True, blank=True)


    class Meta:
        verbose_name = u'Valor do Item do Pregão'
        verbose_name_plural = u'Valores do Item do Pregão'

    def __unicode__(self):
        return u'%s - %s' % (self.item, self.participante)

    def get_situacao_valor(self):

        valor_maximo = PropostaItemPregao.objects.filter(item=self.item).order_by('valor')[0].valor
        if valor_maximo:
            if self.valor > valor_maximo + (10*valor_maximo)/100:
                return u'<font color="green"><b>Acima dos 10%</b></font>'
            else:
                return u'<b>Dentro dos 10%</b>'
        else:
            return u'<font color=red>Valor Máximo não informado.</font>'

    def ativo(self):
        return not self.desclassificado and not self.desistencia

    def get_resultado_participante_item(self):
        if ResultadoItemPregao.objects.filter(participante=self.participante, item=self.item).exists():
            return ResultadoItemPregao.objects.filter(participante=self.participante, item=self.item)[0].ordem


class RodadaPregao(models.Model):
    rodada = models.IntegerField(verbose_name=u'Rodada de Lances')
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    item = models.ForeignKey(ItemSolicitacaoLicitacao,verbose_name=u'Item da Solicitação')
    atual = models.BooleanField(u'Rodada Atual', default=False)

    class Meta:
        verbose_name = u'Rodada do Pregão'
        verbose_name_plural = u'Rodadas do Pregão'

    def __unicode__(self):
        return u'Rodada: %s do Pregão: %s' % (self.rodada, self.pregao)

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
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2, null=True, blank=True)
    declinio = models.BooleanField(u'Declínio', default=False)
    ordem_lance = models.IntegerField(u'Ordem')


    objects = models.Manager()


    class Meta:
        verbose_name = u'Lance da Rodada do Pregão'
        verbose_name_plural = u'Lances da Rodada do Pregão'
        ordering = ['-valor']

    def __unicode__(self):
        return u'Lance %s da Rodada: %s' % (self.id, self.rodada.rodada)

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

    CEDIDO = u'Cedido de outra Unidade Administrativa'
    EMPREGADO_PUBLICO = u'Empregado Público'
    SERVIDOR_COMISSIONADO = u'Servidor Público Comissionado'
    SERVIDOR_EFETIVO = u'Servidor Público Efetivo'
    SERVIDOR_TEMPORARIO = u'Servidor Temporário'
    TERCEIRO = u'Terceiro estranho à Administração'

    VINCULO_CHOICES = (
        (CEDIDO, CEDIDO),
        (EMPREGADO_PUBLICO, EMPREGADO_PUBLICO),
        (SERVIDOR_COMISSIONADO, SERVIDOR_COMISSIONADO),
        (SERVIDOR_EFETIVO, SERVIDOR_EFETIVO ),
        (SERVIDOR_TEMPORARIO, SERVIDOR_TEMPORARIO),
        (TERCEIRO, TERCEIRO),
    )

    user = models.OneToOneField(User, null=True, blank=True)
    nome = models.CharField(max_length=80)
    matricula = models.CharField(u'Matrícula', max_length=50, null=True)
    vinculo = models.CharField(u'Vínculo', max_length=200, choices=VINCULO_CHOICES, default=SERVIDOR_EFETIVO)
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

    class Meta:
        verbose_name = u'Estado'
        verbose_name_plural = u'Estados'

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
    data_designacao = models.DateField(u'Data de Designação', null=True)
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
    MEMBRO_SUPLENTE = u'Membro Suplente'
    #MEMBRO_CPL = u'Membro da CPL'
    FUNCAO_CHOICES = (
        (APOIO, APOIO),
        (MEMBRO_EQUIPE, MEMBRO_EQUIPE),
        (MEMBRO_SUPLENTE, MEMBRO_SUPLENTE),
        (PREGOEIRO, PREGOEIRO),
        (PRESIDENTE, PRESIDENTE),
    )
    comissao = models.ForeignKey(ComissaoLicitacao)
    membro = models.ForeignKey(PessoaFisica)
    matricula = models.CharField(u'Matrícula', max_length=100)
    funcao = models.CharField(u'Função', max_length=100, choices=FUNCAO_CHOICES, default=APOIO)

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
    validade_proposta = models.CharField(u'Dias de Validade da Proposta', max_length=200, null=True,blank=True)
    cadastrada_em = models.DateTimeField(u'Data de Envio da Proposta', null=True,blank=True)
    arquivo = models.FileField(u'Arquivo da Proposta', upload_to=u'upload/pesquisas/', null=True,blank=True)
    numero_ata = models.CharField(u'Número da Ata', max_length=255, null=True, blank=True)
    vigencia_ata = models.DateField(u'Vigência da Ata', null=True, blank=True)
    orgao_gerenciador_ata = models.CharField(u'Órgão Gerenciador da Ata', max_length=255, null=True, blank=True)
    origem = models.CharField(u'Origem', max_length=100, choices=ORIGEM_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name = u'Pesquisa Mercadológica'
        verbose_name_plural = u'Pesquisas Mercadológicas'

    def __unicode__(self):
        return u'Pesquisa Mercadológica: %s, Fornecedor: %s' % (self.id, self.razao_social)

    def get_itens(self):
        return ItemPesquisaMercadologica.objects.filter(pesquisa=self).order_by('item__item')

    def get_total(self):
        total=0
        for item in ItemPesquisaMercadologica.objects.filter(pesquisa=self).order_by('item__item'):
            total += item.valor_maximo * item.item.quantidade
        return total

    def tem_todos_itens(self):
        return ItemPesquisaMercadologica.objects.filter(pesquisa=self).count() == ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao).count()

class ItemPesquisaMercadologica(models.Model):
    pesquisa = models.ForeignKey(PesquisaMercadologica, verbose_name=u'Pesquisa')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    marca = models.CharField(u'Marca', max_length=255, null=True, blank=True)
    valor_maximo = models.DecimalField(u'Valor Máximo', max_digits=20, decimal_places=2, null=True, blank=True)
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
            elemento = self.item
            if elemento.solicitacao.pode_gerar_ordem():
                elemento.valor_medio = elemento.get_melhor_proposta()
            else:
                elemento.valor_medio = soma['valor_maximo__sum']/total_registros
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
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    ordem = models.IntegerField(u'Classificação')
    situacao = models.CharField(u'Situação', max_length=100, choices=RESULTADO_CHOICES)
    observacoes = models.CharField(u'Observação', max_length=5000, null=True, blank=True)
    empate = models.BooleanField(u'Empate', default=False)

    class Meta:
        verbose_name = u'Resultado da Licitação'
        verbose_name_plural = u'Resultados da Licitação'

    def __unicode__(self):
        return u'Resultado do Item: %s, Participante: %s' % (self.item, self.participante)

    def pode_alterar(self):
        return self.situacao == ResultadoItemPregao.CLASSIFICADO

    def get_valor(self):
        if self.item.solicitacao.get_pregao().eh_maior_desconto():
            return u'%s %%' % self.valor
        else:
            return 'R$ %s' % format_money(self.valor)

    def ganhador_atual(self):
        if ResultadoItemPregao.objects.filter(item=self.item, situacao=ResultadoItemPregao.CLASSIFICADO).exists():
            return ResultadoItemPregao.objects.filter(item=self.item, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0].participante
        return None


class AnexoPregao(models.Model):
    pregao = models.ForeignKey('base.Pregao')
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
        return '%s - %s' % (self.nome, self.data)


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
    estado = models.ForeignKey(Estado, verbose_name=u'Estado', null=True)
    telefone = models.CharField(u'Telefone', max_length=500)
    email =models.CharField(u'Email', max_length=500)
    interesse = models.CharField(u'Interesse', max_length=100, choices=INTERESSE_CHOICES)
    arquivo = models.ForeignKey(AnexoPregao)
    baixado_em = models.DateTimeField(u'Baixado em', auto_now_add=True, null=True)

    class Meta:
        verbose_name = u'Log de Download de Arquivo'
        verbose_name_plural = u'Logs de Download de Arquivo'

    def __unicode__(self):
        return u'Download por %s do Arquivo: %s' % (self.nome, self.arquivo)

    def save(self):
        self.estado = self.municipio.estado

        super(LogDownloadArquivo, self).save()


class HistoricoPregao(models.Model):
    pregao = models.ForeignKey(Pregao)
    data = models.DateTimeField(u'Data')
    obs = models.CharField(u'Observação', max_length=10000, null=True, blank=True)

    class Meta:
        verbose_name = u'Histórico do Pregão'
        verbose_name_plural = u'Históricos do Pregão'
        ordering = ['data']


    def __unicode__(self):
        return u'Histórico do Pregão: %s' % self.pregao


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

    def __unicode__(self):
        return u'Movimento %s da Solicitação: %s' % (self.id, self.solicitacao)

def upload_path_documento(instance, filename):
    return os.path.join('upload/documentos_solicitacao/%s/' % instance.solicitacao.id, filename)

class DocumentoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    nome = models.CharField(u'Nome do Arquivo', max_length=500)
    cadastrado_em = models.DateTimeField(u'Cadastrado Em', null=True, blank=True)
    cadastrado_por = models.ForeignKey(User, related_name=u'documento_cadastrado_por', null=True)
    documento = models.FileField(u'Documento', null=True, blank=True, upload_to=upload_path_documento)

    class Meta:
        verbose_name = u'Documento da Solicitação'
        verbose_name_plural = u'Documentos da Solicitação'

    def __unicode__(self):
        return u'Documento da Solicitação: %s' % self.solicitacao



class ItemQuantidadeSecretaria(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    secretaria = models.ForeignKey(Secretaria)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    aprovado = models.BooleanField(u'Aprovado', default=False)
    justificativa_reprovacao = models.CharField(u'Motivo da Negação do Pedido', null=True, blank=True, max_length=1000)
    avaliado_em = models.DateTimeField(u'Avaliado Em', null=True, blank=True)
    avaliado_por = models.ForeignKey(User, related_name=u'pedido_avaliado_por', null=True)

    def get_total(self):
        valor = self.item.valor_medio or 0
        return self.quantidade * valor

    class Meta:
        verbose_name = u'Pedido de Itens da Secretaria'
        verbose_name_plural = u'Pedidos de Itens da Secretaria'

    def __unicode__(self):
        return u'Item %s da Secretaria: %s' % (self.item, self.secretaria)


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
    cpf_ordenador_despesa = models.CharField(u'CPF do Ordenador de Despesa', max_length=200, null=True)
    cnpj = models.CharField(u'CNPJ', max_length=200, null=True)
    url = models.CharField(u'URL de Acesso', max_length=500, null=True)

    def __unicode__(self):
        return u'Configuração Geral'

    class Meta:
        verbose_name = u'Variável de Configuração'
        verbose_name_plural = u'Variáveis de Configuração'

class DotacaoOrcamentaria(models.Model):


    class Meta:
        verbose_name = u'Dotação Orçamentária'
        verbose_name_plural = u'Dotações Orçamentárias'

    def __unicode__(self):
        return 'Dotação: Programa %s - Elemento de Despesa: %s' % (self.programa_num, self.elemento_despesa_num)

class OrdemCompra(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    numero = models.CharField(u'Número da Ordem', max_length=200)
    data = models.DateField(u'Data')
    tipo = models.CharField(u'Tipo da Ordem', max_length=100, choices=((u'Compras', u'Compras'),(u'Serviços', u'Serviços'),), default=u'Compras')
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


    @transaction.atomic
    def delete(self, *args, **kwargs):
        solicitacao = self.solicitacao
        PedidoAtaRegistroPreco.objects.filter(solicitacao=solicitacao).delete()
        PedidoContrato.objects.filter(solicitacao=solicitacao).delete()
        ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao).delete()
        super(OrdemCompra, self).delete(*args, **kwargs)
        solicitacao.delete()

    def get_valor_global(self):
        valor = Decimal(0.00)
        pedidos = None
        if PedidoAtaRegistroPreco.objects.filter(solicitacao=self.solicitacao).exists():
            pedidos = PedidoAtaRegistroPreco.objects.filter(solicitacao=self.solicitacao).order_by('item')

        elif PedidoContrato.objects.filter(solicitacao=self.solicitacao).exists():
            pedidos = PedidoContrato.objects.filter(solicitacao=self.solicitacao).order_by('item')

        elif PedidoCredenciamento.objects.filter(solicitacao=self.solicitacao).exists():
            pedidos = PedidoCredenciamento.objects.filter(solicitacao=self.solicitacao).order_by('item')
        if pedidos:
            for pedido in pedidos:
                valor = valor + (pedido.item.valor*pedido.quantidade)
        else:
            dicionario = {}
            for pesquisa in PesquisaMercadologica.objects.filter(solicitacao=self.solicitacao):
                total = ItemPesquisaMercadologica.objects.filter(pesquisa=pesquisa, ativo=True).aggregate(soma=Sum('valor_maximo'))['soma']
                if total:

                    dicionario[pesquisa.id] = total
            resultado = sorted(dicionario.items(), key=lambda x: x[1])
            itens = ItemPesquisaMercadologica.objects.filter(pesquisa=resultado[0][0]).order_by('item')
            valor = 0
            for item in itens:
                valor += item.get_total()
        return valor




class AtaRegistroPreco(models.Model):
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=20, null=True)
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
    fornecedor_adesao_arp = models.ForeignKey('base.Fornecedor', null=True, related_name=u'fornecedor_contrato_adesao', verbose_name=u'Fornecedor')

    class Meta:
        verbose_name = u'Ata de Registro de Preço'
        verbose_name_plural = u'Atas de Registro de Preço'

    def __unicode__(self):
        if self.adesao:
            return 'Adesão à ARP N° %s' % (self.numero)
        else:
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

    def get_arquivos_publicos(self):
        return AnexoAtaRegistroPreco.objects.filter(ata=self, publico=True)

    def get_contrato(self):
        if Contrato.objects.filter(solicitacao=self.solicitacao).exists():
            return Contrato.objects.filter(solicitacao=self.solicitacao)[0]
        return False

    def get_fornecedores(self):
        itens = ItemAtaRegistroPreco.objects.filter(ata=self)
        return Fornecedor.objects.filter(Q(id__in=itens.values_list('fornecedor', flat=True)) | Q(id__in=itens.values_list('participante__fornecedor', flat=True)))

    def get_valor_total(self, ganhador=None):
        itens = ItemAtaRegistroPreco.objects.filter(ata=self)
        if ganhador:
            itens = itens.filter(fornecedor=ganhador)
        total = 0
        for item in itens:
            total = total + (item.quantidade * item.valor)
        return total

    def get_itens(self):
        return ItemAtaRegistroPreco.objects.filter(ata=self)

    def get_ordem(self):
        if ItemAtaRegistroPreco.objects.filter(ata=self).exists():
            return ItemAtaRegistroPreco.objects.filter(ata=self).order_by('-ordem')[0].ordem + 1
        else:
            return 1

class Credenciamento(models.Model):
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=20, null=True)
    data_inicio = models.DateField(verbose_name=u'Data de Início', null=True)
    data_fim = models.DateField(verbose_name=u'Data de Vencimento', null=True)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, null=True)
    pregao = models.ForeignKey(Pregao, null=True)
    secretaria = models.ForeignKey(Secretaria, null=True)
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


    class Meta:
        verbose_name = u'Credenciamento'
        verbose_name_plural = u'Credenciamentos'

    def __unicode__(self):
        return u'Credenciamento: %s' % (self.numero)

    def get_situacao(self):
        if self.concluido:
            return u'Concluído'
        elif self.suspenso:
            return u'Suspenso'
        elif self.cancelado:
            return u'Cancelado'
        else:
            return u'Ativo'

    def get_ordem(self):
        if ItemCredenciamento.objects.filter(credenciamento=self).exists():
            return ItemCredenciamento.objects.filter(credenciamento=self).order_by('-ordem')[0].ordem + 1
        else:
            return 1

    def get_fornecedores(self):
        participantes = ParticipantePregao.objects.filter(desclassificado=False, excluido_dos_itens=False, pregao=self.pregao)
        return participantes

    def get_valor_total(self, ganhador=None):
        itens = ItemCredenciamento.objects.filter(ata=self)
        if ganhador:
            itens = itens.filter(fornecedor=ganhador)
        total = 0
        for item in itens:
            total = total + (item.quantidade * item.valor)
        return total


class ItemCredenciamento(models.Model):
    credenciamento = models.ForeignKey(Credenciamento)
    item = models.ForeignKey(ItemSolicitacaoLicitacao, null=True)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    material = models.ForeignKey('base.MaterialConsumo', null=True)
    unidade = models.ForeignKey(TipoUnidade, verbose_name=u'Unidade', null=True)
    ordem = models.IntegerField(u'Ordem', null=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = u'Item do Credenciamento'
        verbose_name_plural = u'Itens do Credenciamento'


    def __unicode__(self):
        return u'Item %s do Credenciamento: %s' % (self.item, self.credenciamento)

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoCredenciamento.objects.filter(item=self, ativo=True)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        else:


            if ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                total = ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria)[0].quantidade
            pedidos = PedidoCredenciamento.objects.filter(item=self, ativo=True, setor__secretaria=usuario.pessoafisica.setor.secretaria)
            if pedidos.exists():
                return total - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            return total

        return 0

    def get_saldo_atual_secretaria(self, secretaria):
        pedidos = PedidoCredenciamento.objects.filter(item=self, ativo=True, setor__secretaria=secretaria)
        if pedidos.exists():
            return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
        else:
            return self.quantidade

    def get_valor_total_disponivel(self):
        return self.get_quantidade_disponivel() * Decimal(self.valor)

    def get_valor_total(self):
        return self.valor * self.quantidade

    def get_quantidade_consumida(self):
        if PedidoCredenciamento.objects.filter(item=self).exists():
            return PedidoCredenciamento.objects.filter(item=self).aggregate(total=Sum('quantidade'))['total']
        else:
            return 0

    def get_valor_total_consumido(self):
        return self.get_quantidade_consumida() * Decimal(self.valor)

class PedidoCredenciamento(models.Model):
    credenciamento = models.ForeignKey(Credenciamento)
    item = models.ForeignKey(ItemCredenciamento)
    fornecedor = models.ForeignKey(Fornecedor, null=True)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2, null=True, blank=True)
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)


    class Meta:
        verbose_name = u'Pedido do Credenciamento'
        verbose_name_plural = u'Pedidos do Credenciamento'

    def __unicode__(self):
        return u'Pedido %s do Credenciamento: %s' % (self.id, self.credenciamento)


    def get_total(self):
        return self.quantidade * self.valor

    def get_saldo_atual(self):
        return self.item.get_saldo_atual_secretaria(self.setor.secretaria)


class AnexoCredenciamento(models.Model):
    credenciamento = models.ForeignKey('base.Credenciamento')
    nome = models.CharField(u'Nome', max_length=500)
    data = models.DateField(u'Data')
    arquivo = models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/')
    cadastrado_por = models.ForeignKey(User)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')
    publico = models.BooleanField(u'Documento Público', help_text=u'Se sim, este documento será exibido publicamente', default=False)

    class Meta:
        verbose_name = u'Anexo do Credenciamento'
        verbose_name_plural = u'Anexos do Credenciamento'

    def __unicode__(self):
        return '%s - %s' % (self.nome, self.credenciamento)

class Contrato(models.Model):


    NAO_SE_APLICA = u''
    INCISO_I = u'I'
    INCISO_II = u'II'
    INCISO_IV = u'IV'
    INCISO_V = u'V'

    TEXTO_INCISO_I = u'I - aos projetos cujos produtos estejam contemplados nas metas estabelecidas no Plano Plurianual, os quais poderão ser prorrogados se houver interesse da Administração e desde que isso tenha sido previsto no ato convocatório;'
    TEXTO_INCISO_II = u'II - à prestação de serviços a serem executados de forma contínua, que poderão ter a sua duração prorrogada por iguais e sucessivos períodos com vistas à obtenção de preços e condições mais vantajosas para a administração, limitada a sessenta meses; (Redação dada pela Lei nº 9.648, de 1998)'
    TEXTO_INCISO_IV = u'IV - ao aluguel de equipamentos e à utilização de programas de informática, podendo a duração estender-se pelo prazo de até 48 (quarenta e oito) meses após o início da vigência do contrato.'
    TEXTO_INCISO_V = u'V - às hipóteses previstas nos incisos IX, XIX, XXVIII e XXXI do art. 24, cujos contratos poderão ter vigência por até 120 (cento e vinte) meses, caso haja interesse da administração. (Incluído pela Lei nº 12.349, de 2010)'
    INCISOS_ARTIGO_57_CHOICES = (
        (NAO_SE_APLICA , u'---------------'),
        (INCISO_I, TEXTO_INCISO_I),
        (INCISO_II, TEXTO_INCISO_II),
        (INCISO_IV, TEXTO_INCISO_IV),
        (INCISO_V, TEXTO_INCISO_V),
    )
    numero = models.CharField(max_length=100, help_text=u'No formato: 99999/9999', verbose_name=u'Número', unique=False)
    valor = models.DecimalField(decimal_places=2,max_digits=20)
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
    aplicacao_artigo_57 = models.CharField(u'Aplicação do Art. 57 da Lei 8666/93(Art. 57. - A duração dos contratos regidos por esta Lei ficará adstrita à vigência dos respectivos créditos orçamentários, exceto quanto aos relativos:)', max_length=200, null=True, blank=True, choices=INCISOS_ARTIGO_57_CHOICES, default=NAO_SE_APLICA)
    garantia_execucao_objeto = models.CharField(u'Garantia de Execução do Objeto (%)', null=True, blank=True, max_length=50, help_text=u'Limitado a 5%. Deixar em branco caso não se aplique.')


    class Meta:
        verbose_name = u'Contrato'
        verbose_name_plural = u'Contratos'

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

    def eh_ativo(self):
        return not self.cancelado

    def get_carater_continuado(self):
        if self.continuado:
            return u'Sim'
        return u'Não'

    def get_valor_aditivado(self):
        total = self.valor
        for aditivo in self.aditivos_set.filter(tipo=Aditivo.REAJUSTE_FINANCEIRO):
            if aditivo.de_valor and aditivo.valor: # evita NoneType em aditivo.valor
                total += aditivo.valor
        return total

    def get_aditivo_permitido_valor(self):
        total_valor = 0
        for aditivo in self.aditivos_set.filter(tipo=Aditivo.REAJUSTE_FINANCEIRO):
            total_valor += aditivo.valor


        if self.pregao and self.pregao.objeto_tipo == Pregao.SERVICOS_REFORMA_E_EQUIPAMENTO:
            return (50-total_valor)
        else:
            return (25-total_valor)

    def get_ordem(self):
        if ItemContrato.objects.filter(contrato=self).exists():
            return ItemContrato.objects.filter(contrato=self).order_by('-ordem')[0].ordem + 1
        else:
            return 1

    def get_data_fim(self):
        if not Aditivo.objects.filter(contrato=self, de_prazo=True).exists():
            return self.data_fim
        else:
            return Aditivo.objects.filter(contrato=self, de_prazo=True).order_by('-ordem')[0].data_fim

    def get_proximo_aditivo(self):
        if not Aditivo.objects.filter(contrato=self).exists():
            return 1
        return Aditivo.objects.filter(contrato=self).order_by('-ordem')[0].ordem + 1

    def eh_registro_preco(self):
        return self.pregao.eh_ata_registro_preco

    def get_arquivos_publicos(self):
        return AnexoContrato.objects.filter(contrato=self, publico=True)

    def get_fornecedor(self):
        if ItemContrato.objects.filter(contrato=self).exists() and ItemContrato.objects.filter(contrato=self)[0].participante:
            return ItemContrato.objects.filter(contrato=self)[0].participante
        return ItemContrato.objects.filter(contrato=self)[0].fornecedor


    def get_lotes(self):
        if ItemContrato.objects.filter(contrato=self).exists():
            fornecedor = ItemContrato.objects.filter(contrato=self)[0].fornecedor
            ids = list()
            for lote in ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, eh_lote=True):
                vencedor = lote.get_vencedor()
                if vencedor and vencedor.participante.fornecedor == fornecedor:
                    ids.append(lote.id)

            return ItemSolicitacaoLicitacao.objects.filter(id__in=ids)
        return None


    def get_ordem(self):
        if Aditivo.objects.filter(contrato=self).exists():
            return Aditivo.objects.filter(contrato=self).order_by('-ordem')[0].ordem + 1
        else:
            return 1

    def get_itens(self):
        return self.itemcontrato_set.all().order_by('item__item')

    def eh_gerente(self, user):
        return user.groups.filter(name='Gerente') and self.solicitacao.recebida_setor(user.pessoafisica.setor)

class Aditivo(models.Model):

    ACRESCIMO_QUANTITATIVOS = u'Acréscimo de Quantitativos'
    ACRESCIMO_VALOR = u'Acréscimo de Valor'
    REAJUSTE_FINANCEIRO = u'Reajuste Econômico-financeiro'
    SUPRESSAO_QUANTITATIVO = u'Supressão de Quantitativo'
    SUPRESSAO_VALOR = u'Supressão de Valor'
    TIPO_CHOICES = (
        (u'', '-----------------'),
        (ACRESCIMO_QUANTITATIVOS, ACRESCIMO_QUANTITATIVOS),
        (ACRESCIMO_VALOR, ACRESCIMO_VALOR),
        (REAJUSTE_FINANCEIRO, REAJUSTE_FINANCEIRO),
        (SUPRESSAO_QUANTITATIVO,SUPRESSAO_QUANTITATIVO),
        (SUPRESSAO_VALOR, SUPRESSAO_VALOR),
    )
    contrato = models.ForeignKey(Contrato, related_name='aditivos_set' , on_delete=models.CASCADE)
    ordem = models.PositiveSmallIntegerField(default=0)
    valor = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    data_inicio = models.DateField(verbose_name=u'Data de Início', null=True, blank=True)
    data_fim = models.DateField(verbose_name=u'Data de Vencimento', null=True, blank=True)
    de_prazo = models.BooleanField(verbose_name=u'Aditivo de Prazo', default=False)
    de_valor = models.BooleanField(verbose_name=u'Aditivo de Valor', default=False)
    tipo = models.CharField(u'Tipo de Aditivo', null=True, blank=True, choices=TIPO_CHOICES, max_length=50)
    indice = models.DecimalField(u'Índice de Reajuste', decimal_places=2, max_digits=10, null=True, blank=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = u'Aditivo de Contrato'
        verbose_name_plural = u'Aditivos de Contrato'

    def __unicode__(self):
        tipo = u''
        if self.de_prazo:
            tipo += u'de Prazo, '

        if self.tipo in [Aditivo.ACRESCIMO_QUANTITATIVOS, Aditivo.SUPRESSAO_QUANTITATIVO]:
            tipo += u'de Quantidade, '

        if self.tipo in [Aditivo.ACRESCIMO_VALOR, Aditivo.SUPRESSAO_VALOR, Aditivo.REAJUSTE_FINANCEIRO]:
            tipo += u'de Valor, '


        if len(tipo)==0:
            tipo = u'Indefinido'
        return u'%sº Aditivo (%s)' % (self.ordem, tipo[:-2])


class AditivoItemContrato(models.Model):
    item = models.ForeignKey('base.ItemContrato', on_delete=models.CASCADE)
    valor = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    tipo = models.CharField(u'Tipo de Aditivo', null=True, blank=True, choices=Aditivo.TIPO_CHOICES, max_length=50)
    indice = models.DecimalField(u'Índice de Reajuste', decimal_places=2, max_digits=10, null=True, blank=True)

    class Meta:
        verbose_name = u'Aditivo de Item de Contrato'
        verbose_name_plural = u'Aditivos de Itens de Contrato'

    def __unicode__(self):
        tipo = u''
        if self.de_prazo:
            tipo += u'de Prazo, '

        if self.de_valor:
            tipo += u'de Valor, '


        if len(tipo)==0:
            tipo = u'Indefinido'
        return u'Aditivo do Item: (%s)' % (self.item)

class ItemContrato(models.Model):
    contrato = models.ForeignKey(Contrato)
    item = models.ForeignKey(ItemSolicitacaoLicitacao, null=True)
    participante = models.ForeignKey(ParticipantePregao, null=True)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    fornecedor = models.ForeignKey(Fornecedor, null=True)
    material = models.ForeignKey('base.MaterialConsumo', null=True)
    unidade = models.ForeignKey(TipoUnidade, verbose_name=u'Unidade', null=True)
    inserido_outro_contrato = models.BooleanField(u'Inserido em Outro Contrato', default=False)
    ordem = models.IntegerField(u'Ordem', null=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = u'Item do Contrato'
        verbose_name_plural = u'Itens do Contrato'

    def __unicode__(self):
        return u'Item %s do Contrato: %s' % (self.item, self.contrato)

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        quantidade_aditivo = 0


        aditivos = AditivoItemContrato.objects.filter(item=self)
        if aditivos.exists():
            for aditivo in aditivos:
                if aditivo.tipo == Aditivo.ACRESCIMO_QUANTITATIVOS:
                    if aditivo.valor:
                        quantidade_aditivo += aditivo.valor
                elif aditivo.tipo == Aditivo.SUPRESSAO_QUANTITATIVO:
                    if aditivo.valor:
                        quantidade_aditivo -= aditivo.valor
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoContrato.objects.filter(item=self, ativo=True).exclude(item__contrato__aplicacao_artigo_57=Contrato.INCISO_II)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma'] + quantidade_aditivo
            else:
                return self.quantidade + quantidade_aditivo

        else:
            total = self.quantidade
            origem = False
            if (usuario.pessoafisica.setor.secretaria == self.contrato.solicitacao.setor_origem.secretaria) and ItemQuantidadeSecretaria.objects.filter(item=self.item, item__solicitacao=self.contrato.solicitacao, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                total = ItemQuantidadeSecretaria.objects.filter(item=self.item, item__solicitacao=self.contrato.solicitacao, secretaria=self.contrato.solicitacao.setor_origem.secretaria)[0].quantidade
                origem = True
            if not (usuario.pessoafisica.setor.secretaria == self.contrato.solicitacao.setor_origem.secretaria) and ItemQuantidadeSecretaria.objects.filter(item=self.item, item__solicitacao=self.contrato.solicitacao, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                total = ItemQuantidadeSecretaria.objects.filter(item=self.item, item__solicitacao=self.contrato.solicitacao, secretaria=usuario.pessoafisica.setor.secretaria)[0].quantidade

            pedidos = PedidoContrato.objects.filter(item=self, ativo=True, setor__secretaria=usuario.pessoafisica.setor.secretaria).exclude(item__contrato__aplicacao_artigo_57=Contrato.INCISO_II)

            if origem:
                if pedidos.exists():
                    return total - pedidos.aggregate(soma=Sum('quantidade'))['soma'] + quantidade_aditivo
                return total + quantidade_aditivo
            else:
                if pedidos.exists():
                    return total - pedidos.aggregate(soma=Sum('quantidade'))['soma']
                return total

        return 0

    def get_valor_total(self):
        return self.quantidade * Decimal(self.get_valor_item_contrato())

    def get_valor_total_disponivel(self):
        return self.get_quantidade_disponivel() * Decimal(self.get_valor_item_contrato())

    def get_quantidade_consumida(self):
        if PedidoContrato.objects.filter(item=self).exists():
            return PedidoContrato.objects.filter(item=self).aggregate(total=Sum('quantidade'))['total']
        else:
            return 0

    def get_valor_total_consumido(self):
        return self.get_quantidade_consumida() * Decimal(self.get_valor_item_contrato())

    def get_aditivo_permitido_valor_soma(self):
        total_valor = 0
        for item in AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.ACRESCIMO_VALOR):
            total_valor += item.indice

        if self.contrato.pregao and self.contrato.pregao.objeto_tipo == Pregao.SERVICOS_REFORMA_E_EQUIPAMENTO:
            if total_valor > 50:
                return 0
            return str(50-total_valor).replace(',', '.')
        else:
            if total_valor > 25:
                return 0
            return str(25-total_valor).replace(',', '.')


    def get_aditivo_permitido_valor_subtrai(self):
        total_valor = 0

        for item in AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.SUPRESSAO_VALOR):
            total_valor += item.indice
        if self.contrato.pregao and self.contrato.pregao.objeto_tipo == Pregao.SERVICOS_REFORMA_E_EQUIPAMENTO:
            if total_valor > 50:
                return 0
            return str(50-total_valor).replace(',', '.')
        else:
            if total_valor > 25:
                return 0
            return str(25-total_valor).replace(',', '.')

    def get_aditivo_permitido_quantitativo_soma(self):
        total_quantitativo = 0
        for item in AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.ACRESCIMO_QUANTITATIVOS):
            total_quantitativo += item.indice

        if self.contrato.pregao and self.contrato.pregao.objeto_tipo == Pregao.SERVICOS_REFORMA_E_EQUIPAMENTO:
            return str((self.quantidade*(50-total_quantitativo))/100).replace(',', '.')
        else:
            return str((self.quantidade*(25-total_quantitativo))/100).replace(',', '.')

    def get_aditivo_permitido_quantitativo_subtrai(self):
        total_quantitativo = 0
        for item in AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.SUPRESSAO_QUANTITATIVO):
            total_quantitativo += item.indice
        if self.contrato.pregao and self.contrato.pregao.objeto_tipo == Pregao.SERVICOS_REFORMA_E_EQUIPAMENTO:
            return str((self.quantidade*(50-total_quantitativo))/100).replace(',', '.')
        else:
            return str((self.quantidade*(25-total_quantitativo))/100).replace(',', '.')

    def get_valor_item_contrato(self):

        total = self.valor
        if AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.ACRESCIMO_VALOR, valor__isnull=False).exists():
            total += AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.ACRESCIMO_VALOR).aggregate(total=Sum('valor'))['total']

        if AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.SUPRESSAO_VALOR, valor__isnull=False).exists():
            total -= AditivoItemContrato.objects.filter(item=self, tipo=Aditivo.SUPRESSAO_VALOR).aggregate(total=Sum('valor'))['total']
        return str(total).replace(',', '.')


class PedidoContrato(models.Model):
    contrato = models.ForeignKey(Contrato)
    item = models.ForeignKey(ItemContrato)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2, null=True, blank=True)
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Pedido do Contrato'
        verbose_name_plural = u'Pedidos do Contrato'

    def __unicode__(self):
        return u'Pedido %s do Contrato: %s' % (self.id, self.contrato)

    def get_total(self):
        return self.quantidade * self.valor




class ItemAtaRegistroPreco(models.Model):
    ata = models.ForeignKey(AtaRegistroPreco)
    item = models.ForeignKey(ItemSolicitacaoLicitacao, null=True)
    participante = models.ForeignKey(ParticipantePregao, null=True)
    fornecedor = models.ForeignKey(Fornecedor, null=True)
    marca = models.CharField(u'Marca', max_length=200, null=True)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    material = models.ForeignKey('base.MaterialConsumo', null=True)
    unidade = models.ForeignKey(TipoUnidade, verbose_name=u'Unidade', null=True)
    ordem = models.IntegerField(u'Ordem', null=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = u'Item da ARP'
        verbose_name_plural = u'Itens da ARP'


    def __unicode__(self):
        return u'Item %s da ARP: %s' % (self.item, self.ata)

    def get_quantidade_disponivel(self):
        usuario = tl.get_user()
        if usuario.groups.filter(name=u'Gerente').exists():
            pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True)
            if pedidos.exists():
                return self.quantidade - pedidos.aggregate(soma=Sum('quantidade'))['soma']
            else:
                return self.quantidade

        else:
            valor_pedidos = 0
            perdeu_item = 0
            ganhou_item = 0
            total = 0
            if self.ata.adesao:
                total = self.quantidade
            if ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria).exists():
                total = ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=usuario.pessoafisica.setor.secretaria)[0].quantidade

            if total:
                pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True, setor__secretaria=usuario.pessoafisica.setor.secretaria)
                if pedidos.exists():
                    valor_pedidos = pedidos.aggregate(soma=Sum('quantidade'))['soma']

                transferencias = TransferenciaItemARP.objects.filter(item=self)
                if transferencias.exists():
                    if transferencias.filter(secretaria_origem=usuario.pessoafisica.setor.secretaria).exists():
                        perdeu_item = transferencias.filter(secretaria_origem=usuario.pessoafisica.setor.secretaria).aggregate(soma=Sum('quantidade'))['soma']

                    if transferencias.filter(secretaria_destino=usuario.pessoafisica.setor.secretaria).exists():
                        ganhou_item = transferencias.filter(secretaria_destino=usuario.pessoafisica.setor.secretaria).aggregate(soma=Sum('quantidade'))['soma']

            return total - valor_pedidos + ganhou_item - perdeu_item

        return 0

    def get_saldo_atual_secretaria(self, secretaria):

        valor_pedidos = 0
        perdeu_item = 0
        ganhou_item = 0
        total = 0
        if not self.ata.adesao:
            if ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=secretaria).exists():
                total = ItemQuantidadeSecretaria.objects.filter(item=self.item, secretaria=secretaria)[0].quantidade

        if total:
            pedidos = PedidoAtaRegistroPreco.objects.filter(item=self, ativo=True, setor__secretaria=secretaria)
            if pedidos.exists():
                valor_pedidos = pedidos.aggregate(soma=Sum('quantidade'))['soma']

            transferencias = TransferenciaItemARP.objects.filter(item=self)
            if transferencias.exists():
                if transferencias.filter(secretaria_origem=secretaria).exists():
                    perdeu_item = transferencias.filter(secretaria_origem=secretaria).aggregate(soma=Sum('quantidade'))['soma']

                if transferencias.filter(secretaria_destino=secretaria).exists():
                    ganhou_item = transferencias.filter(secretaria_destino=secretaria).aggregate(soma=Sum('quantidade'))['soma']
        return total - valor_pedidos + ganhou_item - perdeu_item


    def get_total(self):
        return self.quantidade * self.valor

    def get_valor_total_disponivel(self):
        return self.get_quantidade_disponivel() * Decimal(self.valor)

    def get_quantidade_consumida(self):
        if PedidoAtaRegistroPreco.objects.filter(item=self).exists():
            return PedidoAtaRegistroPreco.objects.filter(item=self).aggregate(total=Sum('quantidade'))['total']
        else:
            return 0

    def get_valor_total_consumido(self):
        return self.get_quantidade_consumida() * Decimal(self.valor)


    def tem_varias_secretarias(self):
        if self.item:
            return ItemQuantidadeSecretaria.objects.filter(item=self.item).count() > 1
        return False

    def get_secretarias(self):
        return Secretaria.objects.filter(id__in=ItemQuantidadeSecretaria.objects.filter(item=self.item).values_list('secretaria', flat=True))

class PedidoAtaRegistroPreco(models.Model):
    ata = models.ForeignKey(AtaRegistroPreco)
    item = models.ForeignKey(ItemAtaRegistroPreco)
    solicitacao = models.ForeignKey(SolicitacaoLicitacao)
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    valor = models.DecimalField(u'Valor', max_digits=20, decimal_places=2, null=True, blank=True)
    setor = models.ForeignKey(Setor)
    pedido_por = models.ForeignKey(User)
    pedido_em = models.DateTimeField(u'Pedido em')
    ativo = models.BooleanField(u'Ativo', default=True)


    class Meta:
        verbose_name = u'Pedido da ARP'
        verbose_name_plural = u'Pedidos da ARP'

    def __unicode__(self):
        return u'Pedido %s da ARP: %s' % (self.id, self.ata)


    def get_total(self):
        return self.quantidade * self.valor

    def get_saldo_atual(self):
        return self.item.get_saldo_atual_secretaria(self.setor.secretaria)


class FornecedorCRC(models.Model):

    PORTE_EMPRESA_CHOICES = (
        (u'MEI - Microempreendedor Individual', u'MEI - Microempreendedor Individual'),
        (u'Pequena empresa', u'Pequena empresa'),
        (u'Média empresa', u'Média empresa'),
        (u'Média-grande empresa', u'Média-grande empresa'),
        (u'Grande empresa', u'Grande empresa'),
    )
    fornecedor = models.ForeignKey(Fornecedor, verbose_name=u'Fornecedor')
    porte_empresa = models.CharField(u'Porte da Empresa', max_length=100, choices=PORTE_EMPRESA_CHOICES)
    data_abertura = models.DateField(u'Data de Abertura da Empresa')
    inscricao_estadual = models.CharField(u'Inscrição Estadual', max_length=100, null=True, blank=True)
    inscricao_municipal = models.CharField(u'Inscrição Municipal', max_length=100, null=True, blank=True)
    natureza_juridica = models.CharField(u'Natureza Jurídica', max_length=500)
    ramo_negocio = models.CharField(u'Ramo do Negócio', max_length=500)
    cnae_primario_codigo = models.CharField(u'Código do CNAE Primário', max_length=30)
    cnae_primario_descricao = models.CharField(u'Descrição do CNAE Primário', max_length=500)
    objetivo_social = models.CharField(u'Objetivo Social', max_length=5000)
    capital_social = models.CharField(u'Capital Social (R$)', max_length=100, null=True, blank=True)
    data_ultima_integralizacao = models.DateField(u'Data da Última Integralização',  null=True, blank=True)
    banco = models.CharField(u'Banco', max_length=200, null=True, blank=True)
    agencia = models.CharField(u'Agência', max_length=50, null=True, blank=True)
    conta = models.CharField(u'Conta', max_length=200, null=True, blank=True)
    nome = models.CharField(u'Nome do Representante Legal', max_length=500)
    cpf = models.CharField(u'CPF', max_length=20)
    rg = models.CharField(u'Carteira de Identidade', max_length=20)
    rg_emissor = models.CharField(u'Órgão Expedidor ', max_length=20)
    data_expedicao = models.DateField(u'Data de Expedição')
    data_nascimento = models.DateField(u'Data de Nascimento')
    email = models.CharField(u'Email ', max_length=200)
    validade = models.DateField(u'Validade')
    numero = models.IntegerField(u'Número', null=True, blank=True)
    ano = models.IntegerField(u'Ano', null=True, blank=True)

    class Meta:
        verbose_name = u'Certificado de Registro Cadastral'
        verbose_name_plural = u'Certificados de Registros Cadastrais'

    def __unicode__(self):
        return u'%s - Validade: %s' % (self.fornecedor, self.validade)

    def get_proximo_numero(self, ano):
        if FornecedorCRC.objects.filter(ano=ano).exists():
            ultimo = FornecedorCRC.objects.filter(ano=ano).order_by('-numero')
            return ultimo[0].numero + 1

        else:
            return 1


class CnaeSecundario(models.Model):
    crc = models.ForeignKey(FornecedorCRC, verbose_name=u'CRC')
    codigo = models.CharField(u'Código', max_length=30)
    descricao = models.CharField(u'Descrição', max_length=500)

    class Meta:
        verbose_name = u'CNAE Secundário'
        verbose_name_plural = u'CNAES Secundários'

    def __unicode__(self):
        return u'%s - CNAE Secundário: %s' % (self.crc, self.codigo)

class SocioCRC(models.Model):
    crc = models.ForeignKey(FornecedorCRC, verbose_name=u'CRC')
    cpf = models.CharField(u'CPF', max_length=20)
    nome = models.CharField(u'Nome', max_length=500)
    rg = models.CharField(u'Carteira de Identidade', max_length=20)
    rg_emissor = models.CharField(u'Órgão Expedidor ', max_length=20)
    data_expedicao = models.DateField(u'Data de Expedição')
    data_nascimento = models.DateField(u'Data de Nascimento')
    email = models.CharField(u'Email ', max_length=200)

    class Meta:
        verbose_name = u'Sócio'
        verbose_name_plural = u'Sócios'

    def __unicode__(self):
        return u'%s - Sócio: %s' % (self.crc, self.nome)



class ModeloAta(models.Model):

    TIPO_ATA_CHOICES = (
        (u'Ata de Sessão Inicial', u'Ata de Sessão Inicial'),
        (u'Ata de Julgamento', u'Ata de Julgamento'),
        (u'Ata de Licitação Fracassada', u'Ata de Licitação Fracassada'),
        (u'Ata de Licitação Deserta', u'Ata de Licitação Deserta'),
        (u'Ata de Saneamento', u'Ata de Saneamento'),
    )
    nome = models.CharField(u'Nome da Ata', max_length=1000)
    tipo = models.CharField(u'Tipo da Ata', max_length=100, choices=TIPO_ATA_CHOICES)
    palavras_chaves = models.CharField(u'Palavras-Chave', max_length=4000, null=True, blank=True)
    cadastrado_em = models.DateTimeField(u'Cadastrado Em')
    cadastrado_por = models.ForeignKey(PessoaFisica)
    arquivo = models.FileField(u'Arquivo', null=True, blank=True, upload_to=u'upload/minutas/')

    class Meta:
        verbose_name = u'Modelo de Ata'
        verbose_name_plural = u'Modelos de Atas'

    def __unicode__(self):
        return self.nome


class TipoModelo(models.Model):
    nome = models.CharField(u'Nome', max_length=500)
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Tipo do Modelo'
        verbose_name_plural = u'Tipos do Modelo'

    def __unicode__(self):
        return self.nome


class TipoObjetoModelo(models.Model):
    nome = models.CharField(u'Nome', max_length=500)
    ativo = models.BooleanField(u'Ativo', default=True)

    class Meta:
        verbose_name = u'Tipo de Objeto do Modelo'
        verbose_name_plural = u'Tipos de Objetos do Modelo'

    def __unicode__(self):
        return self.nome


class ModeloDocumento(models.Model):

    TIPO_DOCUMENTO_CHOICES = (
        (u'Minuta de Edital', u'Minuta de Edital'),
        (u'Modelo de Edital', u'Modelo de Edital'),
        (u'Modelos de Termo de Referência', u'Modelos de Termo de Referência'),
        (u'Parecer Jurídico', u'Parecer Jurídico'),
        (u'Minuta de Contrato', u'Minuta de Contrato'),
        (u'Modelo de Rescisão', u'Modelo de Rescisão'),
    )

    TIPO_DOCUMENTO_OBJETO_CHOICES = (
        (u'Material de Consumo', u'Material de Consumo'),
        (u'Material Permanente', u'Material Permanente'),
        (u'Locação', u'Locação'),
        (u'Publicidade', u'Publicidade'),
        (u'Obras e Manutenção', u'Obras e Manutenção'),
        (u'Serviços e Engenharia', u'Serviços e Engenharia'),
        (u'Serviços - Outros', u'Serviços - Outros'),
    )
    nome = models.CharField(u'Nome do Documento', max_length=1000)
    tipo = models.ForeignKey(TipoModelo, null=True)
    tipo_objeto = models.ForeignKey(TipoObjetoModelo, null=True)
    palavras_chaves = models.CharField(u'Palavras-Chave', max_length=4000, null=True, blank=True)
    cadastrado_em = models.DateTimeField(u'Cadastrado Em')
    cadastrado_por = models.ForeignKey(PessoaFisica)
    arquivo = models.FileField(u'Arquivo', null=True, blank=True, upload_to=u'upload/modelos_documentos/')

    class Meta:
        verbose_name = u'Modelo de Documento'
        verbose_name_plural = u'Modelos de Documentos'

    def __unicode__(self):
        return self.nome

class TransferenciaItemARP(models.Model):
    secretaria_origem = models.ForeignKey(Secretaria, verbose_name=u'Secretaria de Origem', related_name='sec_origem')
    secretaria_destino = models.ForeignKey(Secretaria, verbose_name=u'Secretaria de Destino', related_name='sec_destino')
    item = models.ForeignKey(ItemAtaRegistroPreco, verbose_name=u'Item da ARP')
    quantidade = models.DecimalField(u'Quantidade', max_digits=20, decimal_places=2)
    justificativa = models.CharField(u'Justificativa', max_length=5000)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')
    cadastrado_por = models.ForeignKey(PessoaFisica)

    class Meta:
        verbose_name = u'Transferência de Item de ARP'
        verbose_name_plural = u'Transferências de Itens de ARP'

    def __unicode__(self):
        return self.quantidade


