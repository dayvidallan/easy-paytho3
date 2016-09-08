# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
from newadmin.utils import CepModelField
from decimal import Decimal
from django.db.models import Sum
import datetime
from ckeditor.fields import RichTextField
TWOPLACES = Decimal(10) ** -2

class User(AbstractUser):

    class Meta:
        db_table = 'auth_user'

        permissions = (
            ('pode_cadastrar_solicitacao', u'Pode Cadastrar Solicitação'),
            ('pode_cadastrar_pregao', u'Pode Cadastrar Pregão'),
            ('pode_cadastrar_pesquisa_mercadologica', u'Pode Cadastrar Pesquisa Mercadológica'),
            ('pode_ver_minuta', u'Pode Ver Minuta'),
            ('pode_avaliar_minuta', u'Pode Avaliar Minuta'),
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
    nome = models.CharField(u'Nome', max_length=80)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Critério de Julgamento do Pregão'
        verbose_name_plural = u'Critérios de Julgamento de Pregão'

class TipoPregao(models.Model):
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
        verbose_name = u'Tipo de Unidade'
        verbose_name_plural = u'Tipos de Unidade'

class DotacaoOrcamentaria(models.Model):
    nome = models.CharField(u'Nome', max_length=100)

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Dotação Orçamentária'
        verbose_name_plural = u'Dotações Orçamentárias'


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
    num_memorando = models.CharField(u'Número do Memorando', max_length=80)
    objeto = models.CharField(u'Descrição do Objeto', max_length=1500)
    objetivo = models.CharField(u'Objetivo', max_length=1500)
    justificativa = models.CharField(u'Justificativa', max_length=1500)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
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

    def __unicode__(self):
        return self.num_memorando

    class Meta:
        verbose_name = u'Solicitação de Licitação'
        verbose_name_plural = u'Solicitações de Licitação'

    def get_proximo_item(self):
        if not self.itemsolicitacaolicitacao_set.exists():
            return u'1'
        else:
            ultimo = self.itemsolicitacaolicitacao_set.all().order_by('-item')[0]
            return int(ultimo.item) + 1

    def pode_enviar_para_compra(self):
        return self.situacao == SolicitacaoLicitacao.CADASTRADO

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

    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    item = models.IntegerField(u'Item')
    codigo = models.CharField(u'Código', max_length=15)
    especificacao = models.CharField(u'Especificação', max_length=5000)
    unidade = models.ForeignKey(TipoUnidade, verbose_name=u'Unidade')
    quantidade = models.PositiveIntegerField(u'Quantidade')
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(u'Total', decimal_places=2, max_digits=10, null=True, blank=True)
    situacao = models.CharField(u'Situação', max_length=50, choices=SITUACAO_CHOICES, default=CADASTRADO)
    obs = models.CharField(u'Observação', max_length=3000, null=True, blank=True)
    ativo = models.BooleanField(u'Ativo', default=True)

    def __unicode__(self):
        return 'Item: %s - Código: %s' % (self.item, self.codigo)

    class Meta:
        ordering = ['item']
        verbose_name = u'Item da Solicitação de Licitação'
        verbose_name_plural = u'Itens da Solicitação de Licitação'

    def get_lance_minimo(self):
        melhor_proposta = None
        melhor_lance = None
        propostas = PropostaItemPregao.objects.filter(item=self, concorre=True, desistencia=False, desclassificado=False).order_by('valor')
        if propostas.exists():
            melhor_proposta =  propostas[0]
        rodadas = LanceItemRodadaPregao.objects.filter(declinio=False, item=self).order_by('valor')
        if rodadas.exists():
            melhor_lance = rodadas[0]
        if melhor_proposta:
            if melhor_lance:
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
        if int(rodada_atual.rodada) > 1:
            rodada_anterior = int(rodada_atual.rodada) - 1
            participantes_por_ordem = LanceItemRodadaPregao.objects.filter(declinio=False, item=self, rodada__rodada=rodada_anterior).exclude(participante__in=ja_deu_lance).order_by('-valor')
        elif LanceItemRodadaPregao.objects.filter(declinio=False, item=self).exists():
            participantes_por_ordem = PropostaItemPregao.objects.filter(item=self, concorre=True).exclude(participante__in=ja_deu_lance).order_by('-valor')

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
        registros = ItemPesquisaMercadologica.objects.filter(item=self)
        if registros.exists():
            total_registros = registros.count()
            soma = registros.aggregate(Sum('valor_maximo'))
            return soma['valor_maximo__sum']/total_registros
        return None

    def get_valor_medio_envio_pesquisa(self):
        registros = ItemPesquisaMercadologica.objects.filter(item=self).exclude(pesquisa__arquivo__isnull=True).exclude(pesquisa__arquivo="")
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
        return False

    def get_podem_dar_lance(self):
        return PropostaItemPregao.objects.filter(item=self, concorre=True).values_list('participante', flat=True)

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


    def tem_item_anterior(self):
        if self.item > 1:
            anterior = self.item - 1
            if ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao).exists():
                return ItemSolicitacaoLicitacao.objects.filter(item=anterior, solicitacao=self.solicitacao)[0].id
        return False


    def tem_proximo_item(self):
        proximo = self.item + 1
        if ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao).exists():
            return ItemSolicitacaoLicitacao.objects.filter(item=proximo, solicitacao=self.solicitacao)[0].id
        return False

    def gerar_resultado(self):
        if not ResultadoItemPregao.objects.filter(item=self).exists():
            ids_participantes = []
            finalistas = []
            if PropostaItemPregao.objects.filter(item=self, concorre=True).exists():
                for lance in PropostaItemPregao.objects.filter(item=self, concorre=True).order_by('valor'):
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
        return self.situacao not in [Pregao.FRACASSADO, Pregao.DESERTO]

    def eh_fracassado(self):
        return self.situacao == Pregao.FRACASSADO


    def tem_rodada_aberta(self):
        return RodadaPregao.objects.filter(item=self, atual=True).exists()

    def sem_fornecedor_habilitado(self):
       return not ResultadoItemPregao.objects.filter(item=self, situacao=ResultadoItemPregao.CLASSIFICADO).exists()

    def tem_resultado(self):
        return ResultadoItemPregao.objects.filter(item=self).exists()

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


    solicitacao = models.ForeignKey(SolicitacaoLicitacao,verbose_name=u'Solicitação')
    num_pregao = models.CharField(u'Número do Pregão', max_length=255)
    num_processo = models.CharField(u'Número do Processo', max_length=255)
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
    cabecalho_ata = RichTextField(u'Cabeçalho da Ata de Registro de Preço', null=True, blank=True)

    class Meta:
        verbose_name = u'Pregão'
        verbose_name_plural = u'Pregões'

    def __unicode__(self):
        return self.num_pregao

    def eh_ativo(self):
        return self.situacao not in [Pregao.FRACASSADO, Pregao.DESERTO]

    def eh_suspenso(self):
        return self.situacao in [Pregao.SUSPENSO]

    def tem_resultado(self):
        return ResultadoItemPregao.objects.filter(item__solicitacao=self.solicitacao).exists()

#TODO usar esta estrutura para pregão por lote
class ItemPregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    codigo = models.CharField(u'Código', max_length=255)
    especificacao = models.CharField(u'Especificação', max_length=500)
    unidade = models.CharField(u'Unidade de Medida', max_length=500)
    quantidade = models.PositiveIntegerField(u'Quantidade')
    valor_medio = models.DecimalField(u'Valor Médio', max_digits=12, decimal_places=2)
    total = models.DecimalField(u'Total', max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = u'Item do Pregão'
        verbose_name_plural = u'Itens do Pregão'
        ordering = ['pregao','id']

    def __unicode__(self):
        return u'%s - %s' % (self.codigo, self.pregao)

class RamoAtividade(models.Model):
    nome = models.CharField(u'Nome', max_length=200)

    class Meta:
        verbose_name = u'Ramo de Atividade'
        verbose_name_plural = u'Ramos de Atividade'

    def __unicode__(self):
        return self.nome

class Fornecedor(models.Model):
    cnpj = models.CharField(u'CNPJ/CPF', max_length=255, help_text=u'Utilize pontos e traços.')
    razao_social = models.CharField(u'Razão Social', max_length=255)
    endereco = models.CharField(u'Endereço', max_length=255)
    ramo_atividade = models.ForeignKey(RamoAtividade, verbose_name=u'Ramo de Atividade')


    class Meta:
        verbose_name = u'Fornecedor'
        verbose_name_plural = u'Fornecedores'

    def __unicode__(self):
        return u'%s - %s' % (self.razao_social, self.cnpj)

class ParticipantePregao(models.Model):
    pregao = models.ForeignKey(Pregao,verbose_name=u'Pregão')
    fornecedor = models.ForeignKey(Fornecedor, verbose_name=u'Fornecedor')
    nome_representante = models.CharField(u'Nome do Representante', max_length=255, null=True, blank=True)
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
    marca = models.CharField(u'Marca', max_length=200)
    desclassificado = models.BooleanField(u'Desclassificado', default=False)
    motivo_desclassificacao = models.CharField(u'Motivo da Desclassificação', max_length=2000, null=True, blank=True)
    desistencia = models.BooleanField(u'Desistência', default=False)
    motivo_desistencia= models.CharField(u'Motivo da Desistência', max_length=2000, null=True, blank=True)
    concorre = models.BooleanField(u'Concorre', default=True)


    class Meta:
        verbose_name = u'Valor do Item do Pregão'
        verbose_name_plural = u'Valores do Item do Pregão'
        unique_together = ('item','participante')

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


class PessoaFisica(models.Model):
    SEXO_MASCULINO  = u'M'
    SEXO_FEMININO = u'F'
    SEXO_CHOICES = (
                    (SEXO_MASCULINO, u'Masculino'),
                    (SEXO_FEMININO, u'Feminino'),
                    )

    user = models.OneToOneField(User, null=True, blank=True)
    nome = models.CharField(max_length=80)
    cpf = models.CharField(u'CPF',max_length=15, help_text=u'Digite o CPF sem pontos ou traços.')
    sexo = models.CharField(u'Sexo', max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField(u'Data de Nascimento', null=True)
    telefones = models.CharField(u'Telefones', max_length=60, null=True, blank=True)
    celulares = models.CharField(u'Celulares', max_length=60, null=True, blank=True)
    email = models.CharField(u'Email', max_length=80, null=True, blank=True)
    logradouro = models.CharField(u'Logradouro', max_length=80, null=True, blank=True)
    numero = models.CharField(u'Número', max_length=10, null=True, blank=True)
    complemento = models.CharField(u'Complemento', max_length=80, null=True, blank=True)
    bairro = models.CharField(u'Bairro', max_length=80, null=True, blank=True)
    municipio = models.ForeignKey('base.Municipio', null=True, blank=True)
    cep = CepModelField(u'CEP', null=True, blank=True)
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
    nome = models.CharField(u'Identificação', max_length=80)
    portaria = models.CharField(u'Portaria', max_length=80)
    membro = models.ManyToManyField(PessoaFisica, related_name=u'Membros')

    def __unicode__(self):
        return self.nome

    class Meta:
        verbose_name = u'Comissão de Licitação'
        verbose_name_plural = u'Comissões de Licitação'


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


class ItemPesquisaMercadologica(models.Model):
    pesquisa = models.ForeignKey(PesquisaMercadologica, verbose_name=u'Pesquisa')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    marca = models.CharField(u'Marca', max_length=255)
    valor_maximo = models.DecimalField(u'Valor Máximo', max_digits=10, decimal_places=2, null=True, blank=True)


    def save(self):
        super(ItemPesquisaMercadologica, self).save()
        registros = ItemPesquisaMercadologica.objects.filter(item=self.item)
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
    marca = models.CharField(u'Marca', max_length=200)
    ordem = models.IntegerField(u'Classificação')
    situacao = models.CharField(u'Situação', max_length=100, choices=RESULTADO_CHOICES)
    observacoes = models.CharField(u'Observação', max_length=5000, null=True, blank=True)
    empate = models.BooleanField(u'Empate', default=False)

    class Meta:
        verbose_name = u'Resultado da Licitação'
        verbose_name_plural = u'Resultados da Licitação'


    def pode_alterar(self):
        return self.situacao == ResultadoItemPregao.CLASSIFICADO


class AnexoPregao(models.Model):
    pregao = models.ForeignKey(Pregao)
    nome = models.CharField(u'Nome', max_length=500)
    data = models.DateField(u'Data')
    arquivo = models.FileField(max_length=255, upload_to='upload/pregao/editais/anexos/', null=True,blank=True)
    cadastrado_por = models.ForeignKey(User)
    cadastrado_em = models.DateTimeField(u'Cadastrado em')

    class Meta:
        verbose_name = u'Anexo do Pregão'
        verbose_name_plural = u'Anexos do Pregão'

    def __unicode__(self):
        return '%s - %s' % (self.nome, self.pregao)

class LogDownloadArquivo(models.Model):
    PARTICIPAR = u'Participar da Licitação'
    CONSULTA = u'Apenas Consulta'
    INTERESSE_CHOICES = (
        (PARTICIPAR, PARTICIPAR),
        (CONSULTA, CONSULTA),

    )
    nome = models.CharField(u'Nome Empresarial', max_length=500)
    responsavel = models.CharField(u'Responsável', max_length=500)
    cpf = models.CharField(u'CPF', max_length=500)
    cnpj = models.CharField(u'CNPJ', max_length=500)
    endereco = models.CharField(u'Endereço', max_length=500)
    municipio = models.ForeignKey(Municipio, verbose_name=u'Cidade')
    telefone = models.CharField(u'Telefone', max_length=500)
    email =models.CharField(u'Email', max_length=500)
    interesse = models.CharField(u'Interesse', max_length=100, choices=INTERESSE_CHOICES)
    arquivo = models.ForeignKey(AnexoPregao)

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


class ItemQuantidadeSecretaria(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoLicitacao, verbose_name=u'Solicitação')
    item = models.ForeignKey(ItemSolicitacaoLicitacao)
    secretaria = models.ForeignKey(Secretaria)
    quantidade = models.IntegerField(u'Quantidade')

