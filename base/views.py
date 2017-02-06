# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from base.models import *
from base.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import xlrd
from xlrd.biffh import XLRDError
import datetime
import os
from django.template import Context
from django.template.loader import get_template
from django.template import RequestContext
from xhtml2pdf import pisa
from django.db.models import Q, F
from dal import autocomplete
from django.contrib.auth.models import Group
from templatetags.app_filters import format_money
from django.db.transaction import atomic
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.common import I2of5
from reportlab.lib.utils import simpleSplit
import collections
from django.conf import settings
from django.core.mail import send_mail

LARGURA = 210*mm
ALTURA = 297*mm


def get_config():
    if Configuracao.objects.exists():
        return Configuracao.objects.latest('id')
    return False

class SecretariaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Secretaria.objects.none()

        qs = Secretaria.objects.exclude(id=self.request.user.pessoafisica.setor.secretaria.id)

        if self.q:
            qs = qs.filter(nome__istartswith=self.q)

        return qs

class ParticipantePregaoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Fornecedor.objects.none()

        qs = Fornecedor.objects.all()

        if self.q:
            qs = qs.filter(Q(cnpj__istartswith=self.q) | Q(razao_social__istartswith=self.q))

        return qs

class PessoaFisicaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return PessoaFisica.objects.none()

        qs = PessoaFisica.objects.all()

        if self.q:
            qs = qs.filter(Q(nome__istartswith=self.q) | Q(cpf__istartswith=self.q))

        return qs


class MaterialConsumoAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return MaterialConsumo.objects.none()

        qs = MaterialConsumo.objects.all()

        if self.q:
            qs = qs.filter(Q(codigo__icontains=self.q) | Q(nome__icontains=self.q))

        return qs

@login_required()
def index(request):
    eh_ordenador_despesa = False
    if get_config():
        eh_ordenador_despesa = request.user.pessoafisica == get_config().ordenador_despesa
    tem_solicitacao = False
    title = u'Menu Inicial'
    if MovimentoSolicitacao.objects.filter(setor_destino=request.user.pessoafisica.setor, recebido_por__isnull=True).exists():
        tem_solicitacao = MovimentoSolicitacao.objects.filter(setor_destino=request.user.pessoafisica.setor, recebido_por__isnull=True)[0]
    tem_preencher_itens = False
    if SolicitacaoLicitacao.objects.filter(interessados=request.user.pessoafisica.setor.secretaria, prazo_resposta_interessados__gte=datetime.datetime.now().date(), itemsolicitacaolicitacao__isnull=False, setor_atual=F('setor_origem')).exists():
        for item in SolicitacaoLicitacao.objects.filter(interessados=request.user.pessoafisica.setor.secretaria, prazo_resposta_interessados__gte=datetime.datetime.now().date(), itemsolicitacaolicitacao__isnull=False):
            if not ItemQuantidadeSecretaria.objects.filter(solicitacao=item, secretaria=request.user.pessoafisica.setor.secretaria, aprovado=True).exists():
                tem_preencher_itens = item
                continue


    return render(request, 'index.html', locals(), RequestContext(request))

@login_required()
def solicitacoes(request):

    title = u'Solicitações'
    return render(request, 'solicitacoes.html', locals(), RequestContext(request))

@login_required()
def licitacoes(request):

    title = u'Licitações'
    return render(request, 'licitacoes.html', locals(), RequestContext(request))

@login_required()
def pedidos_e_controle(request):

    title = u'Pedidos e Controle'
    return render(request, 'pedidos_e_controle.html', locals(), RequestContext(request))

@login_required()
def administracao(request):

    title = u'Administração'
    return render(request, 'administracao.html', locals(), RequestContext(request))

@login_required()
def cadastros(request):

    title = u'Cadastros'
    return render(request, 'cadastros.html', locals(), RequestContext(request))

@login_required()
def fornecedor(request, fornecedor_id):

    fornecedor = get_object_or_404(Fornecedor, pk= fornecedor_id)
    title = u'Dados do Fornecedor: %s' % fornecedor.razao_social
    exibe_popup = True
    return render(request, 'ver_fornecedores.html', locals(), RequestContext(request))

@login_required()
def pregao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk= pregao_id)

    if not (pregao.solicitacao.setor_atual == request.user.pessoafisica.setor) and pregao.eh_ativo():
        pregao.situacao = Pregao.CONCLUIDO
        pregao.save()

    elif pregao.solicitacao.setor_atual == request.user.pessoafisica.setor and pregao.situacao == Pregao.CONCLUIDO:
        pregao.situacao = Pregao.CADASTRADO
        pregao.save()


    eh_lote = pregao.criterio.id == CriterioPregao.LOTE
    eh_maior_desconto = pregao.tipo.id == TipoPregao.DESCONTO
    title = u'%s ' % pregao
    if eh_lote:
        lotes = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True)
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao=ItemSolicitacaoLicitacao.CADASTRADO)
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao=ItemSolicitacaoLicitacao.CADASTRADO)
    #title = u'Pregão: %s (Processo: %s) - Situação: %s' % (pregao.num_pregao, pregao.num_processo, pregao.situacao)
    itens_pregao_unidades = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False)
    participantes = ParticipantePregao.objects.filter(pregao=pregao,desclassificado=False)
    resultados = ResultadoItemPregao.objects.filter(item__in=itens_pregao.values_list('id',flat=True))
    buscou = False
    ids_ganhador = list()
    if request.GET.get('participante'):
        buscou = True
        participante = get_object_or_404(ParticipantePregao, pk=request.GET.get('participante'))

        for opcao in itens_pregao:
            resultados = ResultadoItemPregao.objects.filter(item=opcao, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')
            if resultados.exists() and resultados[0].participante == participante:
                ids_ganhador.append(resultados[0].item.id)
        itens_pregao = itens_pregao.filter(id__in=ids_ganhador)

        form = GanhadoresForm(request.POST or None, participantes = participantes, initial=dict(ganhador=participante))
    else:
        form = GanhadoresForm(request.POST or None, participantes = participantes)

    return render(request, 'pregao.html', locals(), RequestContext(request))

@login_required()
def cadastra_proposta_pregao(request, pregao_id):
    title=u'Cadastrar Proposta'
    pregao = get_object_or_404(Pregao, pk= pregao_id)
    itens = pregao.solicitacao.itemsolicitacaolicitacao_set.filter(eh_lote=False).order_by('item')
    edicao=False
    participante = None
    selecionou = False
    if request.GET.get('participante'):
        selecionou = True
        participante = get_object_or_404(ParticipantePregao, pk=request.GET.get('participante'))
        itens = PropostaItemPregao.objects.filter(pregao=pregao, participante=participante, item__eh_lote=False).order_by('item')
        if itens.exists():
            edicao=True
        else:
            itens = pregao.solicitacao.itemsolicitacaolicitacao_set.filter(eh_lote=False).order_by('item')
    if edicao or selecionou:
        form = CadastraPrecoParticipantePregaoForm(request.POST or None, request.FILES, pregao=pregao, initial=dict(fornecedor=participante))
    else:
        form = CadastraPrecoParticipantePregaoForm(request.POST or None, request.FILES, pregao=pregao)
    if form.is_valid():
        arquivo_up = form.cleaned_data.get('arquivo')
        fornecedor = form.cleaned_data.get('fornecedor')
        if arquivo_up:
            sheet = None
            try:
                workbook = xlrd.open_workbook(file_contents=arquivo_up.read())
                sheet = workbook.sheet_by_index(0)
            except XLRDError:
                raise Exception(u'Não foi possível processar a planilha. Verfique se o formato do arquivo é .xls ou .xlsx.')

            for row in range(1, sheet.nrows):
                try:
                    item = unicode(sheet.cell_value(row, 0)).strip()
                    marca = unicode(sheet.cell_value(row, 5)).strip() or None
                    valor = unicode(sheet.cell_value(row, 6)).strip()
                    if row == 0:
                        if item != u'Item' or valor != u'VALOR UNITÁRIO':
                            raise Exception(u'Não foi possível processar a planilha. As colunas devem ter Item e Valor.')
                    else:
                        if item and valor:
                            item_do_pregao = ItemSolicitacaoLicitacao.objects.get(eh_lote=False, solicitacao=pregao.solicitacao,item=int(sheet.cell_value(row, 0)))
                            if PropostaItemPregao.objects.filter(item=item_do_pregao, pregao=pregao, participante=fornecedor).exists():
                                PropostaItemPregao.objects.filter(item=item_do_pregao, pregao=pregao, participante=fornecedor).update(marca=marca, valor=valor)
                            else:
                                novo_preco = PropostaItemPregao()
                                novo_preco.item = item_do_pregao
                                novo_preco.pregao = pregao
                                novo_preco.participante = fornecedor
                                novo_preco.valor = valor
                                novo_preco.marca = marca
                                novo_preco.save()
                            if not ParticipanteItemPregao.objects.filter(participante=fornecedor, item=item_do_pregao).exists():
                                participante_item = ParticipanteItemPregao()
                                participante_item.participante = fornecedor
                                participante_item.item = item_do_pregao
                                participante_item.save()


                except ValueError:
                    raise Exception(u'Alguma coluna da planilha possui o valor incorreto.')
        if not edicao and not arquivo_up:
            for idx, item in enumerate(request.POST.getlist('itens'), 1):
                if item:
                    item_do_pregao = ItemSolicitacaoLicitacao.objects.get(eh_lote=False, solicitacao=pregao.solicitacao, id=request.POST.getlist('id_item')[idx-1])
                    novo_preco = PropostaItemPregao()
                    novo_preco.item = item_do_pregao
                    novo_preco.pregao = pregao
                    novo_preco.participante = fornecedor
                    novo_preco.valor = item.replace('.','').replace(',','.')
                    novo_preco.marca = request.POST.getlist('marcas')[idx-1]
                    novo_preco.save()


        lotes = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True)
        if lotes.exists():
            for lote in lotes:
                itens = ItemLote.objects.filter(lote=lote)
                if itens.exists():
                    propostas = PropostaItemPregao.objects.filter(item__in=itens.values_list('item', flat=True), participante=fornecedor, pregao=pregao)
                    if propostas.exists():
                        total_propostas = propostas.aggregate(total=Sum('valor'))['total']
                        if PropostaItemPregao.objects.filter(item=lote, pregao=pregao, participante=fornecedor).exists():
                            PropostaItemPregao.objects.filter(item=lote, pregao=pregao, participante=fornecedor).update(valor=total_propostas)
                        else:
                            nova_proposta_para_lote = PropostaItemPregao()
                            nova_proposta_para_lote.pregao = pregao
                            nova_proposta_para_lote.item = lote
                            nova_proposta_para_lote.participante = fornecedor
                            nova_proposta_para_lote.valor = total_propostas
                            nova_proposta_para_lote.save()

        messages.success(request, u'Proposta cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/cadastra_proposta_pregao/%s/?participante=%s' % (pregao.id, fornecedor.id))
    else:
        if edicao or selecionou:
            form = CadastraPrecoParticipantePregaoForm(request.POST or None, pregao=pregao, initial=dict(fornecedor=participante))
        else:
            form = CadastraPrecoParticipantePregaoForm(request.POST or None, pregao=pregao)

    return render(request, 'cadastra_proposta_pregao.html', locals(), RequestContext(request))


@login_required()
def propostas_item(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk= item_id)
    itens = PropostaItemPregao.objects.filter(item=item)
    titulo = u'Valores - Item %s - Pregão: %s' % (item.item, item.solicitacao.pregao_set.all()[0])
    eh_modalidade_desconto = item.solicitacao.eh_maior_desconto()

    return render(request, 'propostas_item.html', locals(), RequestContext(request))

@login_required()
def cadastra_participante_pregao(request, pregao_id):
    title=u'Cadastrar Participante do Pregão'
    pregao = get_object_or_404(Pregao, pk= pregao_id)
    id_sessao = "%s_fornecedor" % (request.user.pessoafisica.id)
    request.session[id_sessao] = pregao.id
    form = CadastraParticipantePregaoForm(request.POST or None, pregao=pregao)
    if form.is_valid():
        if ParticipantePregao.objects.filter(pregao=pregao,fornecedor=form.cleaned_data['fornecedor']).exists():
            messages.error(request, u'Este fornecedor já foi cadastrado.')
            return HttpResponseRedirect(u'/base/pregao/%s/' % pregao.id)

        o = form.save(False)
        o.pregao = pregao
        if form.cleaned_data.get('sem_representante'):
            o.pode_dar_lance = False
            historico = HistoricoPregao()
            historico.pregao = pregao
            historico.data = datetime.datetime.now()
            historico.obs = u'Ausência do participante: %s. Motivo: %s' % (form.cleaned_data['fornecedor'], form.cleaned_data.get('obs_ausencia_participante'))
            historico.save()
        o.save()

        messages.success(request, u'Participante cadastrado com sucesso')
        return HttpResponseRedirect(u'/base/pregao/%s/#fornecedores' % pregao.id)

    return render(request, 'cadastra_participante_pregao.html', locals(), RequestContext(request))

@login_required()
def rodada_pregao(request, item_id):

    item = get_object_or_404(ItemSolicitacaoLicitacao, pk= item_id)
    pregao = get_object_or_404(Pregao, solicitacao=item.solicitacao)
    rodadas = RodadaPregao.objects.filter(item=item).order_by('-rodada')
    if rodadas.exists():
        num_rodada = rodadas[0].rodada + 1

    else:
        num_rodada = 1

    RodadaPregao.objects.filter(item=item).update(atual=False)
    nova_rodada = RodadaPregao()
    nova_rodada.rodada = num_rodada
    nova_rodada.pregao = pregao
    nova_rodada.item = item
    nova_rodada.atual = True
    nova_rodada.save()
    messages.success(request, u'Nova rodada cadastrada.')
    return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

@login_required()
def lances_rodada_pregao(request, rodada_id, item_id):

    rodada = get_object_or_404(RodadaPregao, pk= rodada_id)

    title=u'Rodada %s do %s' % (rodada.rodada, rodada.pregao)
    lances_rodadas = LanceItemRodadaPregao.objects.filter(rodada=rodada).order_by('item')
    return render(request, 'lances_rodada_pregao.html', locals(), RequestContext(request))

@login_required()
def declinar_lance(request, rodada_id, item_id, participante_id):

    rodada = get_object_or_404(RodadaPregao, pk= rodada_id)
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    participante = get_object_or_404(ParticipantePregao, pk=participante_id)

    novo_lance = LanceItemRodadaPregao()
    novo_lance.item = item
    novo_lance.rodada = rodada
    novo_lance.participante = participante
    novo_lance.declinio = True
    novo_lance.ordem_lance = rodada.get_ordem_lance()
    novo_lance.save()

    messages.success(request, u'Lance declinado com sucesso.')
    return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)


@login_required()
def lances_item(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk= item_id)
    pregao = item.solicitacao.get_pregao()
    desempatar = False
    botao_incluir = False
    eh_modalidade_desconto = item.solicitacao.eh_maior_desconto()

    fornecedores_lance = PropostaItemPregao.objects.filter(item=item, concorre=True).order_by('-concorre', 'desclassificado','desistencia', 'valor')
    if request.GET.get('empate'):
        desempatar = True
    # if not PropostaItemPregao.objects.filter(item=item).exists():
    #     messages.error(request, u'Este item não possui nenhuma proposta cadastrada.')
    #    return HttpResponseRedirect(u'/base/pregao/%s/#propostas' % item.get_licitacao().id)
    rodadas = RodadaPregao.objects.filter(item=item)
    itens_do_lote = False
    if item.eh_lote:
        itens_do_lote = ItemSolicitacaoLicitacao.objects.filter(id__in=ItemLote.objects.filter(lote=item).values_list('item', flat=True))


    if request.GET and request.GET.get('filtrar') == u'1':
        if item.ja_recebeu_lance():
            messages.info(request,u'Não é possível aplicar filtro após o início dos lances.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)
        else:
            if not request.GET.get('incluido') and not request.GET.get('incluir'):
                item.filtrar_por_10_porcento()
            botao_incluir = True
            if request.GET.get('incluir') == u'1':
                fornecedores_lance = item.get_lista_participantes(inativos=True)
            else:
                fornecedores_lance = item.get_lista_participantes(ativos=True)
    elif  request.GET and request.GET.get('filtrar') == u'2':
        if item.ja_recebeu_lance():
            messages.info(request,u'Não é possível aplicar filtro após o início dos lances.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)
        else:
            item.filtrar_todos_ativos()
    form = LanceForm(request.POST or None)
    if form.is_valid():
        rodada_atual = item.get_rodada_atual()
        if desempatar and item.tem_empate_beneficio():
            participante = item.get_participante_desempate()
        else:
            participante = item.get_proximo_lance() or item.get_participante_desempate()
        rodada_anterior = int(rodada_atual.rodada) - 1
        if not eh_modalidade_desconto:
            if int(rodada_atual.rodada) == 1 and form.cleaned_data.get('lance') >= PropostaItemPregao.objects.get(item=item, participante=participante).valor:
                messages.error(request, u'Você não pode dar uma lance maior do que sua proposta.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if int(rodada_atual.rodada) > 1 and form.cleaned_data.get('lance') >= LanceItemRodadaPregao.objects.get(item=item, participante=participante, rodada__rodada=rodada_anterior).valor:
                messages.error(request, u'Você não pode dar uma lance maior do que o lance da rodada anterior.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if form.cleaned_data.get('lance') > item.valor_medio:
                messages.error(request, u'Você não pode dar uma lance maior do que o valor máximo do item.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if LanceItemRodadaPregao.objects.filter(item=item, valor=form.cleaned_data.get('lance')):
                messages.error(request, u'Este lance já foi dado.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if desempatar and item.tem_empate_beneficio():
                if LanceItemRodadaPregao.objects.filter(item=item, valor__lt=form.cleaned_data.get('lance')).exists():
                    messages.error(request, u'Você não pode dar um lance maior que o menor lance atual.')
                    return HttpResponseRedirect(u'/base/lances_item/%s/?empate=True' % item.id)

        else:
            if int(rodada_atual.rodada) == 1 and form.cleaned_data.get('lance') <= PropostaItemPregao.objects.get(item=item, participante=participante).valor:
                messages.error(request, u'Você não pode dar uma lance menor do que sua proposta.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if int(rodada_atual.rodada) > 1 and form.cleaned_data.get('lance') <= LanceItemRodadaPregao.objects.get(item=item, participante=participante, rodada__rodada=rodada_anterior).valor:
                messages.error(request, u'Você não pode dar uma lance menor do que o lance da rodada anterior.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            # if form.cleaned_data.get('lance') >= item.valor_medio:
            #     messages.error(request, u'Você não pode dar uma lance maior do que o valor máximo do item.')
            #     return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if LanceItemRodadaPregao.objects.filter(item=item, valor=form.cleaned_data.get('lance')):
                messages.error(request, u'Este lance já foi dado.')
                return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

            if desempatar and item.tem_empate_beneficio():
                if LanceItemRodadaPregao.objects.filter(item=item, valor__gt=form.cleaned_data.get('lance')).exists():
                    messages.error(request, u'Você não pode dar um lance menor que o maior lance atual.')
                    return HttpResponseRedirect(u'/base/lances_item/%s/?empate=True' % item.id)



        novo_lance = LanceItemRodadaPregao()
        novo_lance.item = item
        novo_lance.rodada = rodada_atual
        novo_lance.participante = participante
        novo_lance.valor = form.cleaned_data.get('lance')
        novo_lance.ordem_lance = rodada_atual.get_ordem_lance()
        novo_lance.save()
        messages.success(request, u'Novo lance cadastrado com sucesso.')

    if item.eh_lote:
        title=u'Lances - Lote: %s' % item.item
    else:
        title=u'Lances - Item: %s' % item
    tabela = {}
    resultado = {}
    lances = LanceItemRodadaPregao.objects.filter(item=item)


    num_rodadas =  rodadas.values('rodada').order_by('rodada').distinct('rodada')
    for num in num_rodadas:
        chave = '%s' % num['rodada']
        tabela[chave] = []
    for lance in lances.order_by('id'):
        chave = '%s' % str(lance.rodada.rodada)
        tabela[chave].append(lance)

    resultado = collections.OrderedDict(sorted(tabela.items(), reverse=True,  key=lambda x: int(x[0])))
    return render(request, 'lances_item.html', locals(), RequestContext(request))

@login_required()
def ver_fornecedores(request, fornecedor_id=None):
    title=u'Lista de Fornecedores'
    fornecedores = Fornecedor.objects.all()
    exibe_popup = False

    if fornecedor_id:
        fornecedor = get_object_or_404(Fornecedor, pk= fornecedor_id)
        exibe_popup = True

    return render(request, 'ver_fornecedores.html', locals(), RequestContext(request))

@login_required()
def ver_pregoes(request):
    title=u'Licitações'
    pregoes = Pregao.objects.all()
    eh_ordenador_despesa = False
    if get_config():
        eh_ordenador_despesa = request.user.pessoafisica == get_config().ordenador_despesa

    form = BuscarSolicitacaoForm(request.POST or None)

    if form.is_valid():

        pregoes = pregoes.filter(Q(solicitacao__processo__numero=form.cleaned_data.get('info')) | Q(solicitacao__num_memorando=form.cleaned_data.get('info')))
    return render(request, 'ver_pregoes.html', locals(), RequestContext(request))

@login_required()
def itens_solicitacao(request, solicitacao_id):
    url = settings.URL

    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'%s' % (solicitacao)
    setor_do_usuario = request.user.pessoafisica.setor
    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao, eh_lote=False).order_by('item')
    pedidos = PedidoItem.objects.filter(solicitacao=solicitacao).order_by('item')
    eh_lote = pedidos.filter(proposta__isnull=False).exists()
    ja_registrou_preco = ItemQuantidadeSecretaria.objects.filter(solicitacao=solicitacao, secretaria=request.user.pessoafisica.setor.secretaria)
    ja_aprovou = ja_registrou_preco.filter(aprovado=True).exists()
    recebida_no_setor = False
    movimentacao = MovimentoSolicitacao.objects.filter(solicitacao=solicitacao)
    if movimentacao.exists():
        ultima_movimentacao = MovimentoSolicitacao.objects.filter(solicitacao=solicitacao).latest('id')
        if ultima_movimentacao.setor_destino == setor_do_usuario and ultima_movimentacao.data_recebimento:
            recebida_no_setor = True
    elif solicitacao.setor_atual == setor_do_usuario:
        if itens.exists() and solicitacao.tipo == SolicitacaoLicitacao.LICITACAO:
            recebida_no_setor = True
        elif solicitacao.tipo == SolicitacaoLicitacao.COMPRA:
            recebida_no_setor = True

    return render(request, 'itens_solicitacao.html', locals(), RequestContext(request))


@login_required()
def cadastrar_item_solicitacao(request, solicitacao_id):
    title=u'Cadastrar Item'
    id_user = '%s' % request.user.pessoafisica.id
    request.session[id_user] = solicitacao_id
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    form = CadastrarItemSolicitacaoForm(request.POST or None, initial=dict(solicitacao=solicitacao), solicitacao=solicitacao)
    if form.is_valid():
        o = form.save(False)
        o.solicitacao = solicitacao
        o.item = solicitacao.get_proximo_item()
        if o.valor_medio:
            o.total = o.valor_medio * o.quantidade
        o.save()
        novo_item = ItemQuantidadeSecretaria()
        novo_item.solicitacao = solicitacao
        novo_item.item = o
        novo_item.secretaria = request.user.pessoafisica.setor.secretaria
        novo_item.quantidade = o.quantidade
        novo_item.aprovado = True
        novo_item.avaliado_por = request.user
        novo_item.avaliado_em = datetime.datetime.now()
        novo_item.save()

        # send_mail('Subject here', 'Here is the message.', settings.EMAIL_HOST_USER,
        #  ['walkyso@gmail.com'], fail_silently=False)


        messages.success(request, u'Item cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)

    return render(request, 'cadastrar_item_solicitacao.html', locals(), RequestContext(request))

def baixar_editais(request):
    hoje = datetime.date.today()
    pregoes = Pregao.objects.all()
    form = BaixarEditaisForm(request.POST or None)
    if form.is_valid():
        pregoes = pregoes.filter(modalidade=form.cleaned_data.get('modalidade'))
    return render(request, 'baixar_editais.html', locals(), RequestContext(request))

@login_required()
def ver_solicitacoes(request):
    title=u'Lista de Solicitações'

    setor = request.user.pessoafisica.setor
    movimentacoes_setor = MovimentoSolicitacao.objects.filter(Q(setor_origem=setor) | Q(setor_destino=setor))
    solicitacoes = SolicitacaoLicitacao.objects.filter(Q(setor_origem=setor, situacao=SolicitacaoLicitacao.CADASTRADO)  | Q(setor_atual=setor, situacao__in=[SolicitacaoLicitacao.RECEBIDO, SolicitacaoLicitacao.EM_LICITACAO])).order_by('-data_cadastro')
    outras = SolicitacaoLicitacao.objects.exclude(id__in=solicitacoes.values_list('id', flat=True)).filter(Q(id__in=movimentacoes_setor.values_list('solicitacao', flat=True)) | Q(interessados=setor.secretaria)).distinct().order_by('-data_cadastro')
    aba1 = u''
    aba2 = u'in active'
    class_aba1 = u''
    class_aba2 = u'active'
    form = BuscarSolicitacaoForm(request.POST or None)

    if form.is_valid():
        aba1 = u'in active'
        aba2 = u''
        class_aba1 = u'active'
        class_aba2 = u''
        outras = SolicitacaoLicitacao.objects.filter(Q(processo__numero=form.cleaned_data.get('info')) | Q(num_memorando=form.cleaned_data.get('info')))
    return render(request, 'ver_solicitacoes.html', locals(), RequestContext(request))

@login_required()
def rejeitar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Negar Solicitação %s' % solicitacao.num_memorando
    form = RejeitarSolicitacaoForm(request.POST or None, instance=solicitacao)
    if form.is_valid():
        o = form.save(False)
        o.situacao = SolicitacaoLicitacao.NEGADA
        o.save()
        messages.success(request, u'Solicitação rejeitada com sucesso.')
        return HttpResponseRedirect(u'/base/ver_solicitacoes/')

    return render(request, 'rejeitar_solicitacao.html', locals(), RequestContext(request))

@login_required()
def cadastrar_pregao(request, solicitacao_id):
    title=u'Cadastrar Licitação'
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    form = PregaoForm(request.POST or None, solicitacao=solicitacao)
    if form.is_valid():
        form.save()
        solicitacao.situacao = SolicitacaoLicitacao.EM_LICITACAO
        solicitacao.save()
        messages.success(request, u'Licitação cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/' % form.instance.id)

    return render(request, 'cadastrar_pregao.html', locals(), RequestContext(request))

@login_required()
def cadastrar_solicitacao(request):
    title=u'Cadastrar Solicitação'
    form = SolicitacaoForm(request.POST or None, request=request)
    if form.is_valid():
        o = form.save(False)
        o.setor_origem = request.user.pessoafisica.setor
        o.setor_atual = request.user.pessoafisica.setor
        o.data_cadastro = datetime.datetime.now()
        o.cadastrado_por = request.user
        if not form.cleaned_data['interessados']:
            o.prazo_resposta_interessados = None
        o.save()
        if form.cleaned_data['interessados'] and form.cleaned_data['outros_interessados']:
            form.save_m2m()
        messages.success(request, u'Solicitação cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % form.instance.id)

    return render(request, 'cadastrar_pregao.html', locals(), RequestContext(request))

@login_required()
def editar_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Editar Solicitação'
    form = SolicitacaoForm(request.POST or None, instance=solicitacao, request=request)
    if form.is_valid():
        o = form.save(False)
        o.setor_origem = request.user.pessoafisica.setor
        o.setor_atual = request.user.pessoafisica.setor
        o.data_cadastro = datetime.datetime.now()
        o.cadastrado_por = request.user
        if not form.cleaned_data.get('interessados'):
            o.prazo_resposta_interessados = None
        o.save()
        if form.cleaned_data.get('interessados') and form.cleaned_data['outros_interessados']:
            form.save_m2m()
        messages.success(request, u'Solicitação cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % form.instance.id)

    return render(request, 'cadastrar_pregao.html', locals(), RequestContext(request))


@login_required()
def cadastrar_material(request, solicitacao_id):
    title=u'Cadastrar Material'
    form = MaterialConsumoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, u'Material com sucesso.')
        return HttpResponseRedirect(u'/base/cadastrar_item_solicitacao/%s/' % solicitacao_id)

    return render(request, 'cadastrar_anexo_pregao.html', locals(), RequestContext(request))

@login_required()
def cadastrar_documento(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Cadastrar Documento'
    form = DocumentoSolicitacaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        o = form.save(False)
        o.solicitacao = solicitacao
        o.cadastrado_por = request.user
        o.cadastrado_em = datetime.datetime.now()
        o.save()
        messages.success(request, u'Documento cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/lista_documentos/%s/' % solicitacao_id)

    return render(request, 'cadastrar_documento.html', locals(), RequestContext(request))

@login_required()
def enviar_para_licitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    solicitacao.situacao = SolicitacaoLicitacao.ENVIADO
    solicitacao.save()
    messages.success(request, u'Solicitação enviada com sucesso.')
    return HttpResponseRedirect(u'/base/ver_solicitacoes/')

@login_required()
def registrar_preco_item(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    title = u'Registrar Valor - %s' % item
    form = RegistrarPrecoItemForm(request.POST or None, instance=item)
    if form.is_valid():
        o = form.save(False)
        o.total = o.quantidade*o.valor_medio
        o.save()
        messages.success(request, u'Valor registrado com sucesso.')
        return HttpResponseRedirect(u'/itens_solicitacao/%s/' % item.solicitacao.id)
    return render(request, 'registrar_preco_item.html', locals(), RequestContext(request))

@login_required()
def pesquisa_mercadologica(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    return HttpResponseRedirect(u'/base/planilha_pesquisa_mercadologica/%s/' % solicitacao.id)


def planilha_pesquisa_mercadologica(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao).order_by('item')

    import xlwt
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=PesquisaMercadologica_Solicitacao.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Sheet1")
    row_num = 0

    columns = [
        (u"Item"),
        (u"Material"),
        (u"Unidade"),
        (u"Marca"),
        (u"Valor Unitario"),
    ]

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num])

    for obj in itens:
        row_num += 1
        row = [
            obj.item,
            obj.material.nome,
            obj.unidade.nome,
            '',
            '',
        ]
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num])

    wb.save(response)
    return response

def preencher_pesquisa_mercadologica(request, solicitacao_id):
    title = u'Preencher Pesquisa Mercadológica'
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    if not solicitacao.prazo_aberto:
        messages.error(request, u'Prazo de envio encerrado.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s' % solicitacao.id)

    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao).order_by('item')

    form = PesquisaMercadologicaForm(request.POST or None, request=request, solicitacao=solicitacao)
    if form.is_valid():
        o = form.save(False)
        o.solicitacao = solicitacao
        if form.cleaned_data.get('origem_opcao') is False:
            o.origem = PesquisaMercadologica.ATA_PRECO
        elif form.cleaned_data.get('origem_opcao') is True:
            o.origem = PesquisaMercadologica.FORNECEDOR
        else:
            messages.error(request, u'Selecione a origem.')
            return HttpResponseRedirect(u'/base/preencher_pesquisa_mercadologica/%s/' % solicitacao.id)


        o.save()
        if form.cleaned_data.get('origem_opcao') is False:
            messages.success(request, u'Cadastro realizado com sucesso.')
            return HttpResponseRedirect(u'/base/upload_itens_pesquisa_mercadologica/%s/' % o.id)

        else:
            messages.success(request, u'Cadastro realizado com sucesso. Envie a planilha abaixo com os valores dos itens.')
            return HttpResponseRedirect(u'/base/preencher_itens_pesquisa_mercadologica/%s/' % o.id)

    return render(request, 'preencher_pesquisa_mercadologica.html', locals(), RequestContext(request))

def preencher_itens_pesquisa_mercadologica(request, pesquisa_id):
    title=u'Preencher Itens da Pesquisa Mercadológica'
    pesquisa = get_object_or_404(PesquisaMercadologica, pk=pesquisa_id)
    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pesquisa.solicitacao)
    if request.POST:
        if request.POST.get('validade') in [''] and pesquisa.origem == PesquisaMercadologica.FORNECEDOR:
            messages.error(request, u'Preencha a validade da proposta.')
            return HttpResponseRedirect(u'/base/preencher_itens_pesquisa_mercadologica/%s/' % pesquisa.id)
        for idx, item in enumerate(request.POST.getlist('itens'), 1):
            if item:
                item_do_pregao = ItemSolicitacaoLicitacao.objects.get(solicitacao=pesquisa.solicitacao, id=request.POST.getlist('id_item')[idx-1])
                novo_preco = ItemPesquisaMercadologica()
                novo_preco.pesquisa = pesquisa
                novo_preco.item = item_do_pregao
                novo_preco.valor_maximo = item.replace('.','').replace(',','.')
                novo_preco.marca = request.POST.getlist('marcas')[idx-1]
                novo_preco.save()
        if request.POST.get('validade'):
            pesquisa.validade_proposta = int(request.POST.get('validade'))
            pesquisa.save()
            messages.success(request, u'Valores cadastrados com sucesso.')
            return HttpResponseRedirect(u'/base/upload_pesquisa_mercadologica/%s/' % pesquisa.id)
        else:
            messages.success(request, u'Valores cadastrados com sucesso.')
            return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % pesquisa.solicitacao.id)


    return render(request, 'preencher_itens_pesquisa_mercadologica.html', locals(), RequestContext(request))


def upload_pesquisa_mercadologica(request, pesquisa_id):
    title=u'Enviar Orçamento da Pesquisa Mercadológica'
    pesquisa = get_object_or_404(PesquisaMercadologica, pk=pesquisa_id)
    form = UploadPesquisaForm(request.POST or None, request.FILES or None, instance=pesquisa)
    if form.is_valid():
        o = form.save(False)
        o.cadastrada_em = datetime.datetime.now()
        o.save()
        messages.success(request, u'Pesquisa cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/ver_solicitacoes/')

    return render(request, 'upload_pesquisa_mercadologica.html', locals(), RequestContext(request))


def imprimir_pesquisa(request, pesquisa_id):
    pesquisa = get_object_or_404(PesquisaMercadologica, pk=pesquisa_id)

    destino_arquivo = u'upload/pesquisas/rascunhos/%s.pdf' % pesquisa_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()


    data = {'pesquisa': pesquisa, 'data_emissao':data_emissao}

    template = get_template('imprimir_pesquisa.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


@login_required()
def ver_pesquisa_mercadologica(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    title=u'Pesquisa Mercadológica'
    pesquisas = ItemPesquisaMercadologica.objects.filter(item=item)

    return render(request, 'ver_pesquisa_mercadologica.html', locals(), RequestContext(request))

@login_required()
def resultado_classificacao(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    title = u'Classificação - %s' % item
    lances = ResultadoItemPregao.objects.filter(item=item).order_by('ordem')
    pregao = item.get_licitacao()
    return render(request, 'resultado_classificacao.html', locals(), RequestContext(request))

@login_required()
def desclassificar_do_pregao(request, participante_id):
    title=u'Desclassificar Participante'
    participante = get_object_or_404(ParticipantePregao, pk=participante_id)
    pregao = participante.pregao
    form = DesclassificaParticipantePregao(request.POST or None, instance = participante)
    if form.is_valid():
        o = form.save(False)
        o.desclassificado = True
        o.save()
        if PropostaItemPregao.objects.filter(participante=participante).exists():
            PropostaItemPregao.objects.filter(participante=participante).update(concorre=False, desclassificado=True, motivo_desclassificacao=o.motivo_desclassificacao)
        historico = HistoricoPregao()
        historico.pregao = participante.pregao
        historico.data = datetime.datetime.now()
        historico.obs = u'Desclassificação do participante: %s. Motivo: %s' % (participante, form.cleaned_data.get('motivo_desclassificacao'))
        historico.save()
        messages.success(request, u'Desclassificação cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/' % participante.pregao.id)
    return render(request, 'desclassificar_do_pregao.html', locals(), RequestContext(request))

@login_required()
def planilha_propostas(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    pregao = get_object_or_404(Pregao, solicitacao=solicitacao)
    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao, eh_lote=False).order_by('item')

    # import xlwt
    #
    # workbook = xlwt.open_workbook(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor.xls'))
    #
    #
    # sheet = workbook.sheet_by_index(0)
    #
    # for row in range(0, sheet.nrows):
    #     if row == 20:
    #
    #        sheet.write(row, 0, label = 'Row 0, Column 0 Value')
    #
    # workbook.save(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor_teste.xls'))
    from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
    from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd

    nome = os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor')
    file_path = os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor.xls')
    rb = open_workbook(file_path,formatting_info=True)

    wb = copy(rb) # a writable copy (I can't read values out of this, only write to it)
    w_sheet = wb.get_sheet(0) # the sheet to write to within the writable copy
    # w_sheet.write(1, 1, solicitacao.get_pregao().num_pregao)
    # w_sheet.write(2, 1, solicitacao.objetivo)
    # endereco = u'%s, dia %s às %s.' % (solicitacao.get_pregao().local, solicitacao.get_pregao().data_abertura, solicitacao.get_pregao().hora_abertura)
    # w_sheet.write(3, 1, endereco)


    sheet = rb.sheet_by_name("Sheet1")
    for idx, item in enumerate(itens, 0):
        row_index = idx + 1
        # cell = sheet.cell(row_index, 0)
        # print "cell.xf_index is", cell.xf_index
        # fmt = rb.xf_list[cell.xf_index]
        # print "type(fmt) is", type(fmt)

        w_sheet.write(row_index, 0, item.item)
        w_sheet.write(row_index, 1, item.material.nome)
        w_sheet.write(row_index, 2, item.unidade.nome)
        w_sheet.write(row_index, 3, item.quantidade)
        w_sheet.write(row_index, 4, item.valor_medio)

    salvou = nome + u'_%s' % pregao.id + '.xls'
    wb.save(salvou)

    arquivo = open(salvou, "rb")


    content_type = 'application/vnd.ms-excel'
    response = HttpResponse(arquivo.read(), content_type=content_type)
    nome_arquivo = salvou.split('/')[-1]
    response['Content-Disposition'] = 'attachment; filename=%s' % nome_arquivo
    arquivo.close()
    os.unlink(salvou)
    return response

    # import ipdb; ipdb.set_trace()
    # wb = load_workbook(filename = os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor.xlsx'))
    #
    # wb = load_workbook(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor.xlsx'))
    # sheet = wb.get_sheet_by_name('Sheet1')
    # print sheet
    # #
    # # import ipdb; ipdb.set_trace()
    # # stimulusTimes = [1, 2, 3]
    # # reactionTimes = [2.3, 5.1, 7.0]
    # #
    # # for i in range(len(stimulusTimes)):
    # #     sheet['A' + str(i + 6)].value = stimulusTimes[i]
    # #     sheet['B' + str(i + 6)].value = reactionTimes[i]
    # #
    # # wb.save(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/modelo_proposta_fornecedor.xlsx'))
    #
    #
    #
    #
    #
    #
    # return
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # import xlwt
    # response = HttpResponse(content_type='application/ms-excel')
    # response['Content-Disposition'] = 'attachment; filename=Proposta_%s.xls' % pregao.num_pregao
    # wb = xlwt.Workbook(encoding='utf-8')
    # ws = wb.add_sheet("Sheet1")
    # row_num = 0
    #
    # columns = [
    #     (u"Item"),
    #     (u"Material"),
    #     (u"Unidade"),
    #     (u"Quantidade"),
    #     (u"Marca"),
    #     (u"Valor"),
    # ]
    #
    # for col_num in xrange(len(columns)):
    #     ws.write(row_num, col_num, columns[col_num])
    #
    # for obj in itens:
    #     row_num += 1
    #     row = [
    #         obj.item,
    #         obj.material.nome,
    #         obj.unidade.nome,
    #         obj.quantidade,
    #         '',
    #         '',
    #     ]
    #     for col_num in xrange(len(row)):
    #         ws.write(row_num, col_num, row[col_num])
    #
    # wb.save(response)
    # return response

@login_required()
def remover_participante(request, proposta_id, situacao):
    proposta = get_object_or_404(PropostaItemPregao, pk=proposta_id)
    if situacao == u'1':
        title=u'Registrar Desclassificação'
    elif situacao == u'2':
        title=u'Registrar Desistências'

    form = RemoverParticipanteForm(request.POST or None)
    if form.is_valid():
        if situacao == u'1':
            proposta.desclassificado = True
            proposta.motivo_desclassificacao = form.cleaned_data.get('motivo')

        elif situacao == u'2':
            proposta.desistencia = True
            proposta.motivo_desistencia = form.cleaned_data.get('motivo')

        proposta.concorre = False
        proposta.save()

        historico = HistoricoPregao()
        historico.pregao = proposta.pregao
        historico.data = datetime.datetime.now()
        if situacao == u'1':
            historico.obs = u'Desclassificação do participante: %s do Item: %s. Motivo: %s' % (proposta.participante, proposta.item.item, form.cleaned_data.get('motivo'))
        elif situacao == u'2':
            historico.obs = u'Desistência do participante: %s do Item: %s. Motivo: %s' % (proposta.participante, proposta.item.item, form.cleaned_data.get('motivo'))
        historico.save()
        messages.success(request, u'Remoção feita com sucesso.')
        return HttpResponseRedirect(u'/base/lances_item/%s/' % proposta.item.id)



    return render(request, 'remover_participante.html', locals(), RequestContext(request))

@login_required()
def adicionar_por_discricionaridade(request, proposta_id):
    proposta = get_object_or_404(PropostaItemPregao, pk=proposta_id)
    proposta.concorre = True
    proposta.save()
    messages.success(request, u'Participante adicionado.')
    return HttpResponseRedirect(u'/base/lances_item/%s/?filtrar=1&incluido=1' % proposta.item.id)

@login_required()
def gerar_resultado(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    item.gerar_resultado()
    messages.success(request, u'Resultados gerados com sucesso.')
    return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % item.get_licitacao().id)


@login_required()
def resultado_alterar(request, resultado_id, situacao):
    title=u'Alterar Situação de Fornecedor'
    resultado = get_object_or_404(ResultadoItemPregao, pk=resultado_id)
    form = ResultadoObsForm(request.POST or None, instance=resultado)
    if form.is_valid():
        if situacao ==u'1':
            resultado.situacao = ResultadoItemPregao.INABILITADO

        elif situacao == u'2':
            resultado.situacao = ResultadoItemPregao.DESCLASSIFICADO
        elif situacao == u'3':
            resultado.situacao = ResultadoItemPregao.CLASSIFICADO
        form.save()

        historico = HistoricoPregao()
        historico.pregao = resultado.item.get_licitacao()
        historico.data = datetime.datetime.now()
        if situacao == u'1':
            historico.obs = u'Inabilitação do participante: %s do Item: %s. Motivo: %s' % (resultado.participante, resultado.item.item, form.cleaned_data.get('observacoes'))
        elif situacao == u'2':
            historico.obs = u'Desclassificação do participante: %s do Item: %s. Motivo: %s' % (resultado.participante, resultado.item.item, form.cleaned_data.get('observacoes'))
        elif situacao == u'3':
            historico.obs = u'Classificação do participante: %s do Item: %s. Motivo: %s' % (resultado.participante, resultado.item.item, form.cleaned_data.get('observacoes'))
        historico.save()
        messages.success(request, u'Situação alterada com sucesso.')
        return HttpResponseRedirect(u'/base/resultado_classificacao/%s/' % resultado.item.id)
    return render(request, 'resultado_alterar.html', locals(), RequestContext(request))

@login_required()
def resultado_alterar_todos(request, pregao_id, participante_id, situacao):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    participante = get_object_or_404(ParticipantePregao, pk=participante_id)
    title=u'Alterar Participante'
    form = RemoverParticipanteForm(request.POST or None)
    if form.is_valid():
        if situacao ==u'1':
            ResultadoItemPregao.objects.filter(item__solicitacao=pregao.solicitacao, participante=participante).update(situacao=ResultadoItemPregao.INABILITADO, observacoes=form.cleaned_data.get('motivo'))

        elif situacao == u'2':
            ResultadoItemPregao.objects.filter(item__solicitacao=pregao.solicitacao, participante=participante).update(situacao=ResultadoItemPregao.DESCLASSIFICADO, observacoes=form.cleaned_data.get('motivo'))

        historico = HistoricoPregao()
        historico.pregao = pregao
        historico.data = datetime.datetime.now()
        if situacao == u'1':
            historico.obs = u'Inabilitação do participante: %s de todos os itens. Motivo: %s' % (participante, form.cleaned_data.get('motivo'))
        elif situacao == u'2':
            historico.obs = u'Desclassificação do participante: %s de todos os itens. Motivo: %s' % (participante, form.cleaned_data.get('motivo'))

        historico.save()
        return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % pregao.id)
    return render(request, 'encerrar_pregao.html', locals(), RequestContext(request))


@login_required()
def resultado_ajustar_preco(request, resultado_id):
    title=u'Ajustar Preço de Fornecedor'
    resultado = get_object_or_404(ResultadoItemPregao, pk=resultado_id)
    form = ResultadoAjustePrecoForm(request.POST or None, instance=resultado)
    if form.is_valid():
        form.save()
        if resultado.item.get_licitacao().eh_pregao():
            messages.success(request, u'Situação alterada com sucesso.')
            return HttpResponseRedirect(u'/base/resultado_classificacao/%s/' % resultado.item.id)
        else:
            PropostaItemPregao.objects.filter(item=resultado.item, participante=resultado.participante, marca=resultado.marca).update(valor=resultado.valor)
            return HttpResponseRedirect(u'/base/gerar_resultado_licitacao/%s/' % resultado.item.get_licitacao().id)
    return render(request, 'resultado_ajustar_preco.html', locals(), RequestContext(request))

@login_required()
def desempatar_item(request, item_id):
    title=u'Desempatar Item'
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    resultados = ResultadoItemPregao.objects.filter(item=item, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')

    return render(request, 'desempatar_item.html', locals(), RequestContext(request))

@login_required()
def definir_colocacao(request, resultado_id):
    resultado = get_object_or_404(ResultadoItemPregao, pk=resultado_id)
    form = DefinirColocacaoForm(request.POST or None, instance=resultado)
    if form.is_valid():
        o = form.save(False)
        o.empate = False
        o.save()
        messages.success(request, u'Colocação registrada com sucesso.')
        return HttpResponseRedirect(u'/base/desempatar_item/%s/' % resultado.item.id)
    return render(request, 'definir_colocacao.html', locals(), RequestContext(request))

@login_required()
def movimentar_solicitacao(request, solicitacao_id, tipo):
    title=u'Enviar Solicitação'
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    if tipo ==u'3':
        form = SetorEnvioForm(request.POST or None, devolve=True)
    else:
        form = SetorEnvioForm(request.POST or None, devolve=False)
    if form.is_valid():
        if tipo ==u'3':
            solicitacao.situacao = SolicitacaoLicitacao.DEVOLVIDO
            solicitacao.setor_atual = solicitacao.setor_origem
        else:
            solicitacao.situacao = SolicitacaoLicitacao.ENVIADO
            solicitacao.setor_atual = form.cleaned_data.get('setor')


        solicitacao.save()
        nova_movimentacao = MovimentoSolicitacao()
        nova_movimentacao.solicitacao = solicitacao
        nova_movimentacao.setor_origem = request.user.pessoafisica.setor
        nova_movimentacao.data_envio = datetime.datetime.now()
        nova_movimentacao.enviado_por = request.user
        nova_movimentacao.setor_destino = form.cleaned_data.get('setor')
        nova_movimentacao.obs = form.cleaned_data.get('obs')
        nova_movimentacao.save()
        messages.success(request, u'Solicitação enviada com sucesso.')
        return HttpResponseRedirect(u'/base/ver_solicitacoes/')
    return render(request, 'movimentar_solicitacao.html', locals(), RequestContext(request))


@login_required()
def cadastrar_anexo_pregao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title=u'Cadastrar Anexo - %s' % pregao
    form = AnexoPregaoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        o = form.save(False)
        o.pregao = pregao
        o.cadastrado_por = request.user
        o.cadastrado_em = datetime.datetime.now()
        o.save()
        messages.success(request, u'Anexo cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#anexos' % pregao.id)

    return render(request, 'cadastrar_anexo_pregao.html', locals(), RequestContext(request))

@login_required()
def cadastrar_anexo_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    title=u'Cadastrar Anexo - %s' % contrato
    form = AnexoContratoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        o = form.save(False)
        o.contrato = contrato
        o.cadastrado_por = request.user
        o.cadastrado_em = datetime.datetime.now()
        o.save()
        messages.success(request, u'Anexo cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/visualizar_contrato/%s/#anexos' % contrato.id)

    return render(request, 'cadastrar_anexo_contrato.html', locals(), RequestContext(request))

@login_required()
def cadastrar_contrato(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    pregao = solicitacao.get_pregao()

    if not pregao.eh_ata_registro_preco:
        title=u'Cadastrar Contrato'
    else:
        title=u'Cadastrar Ata de Registro de Preço'

    form = ContratoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        o = form.save(False)
        o.solicitacao = solicitacao
        o.pregao = pregao
        o.valor = pregao.get_valor_total()
        o.save()
        messages.success(request, u'Cadastrado realizado com sucesso.')
        return HttpResponseRedirect(u'/base/visualizar_contrato/%s/' % o.id)

    return render(request, 'cadastrar_contrato.html', locals(), RequestContext(request))

def baixar_arquivo(request, arquivo_id):
    title=u'Baixar Arquivo'
    arquivo = get_object_or_404(AnexoPregao, pk=arquivo_id)
    form = LogDownloadArquivoForm(request.POST or None)
    if form.is_valid():
        o = form.save(False)
        o.arquivo = arquivo
        o.save()
        return HttpResponseRedirect(u'/media/%s' % arquivo.arquivo)
    return render(request, 'baixar_arquivo.html', locals(), RequestContext(request))

@login_required()
def alterar_valor_lance(request, lance_id):
    lance = get_object_or_404(LanceItemRodadaPregao, pk=lance_id)
    form = AlteraLanceForm(request.POST or None, instance=lance)
    if form.is_valid():
        rodada_atual = lance.item.get_rodada_atual()
        participante = lance.participante
        item = lance.item
        rodada_anterior = int(rodada_atual.rodada) - 1
        if int(rodada_atual.rodada) == 1 and form.cleaned_data.get('valor') >= PropostaItemPregao.objects.get(item=item, participante=participante).valor:
            messages.error(request, u'Você não pode dar uma lance maior do que sua proposta.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

        if int(rodada_atual.rodada) > 1 and form.cleaned_data.get('valor') >= LanceItemRodadaPregao.objects.get(item=item, participante=participante, rodada__rodada=rodada_anterior).valor:
            messages.error(request, u'Você não pode dar uma lance maior do que o lance da rodada anterior.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

        if form.cleaned_data.get('valor') >= item.valor_medio:
            messages.error(request, u'Você não pode dar uma lance maior do que o valor máximo do item.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

        if LanceItemRodadaPregao.objects.filter(item=item, valor=form.cleaned_data.get('valor')):
            messages.error(request, u'Este lance já foi dado.')
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)



        form.save()
        messages.success(request, u'Lance alterado com sucesso.')
        return HttpResponseRedirect(u'/base/lances_item/%s/' % lance.item.id)
    return render(request, 'alterar_valor_lance.html', locals(), RequestContext(request))

@login_required()
def avancar_proximo_item(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    if item.tem_empate_beneficio():
        messages.error(request, u'Este item tem um empate.')
        return HttpResponseRedirect(u'/base/lances_item/%s/?empate=True' % item.id)
    else:
        if item.eh_ativo():
            item.gerar_resultado()
        #item.ativo=False
        #item.save()
        if request.GET.get('ultimo'):
            return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % item.get_licitacao().id)
        else:
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.tem_proximo_item())


@login_required()
def cancelar_rodada(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    rodada = item.get_rodada_atual()
    LanceItemRodadaPregao.objects.filter(rodada=rodada, item=item).delete()
    rodada_anterior = rodada.get_rodada_anterior()
    if rodada_anterior:
        rodada_anterior.atual=True
        rodada_anterior.save()
    rodada.delete()
    messages.success(request, u'Rodada cancelada.')
    return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)

@login_required()
def editar_proposta(request, proposta_id):
    proposta = get_object_or_404(PropostaItemPregao, pk=proposta_id)
    form = EditarPropostaForm(request.POST or None, instance=proposta)
    if form.is_valid():
        form.save()
        messages.success(request, u'Item da proposta atualizada com sucesso.')
        return HttpResponseRedirect(u'/base/cadastra_proposta_pregao/%s/?participante=%s' % (proposta.pregao.id, proposta.participante.id))

    return render(request, 'editar_proposta.html', locals(), RequestContext(request))

@login_required()
def encerrar_pregao(request, pregao_id, motivo):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title=u'Alterar Situação - %s' % pregao
    form = EncerrarPregaoForm(request.POST or None, instance=pregao)
    if form.is_valid():
        o = form.save(False)
        if motivo == u'1':
            o.situacao = Pregao.DESERTO
        elif motivo == u'2':
            o.situacao = Pregao.FRACASSADO
        o.save()
        historico = HistoricoPregao()
        historico.pregao = pregao
        historico.data = datetime.datetime.now()
        if motivo == u'1':
            historico.obs = u'Pregão Deserto. Observações: %s' %  form.cleaned_data.get('obs')
        elif motivo == u'2':
            historico.obs = u'Pregão Fracassado. Observações: %s' %  form.cleaned_data.get('obs')
        historico.save()
        messages.success(request, u'Pregão atualizado com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#fornecedores' % pregao.id)

    return render(request, 'encerrar_pregao.html', locals(), RequestContext(request))

@login_required()
def encerrar_itempregao(request, item_id, motivo, origem):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    title=u'Alterar Situação do Item %s' % item
    form = EncerrarItemPregaoForm(request.POST or None, instance=item)
    if form.is_valid():
        o = form.save(False)
        if motivo == u'1':
            o.situacao = ItemSolicitacaoLicitacao.DESERTO
            historico = HistoricoPregao()
            historico.pregao = item.get_licitacao()
            historico.data = datetime.datetime.now()
            historico.obs = u'Item Deserto: %s. Motivo: %s' % (item, form.cleaned_data.get('obs'))
            historico.save()
        elif motivo == u'2':
            o.situacao = ItemSolicitacaoLicitacao.FRACASSADO
            historico = HistoricoPregao()
            historico.pregao = item.get_licitacao()
            historico.data = datetime.datetime.now()
            historico.obs = u'Item Fracassado: %s. Motivo: %s' % (item, form.cleaned_data.get('obs'))
            historico.save()
        o.save()
        messages.success(request, u'Item atualizado com sucesso.')
        if origem ==u'1':
            return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)
        else:
            return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % item.get_licitacao().id)


    return render(request, 'encerrar_pregao.html', locals(), RequestContext(request))

@login_required()
def suspender_pregao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title=u'Suspender - %s' % pregao
    if 'retomar' in request.GET:
        pregao.situacao = Pregao.CADASTRADO
        pregao.save()
        registro = HistoricoPregao()
        registro.data =datetime.datetime.now()
        registro.obs = u'Pregão Retomado'
        registro.pregao = pregao
        registro.save()
        messages.success(request, u'Pregão retomado com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#fornecedores' % pregao.id)

    form = RemoverParticipanteForm(request.POST or None)
    if form.is_valid():
        registro = HistoricoPregao()
        registro.data =datetime.datetime.now()
        registro.obs = form.cleaned_data.get('motivo')
        registro.pregao = pregao
        registro.save()
        pregao.situacao = Pregao.SUSPENSO
        pregao.save()

        messages.success(request, u'Pregão suspenso com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#fornecedores' % pregao.id)

    return render(request, 'encerrar_pregao.html', locals(), RequestContext(request))


@login_required()
def prazo_pesquisa_mercadologica(request, solicitacao_id):
    title=u'Prazo de recebimento de pesquisas'
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    if solicitacao.prazo_aberto:
        solicitacao.prazo_aberto = False
        solicitacao.save()
        messages.success(request, u'Período para recebimento de pesquisa fechado com sucesso.')
    else:
        solicitacao.prazo_aberto = True
        solicitacao.save()
        messages.success(request, u'Período para recebimento de pesquisa aberto com sucesso.')

    return HttpResponseRedirect(u'/base/itens_solicitacao/%s' % solicitacao.id)

    return render(request, 'encerrar_pregao.html', locals(), RequestContext(request))

@login_required()
def modelo_memorando(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    texto = u'teste de geracao de doc<br><br>Solicitação: %s <br>Objetivo: %s<br>Justificativa: %s' % (solicitacao, solicitacao.objetivo, solicitacao.justificativa)
    response = HttpResponse(texto, content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'attachment; filename=file.doc'
    return response


@login_required()
def receber_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    movimento = MovimentoSolicitacao.objects.filter(solicitacao=solicitacao, data_recebimento__isnull=True)
    if movimento.exists():
        atualiza_registro = MovimentoSolicitacao.objects.get(id=movimento[0].id)
        atualiza_registro.data_recebimento = datetime.datetime.now()
        atualiza_registro.recebido_por = request.user
        atualiza_registro.setor_destino = request.user.pessoafisica.setor
        atualiza_registro.save()
        if atualiza_registro.setor_destino == solicitacao.setor_origem:
            solicitacao.situacao = SolicitacaoLicitacao.CADASTRADO
        else:
            solicitacao.situacao = SolicitacaoLicitacao.RECEBIDO
        solicitacao.save()
    messages.success(request, u'Solicitação recebida com sucesso.')
    return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)

@login_required()
def ver_movimentacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Movimentação - %s' % solicitacao
    movimentos = MovimentoSolicitacao.objects.filter(solicitacao=solicitacao).order_by('-data_envio')
    return render(request, 'ver_movimentacao.html', locals(), RequestContext(request))

@login_required()
def cadastrar_minuta(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Cadastrar Minuta - %s' % solicitacao
    form = CadastroMinutaForm(request.POST or None, request.FILES or None, instance=solicitacao)
    if form.is_valid():
        form.save()
        messages.success(request, u'Minuta cadastrada com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)
    return render(request, 'cadastrar_minuta.html', locals(), RequestContext(request))


@login_required()
def avalia_minuta(request, solicitacao_id, tipo):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Avaliar Minuta -  %s' % solicitacao
    form = ObsForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        if tipo == u'1':
            solicitacao.minuta_aprovada = True
        elif tipo == u'2':
            solicitacao.minuta_aprovada = True
        solicitacao.data_avaliacao_minuta = datetime.datetime.now()
        solicitacao.minuta_avaliada_por = request.user
        solicitacao.obs_avaliacao_minuta = form.cleaned_data.get('obs')
        solicitacao.arquivo_parecer_minuta = form.cleaned_data.get('arquivo')
        solicitacao.save()
        messages.success(request, u'Minuta avaliada com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)
    return render(request, 'cadastrar_anexo_pregao.html', locals(), RequestContext(request))

@login_required()
def retomar_lances(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    item.ativo=True
    item.save()
    messages.success(request, u'Lances retomados com sucesso.')
    return HttpResponseRedirect(u'/base/lances_item/%s/' % item.id)


@login_required()
def informar_quantidades(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Informar quantidade dos itens - %s' % solicitacao
    itens = ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao).order_by('item')

    if request.POST:
        ItemQuantidadeSecretaria.objects.filter(secretaria = request.user.pessoafisica.setor.secretaria, solicitacao = solicitacao).delete()
        for idx, item in enumerate(request.POST.getlist('quantidade'), 1):
            if item:
                item_do_pregao = ItemSolicitacaoLicitacao.objects.get(solicitacao=solicitacao, id=request.POST.getlist('id_item')[idx-1])
                novo_preco = ItemQuantidadeSecretaria()
                novo_preco.solicitacao = solicitacao
                novo_preco.item = item_do_pregao
                novo_preco.secretaria = request.user.pessoafisica.setor.secretaria
                novo_preco.quantidade = request.POST.getlist('quantidade')[idx-1]
                novo_preco.save()

        messages.success(request, u'Quantidades cadastradas com sucesso. Faça o upload do memorando de solicitação.')
        return HttpResponseRedirect(u'/base/lista_documentos/%s/' % solicitacao.id)

    return render(request, 'informar_quantidades.html', locals(), RequestContext(request))

@login_required()
def ver_pedidos_secretaria(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    solicitacao = item.solicitacao
    title = u'Pedidos das Secretarias - %s' % item
    pedidos = ItemQuantidadeSecretaria.objects.filter(item=item)

    tem_pendente = pedidos.filter(avaliado_em__isnull=True).exists()
    total = pedidos.aggregate(total=Sum('quantidade'))
    pode_avaliar = request.user.groups.filter(name=u'Secretaria').exists() and solicitacao.pode_enviar_para_compra()  and solicitacao.setor_origem == request.user.pessoafisica.setor
    return render(request, 'ver_pedidos_secretaria.html', locals(), RequestContext(request))


@login_required()
def importar_itens(request, solicitacao_id):
    unidades = TipoUnidade.objects.all()
    texto=u''
    for item in unidades:
        texto = texto + item.nome +', '
    texto = texto[:-2]
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Importar Itens para a Solicitação N°: %s' % solicitacao
    form = ImportarItensForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        arquivo_up = form.cleaned_data.get('arquivo')
        if arquivo_up:
            sheet = None
            try:
                workbook = xlrd.open_workbook(file_contents=arquivo_up.read())
                sheet = workbook.sheet_by_index(0)
                ItemSolicitacaoLicitacao.objects.filter(solicitacao=solicitacao).delete()
            except XLRDError:
                raise Exception(u'Não foi possível processar a planilha. Verfique se o formato do arquivo é .xls ou .xlsx.')

            for row in range(3, sheet.nrows):

                #codigo = unicode(sheet.cell_value(row, 0)).strip()
                especificacao = unicode(sheet.cell_value(row, 0)).strip()
                unidade = unicode(sheet.cell_value(row, 1)).strip()
                qtd = unicode(sheet.cell_value(row, 2)).strip()
                if row == 3:
                    if especificacao != u'ESPECIFICAÇÃO DO PRODUTO' or unidade != u'UNIDADE' or qtd != u'QUANTIDADE':
                        raise Exception(u'Não foi possível processar a planilha. As colunas devem ter Especificação, Unidade e Quantidade.')
                else:
                    if especificacao and unidade and qtd:
                        if TipoUnidade.objects.filter(nome=unidade).exists():
                            un = TipoUnidade.objects.filter(nome=unidade)[0]
                        else:
                            un = TipoUnidade.objects.get_or_create(nome=unidade)[0]
                        novo_item = ItemSolicitacaoLicitacao()
                        novo_item.solicitacao = solicitacao
                        novo_item.item = solicitacao.get_proximo_item()

                        if MaterialConsumo.objects.filter(nome=sheet.cell_value(row, 0)).exists():
                            material = MaterialConsumo.objects.filter(nome=sheet.cell_value(row, 0))[0]
                        else:
                            material = MaterialConsumo()
                            if MaterialConsumo.objects.exists():
                                id = MaterialConsumo.objects.latest('id')
                                material.id = id.pk+1
                                material.codigo = id.pk+1
                            else:
                                material.id = 1
                                material.codigo = 1
                            material.nome = especificacao
                            material.save()
                        novo_item.material = material
                        novo_item.unidade = un
                        novo_item.quantidade = int(sheet.cell_value(row, 2))
                        novo_item.save()

                        novo_item_qtd = ItemQuantidadeSecretaria()
                        novo_item_qtd.solicitacao = solicitacao
                        novo_item_qtd.item = novo_item
                        novo_item_qtd.secretaria = request.user.pessoafisica.setor.secretaria
                        novo_item_qtd.quantidade = novo_item.quantidade
                        novo_item_qtd.aprovado = True
                        novo_item_qtd.avaliado_por = request.user
                        novo_item_qtd.avaliado_em = datetime.datetime.now()
                        novo_item_qtd.save()


        messages.success(request, u'Itens cadastrados com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)

    return render(request, 'importar_itens.html', locals(), RequestContext(request))


@login_required()
def upload_itens_pesquisa_mercadologica(request, pesquisa_id):

    pesquisa = get_object_or_404(PesquisaMercadologica, pk=pesquisa_id)
    title=u'Importar Pesquisa - %s' % pesquisa.solicitacao
    form = ImportarItensForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        arquivo_up = form.cleaned_data.get('arquivo')
        if arquivo_up:
            sheet = None
            try:
                workbook = xlrd.open_workbook(file_contents=arquivo_up.read())
                sheet = workbook.sheet_by_index(0)
                ItemPesquisaMercadologica.objects.filter(pesquisa=pesquisa).delete()
            except XLRDError:
                raise Exception(u'Não foi possível processar a planilha. Verfique se o formato do arquivo é .xls ou .xlsx.')

            for row in range(0, sheet.nrows):
                item = unicode(sheet.cell_value(row, 0)).strip()
                especificacao = unicode(sheet.cell_value(row, 1)).strip()
                unidade = unicode(sheet.cell_value(row, 2)).strip()
                marca = unicode(sheet.cell_value(row, 3)).strip()
                valor = unicode(sheet.cell_value(row, 4)).strip()
                if row == 0:
                    if item!= u'Item' or especificacao != u'Material' or unidade != u'Unidade' or marca != u'Marca' or valor!=u'Valor Unitario':
                        raise Exception(u'Não foi possível processar a planilha. As colunas devem ter Item, Material, Unidade e Marca e Valor Unitario.')
                else:
                    if item and especificacao and unidade and marca and valor:
                        item_do_pregao = ItemSolicitacaoLicitacao.objects.get(solicitacao=pesquisa.solicitacao, item=int(sheet.cell_value(row, 0)))
                        novo_preco = ItemPesquisaMercadologica()
                        novo_preco.pesquisa = pesquisa
                        novo_preco.item = item_do_pregao
                        novo_preco.valor_maximo = valor
                        novo_preco.marca = marca
                        novo_preco.save()


        messages.success(request, u'Itens cadastrados com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % pesquisa.solicitacao.id)

    return render(request, 'upload_itens_pesquisa_mercadologica.html', locals(), RequestContext(request))

@login_required()
def relatorio_resultado_final(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)
    eh_lote = pregao.criterio.id == CriterioPregao.LOTE
    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    eh_maior_desconto = pregao.tipo.id == TipoPregao.DESCONTO

    if eh_lote:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO]).order_by('item')
    total = 0
    for item in itens_pregao:
        if item.get_total_lance_ganhador():
            total = total + item.get_total_lance_ganhador()
    observacao = False
    if not pregao.eh_pregao() and ResultadoItemPregao.objects.filter(item__in=itens_pregao.values_list('id', flat=True), observacoes__isnull=False, ordem=1).exists():
        observacao = ResultadoItemPregao.objects.filter(item__in=itens_pregao.values_list('id', flat=True), observacoes__isnull=False, ordem=1)[0].observacoes
    data = {'eh_lote':eh_lote, 'observacao': observacao,  'eh_maior_desconto': eh_maior_desconto, 'configuracao':configuracao, 'logo':logo, 'itens_pregao': itens_pregao, 'data_emissao':data_emissao, 'pregao':pregao, 'total': total}

    template = get_template('relatorio_resultado_final.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def relatorio_resultado_final_por_vencedor(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)
    eh_lote = pregao.criterio.id == CriterioPregao.LOTE

    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    eh_maior_desconto = pregao.tipo.id == TipoPregao.DESCONTO
    tabela = {}
    total = {}

    if eh_lote:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    resultado = ResultadoItemPregao.objects.filter(item__solicitacao=pregao.solicitacao, situacao=ResultadoItemPregao.CLASSIFICADO)
    chaves =  resultado.values('participante__fornecedor').order_by('participante__fornecedor').distinct('participante__fornecedor')
    for num in chaves:
        fornecedor = get_object_or_404(Fornecedor, pk=num['participante__fornecedor'])
        chave = u'%s' % fornecedor
        tabela[chave] = dict(lance = list(), total = 0)

    for item in itens_pregao.order_by('item'):
        if item.get_vencedor():
            chave = u'%s' % item.get_vencedor().participante.fornecedor
            tabela[chave]['lance'].append(item)
            valor = tabela[chave]['total']
            valor = valor + item.get_total_lance_ganhador()
            tabela[chave]['total'] = valor



    resultado = collections.OrderedDict(sorted(tabela.items()))

    data = {'eh_lote':eh_lote, 'eh_maior_desconto':eh_maior_desconto, 'configuracao':configuracao, 'logo':logo, 'itens_pregao': itens_pregao, 'data_emissao':data_emissao, 'pregao':pregao, 'resultado':resultado}

    template = get_template('relatorio_resultado_final_por_vencedor.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def relatorio_lista_participantes(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)

    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    participantes = ParticipantePregao.objects.filter(pregao=pregao)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    data = {'participantes': participantes, 'configuracao':configuracao, 'logo':logo, 'data_emissao':data_emissao, 'pregao':pregao}

    template = get_template('relatorio_lista_participantes.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def relatorio_classificacao_por_item(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)
    eh_lote = pregao.criterio.id == CriterioPregao.LOTE
    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    eh_maior_desconto = pregao.tipo.id == TipoPregao.DESCONTO
    tabela = {}
    itens = {}
    resultado = ResultadoItemPregao.objects.filter(item__solicitacao=pregao.solicitacao, item__situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    chaves =  resultado.values('item__item').order_by('item')
    for num in chaves:
        chave = '%s' % num['item__item']
        tabela[chave] = []
        itens[chave] =  []

    for item in resultado.order_by('item','ordem'):
        chave = '%s' % str(item.item.item)
        tabela[chave].append(item)
        itens[chave] = item.item.get_itens_do_lote()



    resultado = collections.OrderedDict(sorted(tabela.items()))

    data = {'itens':itens, 'eh_maior_desconto': eh_maior_desconto, 'configuracao':configuracao, 'logo':logo, 'eh_lote':eh_lote, 'data_emissao':data_emissao, 'pregao':pregao, 'resultado':resultado}

    template = get_template('relatorio_classificacao_por_item.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


@login_required()
def relatorio_ocorrencias(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)

    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    registros = HistoricoPregao.objects.filter(pregao=pregao)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    data = {'registros': registros, 'configuracao':configuracao, 'logo':logo, 'data_emissao':data_emissao, 'pregao':pregao}

    template = get_template('relatorio_ocorrencias.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')



@login_required()
def relatorio_lances_item(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)
    eh_lote = pregao.criterio.id == CriterioPregao.LOTE
    destino_arquivo = u'upload/resultados/%s.pdf' % pregao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/resultados')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/resultados'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()

    tabela = {}
    itens = {}


    for item in ItemSolicitacaoLicitacao.objects.filter(solicitacao = pregao.solicitacao, lanceitemrodadapregao__isnull=False).order_by('item'):
        lista_rodadas = dict()
        rodadas = RodadaPregao.objects.filter(item=item)
        for rodada in rodadas:
            lista_rodadas[rodada.rodada] = dict(lances=list())
        chave = u'%s' % (item)
        tabela[chave] =  lista_rodadas
        itens[chave] =  item.get_itens_do_lote()

        for lance in LanceItemRodadaPregao.objects.filter(item=item).order_by('ordem_lance'):
            lista_rodadas[lance.rodada.rodada]['lances'].append(lance)

        # num_rodadas =  rodadas.values('rodada').order_by('rodada').distinct('rodada')
        # for num in num_rodadas:
        #     chave = '%s' % num['rodada']
        #     tabela[chave] = []
        # for lance in lances.order_by('id'):
        #     chave = '%s' % str(lance.rodada.rodada)
        #     tabela[chave].append(lance)


    resultado = collections.OrderedDict(sorted(tabela.items()))

    itens = collections.OrderedDict(sorted(itens.items()))



    data = {'eh_lote':eh_lote, 'itens':itens, 'data_emissao':data_emissao, 'pregao':pregao, 'resultado':resultado, 'configuracao': configuracao, 'logo': logo}


    template = get_template('relatorio_lances_item.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def relatorio_ata_registro_preco(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    eh_lote = pregao.criterio.id == CriterioPregao.LOTE
    tabela = {}
    total = {}

    if eh_lote:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    resultado = ResultadoItemPregao.objects.filter(item__solicitacao=pregao.solicitacao)
    chaves =  resultado.values('participante').order_by('participante')
    for num in chaves:
        participante = get_object_or_404(ParticipantePregao, pk=num['participante'])
        chave = u'%s' % participante.id
        tabela[chave] = dict(lance = list(), total = 0)

    for item in itens_pregao.order_by('item'):
        if item.get_vencedor():
            chave = u'%s' % item.get_vencedor().participante.id
            tabela[chave]['lance'].append(item)
            valor = tabela[chave]['total']
            valor = valor + item.get_total_lance_ganhador()
            tabela[chave]['total'] = valor



    resultado = collections.OrderedDict(sorted(tabela.items()))

    texto = u''

    for key, lances in resultado.items():

        if lances['lance']:
            fornecedor = get_object_or_404(ParticipantePregao, pk=key)

            dados = u'''<br><br>
              <table>
                <tr>
                    <td colspan=2>%s</td>
                </tr>
                <tr>
                    <td colspan=2>Endereço: %s</td>
                </tr>
                <tr>
                    <td colspan=2>CPF/CNPJ: %s</td>
                </tr>

                <tr>
                    <td>Representante Legal: %s</td>
                    <td>CPF: %s</td>
                </tr>

            </table>
            <br><br>
            ''' % (fornecedor.fornecedor.razao_social, fornecedor.fornecedor.endereco, fornecedor.fornecedor.cnpj, fornecedor.nome_representante, fornecedor.cpf_representante)

            texto =  texto + unicode(dados)

            if eh_lote:
                texto = texto + u'''<table><tr><td>Lote</td><td>Itens do Lote<td>Valor Total</td></tr>'''
            else:
                texto = texto + u'''<table><tr><td>Item</td><td>Descrição</td><td>Marca</td><td>Unidade</td><td>Quantidade</td><td>Valor Unit.</td><td>Valor Total</td></tr>'''

            for lance in lances['lance']:
                total = lance.get_vencedor().valor * lance.quantidade
                if eh_lote:
                    conteudo = u''
                    for componente in lance.get_itens_do_lote():
                        conteudo += '%s<br>' % componente.material.nome

                    texto = texto + u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (lance.item, conteudo, format_money(total))
                else:
                    texto = texto + u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (lance.item, lance.material.nome, lance.get_vencedor().marca, lance.unidade, lance.quantidade, format_money(lance.get_vencedor().valor), format_money(total))

            texto = texto + u'</table>'


    response = HttpResponse(texto, content_type='application/vnd.ms-word')
    response['Content-Disposition'] = 'attachment; filename=Ata_registro_preco_pregao_%s.doc' % pregao.id
    return response



@login_required()
def gerenciar_grupos(request):
    if not request.user.is_superuser:
        messages.success(request, u'Acesso proibido.')
        return HttpResponseRedirect(u'/')

    title=u'Gerenciar Grupos do Usuário'
    form = BuscaPessoaForm(request.POST or None)
    if form.is_valid():
        pessoa = form.cleaned_data.get('pessoa')
        ids_grupos_pessoas = pessoa.user.groups.all().values_list('id', flat=True)
        grupos = Group.objects.all()
        grupos_usuario = list()
        for grupo in grupos:
            if grupo.id in ids_grupos_pessoas:
                grupos_usuario.append((grupo, 1))
            else:
                grupos_usuario.append((grupo, 2))

    return render(request, 'gerenciar_grupos.html', locals(), RequestContext(request))


@login_required()
def gerenciar_grupo_usuario(request, usuario_id, grupo_id, acao):
    if not request.user.is_superuser:
        messages.success(request, u'Acesso proibido.')
        return HttpResponseRedirect(u'/')

    usuario = get_object_or_404(User, pk=usuario_id)
    grupo = get_object_or_404(Group, pk=grupo_id)

    if acao == u'1':
        usuario.groups.add(grupo)
        messages.success(request, u'Usuário adicionado com sucesso.')

    elif acao == u'2':
        usuario.groups.remove(grupo)
        messages.success(request, u'Usuário removido com sucesso.')
    return HttpResponseRedirect(u'/base/gerenciar_grupos/')

@login_required()
def pedido_outro_interessado(request, pedido_id, opcao):
    title=u'Rejeitar Pedido'
    pedido = get_object_or_404(ItemQuantidadeSecretaria, pk=pedido_id)
    if not pedido.avaliado_em:
        if opcao == u'1':
            pedido.aprovado = True
            pedido.avaliado_em = datetime.datetime.now()
            pedido.avaliado_por = request.user
            pedido.save()
            item = pedido.item
            item.quantidade += pedido.quantidade
            item.save()
            messages.success(request, u'Pedido aprovado com sucesso.')
            return HttpResponseRedirect(u'/base/avaliar_pedidos/%s/' % pedido.item.solicitacao.id)
        else:
            form = RemoverParticipanteForm(request.POST or None)
            if form.is_valid():
                pedido.aprovado = False
                pedido.justificativa_reprovacao = form.cleaned_data.get('motivo')
                pedido.avaliado_em = datetime.datetime.now()
                pedido.avaliado_por = request.user
                pedido.save()
                messages.success(request, u'Pedido rejeitado com sucesso.')
                return HttpResponseRedirect(u'/base/avaliar_pedidos/%s/' % pedido.item.solicitacao.id)

    else:
        return HttpResponseRedirect(u'/base/avaliar_pedidos/%s/' % pedido.item.solicitacao.id)



    return render(request, 'pedido_outro_interessado.html', locals(), RequestContext(request))


@login_required()
def abrir_processo_para_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Abrir Processo - Solicitação N°: %s' % solicitacao.num_memorando
    form = AbrirProcessoForm(request.POST or None, solicitacao=solicitacao)
    if form.is_valid():
        o = form.save(False)
        o.setor_origem = solicitacao.setor_origem
        o.pessoa_cadastro = request.user
        o.save()
        solicitacao.processo = o
        solicitacao.save()
        messages.success(request, u'Processo aberto com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)
    return render(request, 'abrir_processo_para_solicitacao.html', locals(), RequestContext(request))


@login_required()
def ver_processo(request, processo_id):
    processo = get_object_or_404(Processo, pk=processo_id)
    solicitacao = SolicitacaoLicitacao.objects.filter(processo=processo)
    if solicitacao.exists():
        solicitacao = solicitacao[0]
    title=u'Processo N°: %s' % processo.numero
    return render(request, 'ver_processo.html', locals(), RequestContext(request))


@login_required()
def imprimir_capa_processo(request, processo_id):
    processo = get_object_or_404(Processo, pk=processo_id)
    # destino_arquivo = u'upload/pesquisas/rascunhos/%s.pdf' % processo_id
    # if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'rascunhos')):
    #     os.makedirs(os.path.join(settings.MEDIA_ROOT, 'rascunhos'))
    # caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    # data_emissao = datetime.date.today()
    #
    #
    # data = {'processo': processo, 'data_emissao':data_emissao}
    #
    # template = get_template('imprimir_capa_processo.html')
    #
    # html  = template.render(Context(data))
    #
    # pdf_file = open(caminho_arquivo, "w+b")
    # pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
    #         encoding='utf-8')
    # pdf_file.close()
    # file = open(caminho_arquivo, "r")
    # pdf = file.read()
    # file.close()
    # return HttpResponse(pdf, 'application/pdf')



    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename=capa_processo.pdf'

    c = canvas.Canvas(response, pagesize = (LARGURA, ALTURA))


    if Configuracao.objects.exists():
        imagem_logo = os.path.join(settings.MEDIA_ROOT, Configuracao.objects.latest('id').logo.name)
        # if imagem_logo:
        #     c.drawInlineImage(imagem_logo, 30*mm, ALTURA - 50*mm)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(50*mm, ALTURA - 42*mm, u'%s' % Configuracao.objects.latest('id').nome)

    c.setLineWidth(0.2*mm)

    # Nº DO PROTOCOLO E CÓDIGO DE BARRAS
    c.rect(LARGURA - 100*mm, ALTURA - 78*mm, 80*mm, 22*mm)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(LARGURA - 96*mm, ALTURA - 62*mm, u'Protocolo nº %s' % processo.numero)
    codbarra = I2of5(processo.numero, width=100*mm,
                     barHeight=10*mm, barWidth=0.5*mm, bearers = 0, checksum = 0)
    codbarra.drawOn(c, LARGURA - 101*mm, ALTURA - 75*mm)

    # INFORMAÇÕES SOBRE O DOCUMENTO
    c.rect(30*mm, ALTURA - 129*mm, 160*mm, 47*mm)
    c.setFont('Helvetica', 12)
    c.drawString(32*mm, ALTURA - 88*mm, u'Data: %s' % processo.data_cadastro.strftime('%d/%m/%Y'))
    #c.drawString(110*mm, ALTURA - 88*mm, u'Campus: %s' % processo.uo.setor.sigla)
    #c.drawString(32*mm, ALTURA - 95*mm, u'Interessado: %s' % processo.pessoa_interessada.nome[:55] + (processo.pessoa_interessada.nome[55:] and '...'))
    c.drawString(32*mm, ALTURA - 102*mm, u'Origem: %s' % (processo.setor_origem))
    #c.drawString(32*mm, ALTURA - 109*mm, u'Destino: %s' % (unicode(processo.tramite_set.all()[0].orgao_recebimento)))
    L = simpleSplit('Objeto: %s' % processo.objeto,'Helvetica',12,150 * mm)
    y = ALTURA - 116*mm
    for t in L:
        c.drawString(32*mm,y,t)
        y -= 5*mm

    # TRAMITAÇÃO

    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(110*mm, 158*mm, u'TRAMITAÇÃO')

    # Linhas verticais
    for h in range(30, 201, 80):
        c.line(h*mm, 20*mm, h*mm, 152*mm)

    # Linhas horizontais
    for v in range(20, 153, 12):
        c.line(30*mm, v*mm, 190*mm, v*mm)

    # Escrevendo "Data e Destino"
    c.setFont('Helvetica', 11)
    for h in range(30, 130, 80): # horizontal
        for v in range(20, 150, 12): # vertical
            c.drawString(h*mm + 2*mm, v*mm + 4*mm, u'Data: ___/___/______    Destino:')

    c.showPage()
    c.save()
    return response


@atomic
@login_required()
def criar_lote(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title= u'%s - Cadastrar Novo Lote' % pregao
    form = CriarLoteForm(request.POST or None, pregao=pregao)
    if form.is_valid():
        ids = list()
        valor_medio = Decimal(0.00)
        quantidade = 1
        for item in form.cleaned_data.get('solicitacoes'):
            ids.append(item.id)
            valor_medio += item.valor_medio


        novo_lote = ItemSolicitacaoLicitacao()
        novo_lote.solicitacao = pregao.solicitacao
        novo_lote.item = pregao.solicitacao.get_proximo_item(eh_lote=True)
        novo_lote.quantidade = quantidade
        novo_lote.valor_medio = valor_medio
        novo_lote.total = valor_medio
        novo_lote.eh_lote = True
        novo_lote.save()

        controle = 1
        for item in ids:
            solicitacao = get_object_or_404(ItemSolicitacaoLicitacao, pk=item)
            novo_item_lote = ItemLote()
            novo_item_lote.lote = novo_lote
            novo_item_lote.item = solicitacao
            novo_item_lote.numero_item = controle
            novo_item_lote.save()
            controle +=1

        messages.success(request, u'Lote criado com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#lotes' % pregao.id)


    return render(request, 'criar_lote.html', locals(), RequestContext(request))


@login_required()
def extrato_inicial(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/extratos/%s.pdf' % pregao.id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/extratos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/extratos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)


    data = {'pregao': pregao, 'configuracao': configuracao, 'logo': logo}

    template = get_template('extrato_inicial.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()


    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


@login_required()
def termo_adjudicacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/extratos/%s.pdf' % pregao.id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/extratos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/extratos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)


    tabela = {}

    eh_lote = pregao.criterio.id == CriterioPregao.LOTE

    if eh_lote:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    resultado = ResultadoItemPregao.objects.filter(ordem=1, item__solicitacao=pregao.solicitacao, situacao=ResultadoItemPregao.CLASSIFICADO)
    chaves =  resultado.values('participante__fornecedor').order_by('participante__fornecedor').distinct('participante__fornecedor')
    for num in chaves:
        fornecedor = get_object_or_404(Fornecedor, pk=num['participante__fornecedor'])
        chave = u'%s' % fornecedor
        tabela[chave] = dict(itens = list(), total = 0)
    total_geral = 0
    for item in itens_pregao.order_by('item'):

        if item.get_vencedor():
            chave = u'%s' % item.get_vencedor().participante.fornecedor
            tabela[chave]['itens'].append(item.item)
            valor = tabela[chave]['total']
            valor = valor + item.get_total_lance_ganhador()
            tabela[chave]['total'] = valor


    for item in tabela:
        total_geral = total_geral + tabela[item]['total']

    fracassados = list()
    for item in itens_pregao.filter(situacao=ItemSolicitacaoLicitacao.FRACASSADO):
        fracassados.append(item.item)

    resultado = collections.OrderedDict(sorted(tabela.items()))


    data = {'pregao': pregao, 'eh_lote': eh_lote, 'configuracao': configuracao, 'logo': logo, 'resultado': resultado, 'total_geral': total_geral, 'fracassados': fracassados}

    template = get_template('termo_adjudicacao.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()


    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')



@login_required()
def editar_meu_perfil(request, pessoa_id):
    pessoa = get_object_or_404(PessoaFisica, pk=pessoa_id)
    if pessoa.id == request.user.pessoafisica.id:
        title=u'Editar Meu Perfil'
        form = PessoaFisicaForm(request.POST or None, request=request, instance=pessoa, edicao=True)
        if form.is_valid():
            form.save()
            messages.success(request, u'Perfil editado com sucesso.')
            return HttpResponseRedirect(u'/')


    return render(request, 'editar_meu_perfil.html', locals(), RequestContext(request))


@login_required()
def editar_pedido(request, pedido_id):
    title=u'Editar Pedido'
    pedido = get_object_or_404(ItemQuantidadeSecretaria, pk=pedido_id)
    solicitacao = pedido.solicitacao
    form = EditarPedidoForm(request.POST or None, instance=pedido)
    if form.is_valid():
        form.save()
        messages.success(request, u'Perfil editado com sucesso.')
        return HttpResponseRedirect(u'/base/ver_pedidos_secretaria/%s/' % pedido.item.id)


    return render(request, 'editar_pedido.html', locals(), RequestContext(request))



@login_required()
def aprovar_todos_pedidos(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)

    total=0
    for pedido in ItemQuantidadeSecretaria.objects.filter(item=item, avaliado_em__isnull=True):
        total += pedido.quantidade
    item.quantidade += total
    item.save()
    ItemQuantidadeSecretaria.objects.filter(item=item, avaliado_em__isnull=True).update(aprovado=True, avaliado_por=request.user, avaliado_em=datetime.datetime.now())
    messages.success(request, u'Pedidos aprovados com sucesso.')
    return HttpResponseRedirect(u'/base/ver_pedidos_secretaria/%s/' % item.id)

@login_required()
def gestao_pedidos(request):
    setor = request.user.pessoafisica.setor
    title=u'Gestão de Pedidos - %s/%s' % (setor.sigla, setor.secretaria.sigla)
    meus_pedidos = ItemQuantidadeSecretaria.objects.filter(secretaria=setor.secretaria).values_list('solicitacao', flat=True)
    pregoes_finalizados = Pregao.objects.filter(solicitacao__in=meus_pedidos)
    atas_finalizadas = pregoes_finalizados.filter(eh_ata_registro_preco=True)
    contratos_finalizados = pregoes_finalizados.filter(eh_ata_registro_preco=False)
    atas = SolicitacaoLicitacao.objects.filter(liberada_compra=True, id__in=atas_finalizadas.values_list('solicitacao', flat=True))
    contratos = SolicitacaoLicitacao.objects.filter(liberada_compra=True, id__in=contratos_finalizados.values_list('solicitacao', flat=True))

    return render(request, 'gestao_pedidos.html', locals(), RequestContext(request))

@login_required()
def gestao_contratos(request):
    setor = request.user.pessoafisica.setor
    title=u'Gestão de Contratos - %s/%s' % (setor.sigla, setor.secretaria.sigla)
    solicitacoes = SolicitacaoLicitacao.objects.filter(setor_origem__secretaria=setor.secretaria)
    atas_finalizadas = Pregao.objects.filter(eh_ata_registro_preco=True, solicitacao__in=solicitacoes.values_list('id', flat=True))
    contratos_finalizados = Pregao.objects.filter(eh_ata_registro_preco=False, solicitacao__in=solicitacoes.values_list('id', flat=True))
    atas = Contrato.objects.filter(solicitacao__in=atas_finalizadas.values_list('solicitacao', flat=True))
    contratos = Contrato.objects.filter(solicitacao__in=contratos_finalizados.values_list('solicitacao', flat=True))

    return render(request, 'gestao_contratos.html', locals(), RequestContext(request))


@login_required()
def avaliar_pedidos(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title=u'Avaliar Pedidos - %s' % solicitacao
    tabela = {}
    pode_avaliar = request.user.groups.filter(name=u'Secretaria').exists() and solicitacao.pode_enviar_para_compra()  and solicitacao.setor_origem == request.user.pessoafisica.setor
    pedidos = ItemQuantidadeSecretaria.objects.filter(solicitacao=solicitacao)

    form = FiltrarSecretariaForm(request.POST or None, pedidos=pedidos)
    if request.GET.get('secretaria'):
        pedidos = pedidos.filter(secretaria=request.GET.get('secretaria'))
    chaves =  pedidos.values('secretaria').order_by('secretaria').distinct('secretaria')
    for num in chaves:
        secretaria = get_object_or_404(Secretaria, pk=num['secretaria'])
        chave = u'%s' % secretaria.id
        pendente = pedidos.filter(secretaria=secretaria, avaliado_em__isnull=True).exists()
        tabela[chave] = dict(pedido = list(), nome=secretaria, pendente=pendente)

    for item in pedidos.order_by('item'):

        chave = u'%s' % item.secretaria.id
        tabela[chave]['pedido'].append(item)

    resultado = collections.OrderedDict(sorted(tabela.items()))
    return render(request, 'avaliar_pedidos.html', locals(), RequestContext(request))


@login_required()
def aprovar_todos_pedidos_secretaria(request, solicitacao_id, secretaria_id):
    if ItemQuantidadeSecretaria.objects.filter(solicitacao=solicitacao_id, secretaria=secretaria_id, avaliado_em__isnull=True).exists():
        for pedido in ItemQuantidadeSecretaria.objects.filter(solicitacao=solicitacao_id, secretaria=secretaria_id, avaliado_em__isnull=True):
            pedido.item.quantidade += pedido.quantidade
            pedido.item.save()
        ItemQuantidadeSecretaria.objects.filter(solicitacao=solicitacao_id, secretaria=secretaria_id, avaliado_em__isnull=True).update(aprovado=True, avaliado_por=request.user, avaliado_em=datetime.datetime.now())
        messages.success(request, u'Pedidos aprovados com sucesso.')
    return HttpResponseRedirect(u'/base/avaliar_pedidos/%s/' % solicitacao_id)


@login_required()
def novo_pedido_compra(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    pregao = solicitacao.get_pregao()
    title=u'Novo Pedido de Compra - %s' % pregao
    form = NovoPedidoCompraForm(request.POST or None)
    if form.is_valid():
        o = form.save(False)
        o.tipo = SolicitacaoLicitacao.COMPRA
        o.setor_origem = request.user.pessoafisica.setor
        o.setor_atual = request.user.pessoafisica.setor
        o.data_cadastro = datetime.datetime.now()
        o.cadastrado_por = request.user
        o.save()

        return HttpResponseRedirect(u'/base/informar_quantidades_do_pedido/%s/%s/' % (solicitacao.id, o.id))
    return render(request, 'novo_pedido_compra.html', locals(), RequestContext(request))

@login_required()
def informar_quantidades_do_pedido(request, solicitacao_original, nova_solicitacao):
    setor = request.user.pessoafisica.setor
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_original)
    nova_solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=nova_solicitacao)
    title=u'Pedido de Compra - %s' % nova_solicitacao
    participantes = solicitacao.get_resultado()
    form = FiltraVencedorPedidoForm(request.POST or None, participantes=participantes)
    eh_lote = solicitacao.eh_lote()
    if eh_lote:
        resultados = solicitacao.get_lotes()
    else:
        resultados = participantes
    buscou = False

    if form.is_valid():
        buscou = True
        if eh_lote:
            ids = list()
            for item in solicitacao.itemsolicitacaolicitacao_set.filter(eh_lote=True):
                registro = ResultadoItemPregao.objects.filter(item=item, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0]
                if registro.participante == form.cleaned_data.get('vencedor'):
                    ids.append(registro.item.id)
            resultados = resultados.filter(id__in=ids)
        else:
            resultados = solicitacao.get_resultado(vencedor=form.cleaned_data.get('vencedor'))
        fornecedor = form.cleaned_data.get('vencedor')
        if 'quantidades' in request.POST:
            fornecedor = request.POST.get('fornecedor')
            participante = ParticipantePregao.objects.get(id=fornecedor)

            if eh_lote and '0' in request.POST.getlist('quantidades'):
                messages.error(request, u'Informe a quantidade solicitada para cada item do lote')
                return HttpResponseRedirect(u'/base/informar_quantidades_do_pedido/%s/%s/' % (solicitacao.id, nova_solicitacao.id))


            if eh_lote:
                ids = list()
                resultados = solicitacao.itemsolicitacaolicitacao_set.filter(eh_lote=False)
                for item in solicitacao.itemsolicitacaolicitacao_set.filter(eh_lote=True):
                    registro = ResultadoItemPregao.objects.filter(item=item, situacao=ResultadoItemPregao.CLASSIFICADO).order_by('ordem')[0]
                    if registro.participante == participante:
                        for id_do_item in registro.item.get_itens_do_lote():
                            ids.append(id_do_item.id)
                resultados = resultados.filter(id__in=ids)

                for idx, valor in enumerate(request.POST.getlist('quantidades'), 0):
                    valor_pedido = int(valor)
                    if valor_pedido > 0:
                        if valor_pedido > resultados[idx].get_quantidade_disponivel():
                            messages.error(request, u'A quantidade disponível do item "%s" é menor do que a quantidade solicitada.' % resultados[idx])
                            return HttpResponseRedirect(u'/base/informar_quantidades_do_pedido/%s/%s/' % (solicitacao.id, nova_solicitacao.id))
            else:
                resultados = solicitacao.get_resultado(vencedor=participante)
                for idx, valor in enumerate(request.POST.getlist('quantidades'), 0):
                    valor_pedido = int(valor)
                    if valor_pedido > 0:
                        if valor_pedido > resultados[idx].item.get_quantidade_disponivel():
                            messages.error(request, u'A quantidade disponível do item "%s" é menor do que a quantidade solicitada.' % resultados[idx].item)
                            return HttpResponseRedirect(u'/base/informar_quantidades_do_pedido/%s/%s/' % (solicitacao.id, nova_solicitacao.id))

            for idx, valor in enumerate(request.POST.getlist('quantidades'), 0):
                valor_pedido = int(valor)
                if valor_pedido > 0:
                    novo_pedido = PedidoItem()
                    novo_pedido.solicitacao = nova_solicitacao
                    if eh_lote:
                        novo_pedido.item = resultados[idx]
                        novo_pedido.proposta = resultados[idx].get_proposta_item_lote()
                    else:
                        novo_pedido.item = resultados[idx].item
                        novo_pedido.resultado = resultados[idx]
                    novo_pedido.quantidade = valor_pedido
                    novo_pedido.setor = setor
                    novo_pedido.pedido_por = request.user
                    novo_pedido.pedido_em = datetime.datetime.now()
                    novo_pedido.save()

            messages.success(request, u'Pedido cadastrado com sucesso.')
            return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % nova_solicitacao.id)
    return render(request, 'informar_quantidades_do_pedido.html', locals(), RequestContext(request))

@login_required()
def apagar_anexo_pregao(request, item_id):
    anexo = get_object_or_404(AnexoPregao, pk=item_id)
    pregao = anexo.pregao
    anexo.delete()
    messages.success(request, u'Anexo removido com sucesso.')
    return HttpResponseRedirect(u'/base/pregao/%s/' % pregao.id)

@login_required()
def apagar_anexo_contrato(request, item_id):
    anexo = get_object_or_404(AnexoContrato, pk=item_id)
    contrato = anexo.contrato
    anexo.delete()
    messages.success(request, u'Anexo removido com sucesso.')
    return HttpResponseRedirect(u'/base/visualizar_contrato/%s/#anexos' % contrato.id)

@login_required()
def editar_anexo_contrato(request, item_id):
    anexo = get_object_or_404(AnexoContrato, pk=item_id)
    contrato = anexo.contrato
    title=u'Editar Anexo - %s' % contrato
    form = AnexoContratoForm(request.POST or None, request.FILES or None, instance=anexo)
    if form.is_valid():
        form.save()
        messages.success(request, u'Anexo cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/visualizar_contrato/%s/#anexos' % contrato.id)

    return render(request, 'cadastrar_anexo_contrato.html', locals(), RequestContext(request))


@login_required()
def gerar_pedido_fornecedores(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)

    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/pedidos/%s.pdf' % solicitacao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/pedidos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/pedidos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()

    pedidos = PedidoItem.objects.filter(solicitacao=solicitacao)
    eh_lote = Pregao.objects.filter(solicitacao=pedidos[0].item.solicitacao)[0].criterio == CriterioPregao.LOTE

    tabela = {}

    if eh_lote:
        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_empresa_item_lote().fornecedor
            tabela[chave] = dict(pedidos = list(), total = 0)

        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_empresa_item_lote().fornecedor
            tabela[chave]['pedidos'].append(pedido)
            valor = tabela[chave]['total']
            valor = valor + (pedido.item.get_valor_item_lote()*pedido.quantidade)
            tabela[chave]['total'] = valor

    else:
        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_vencedor().participante.fornecedor
            tabela[chave] = dict(pedidos = list(), total = 0)

        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_vencedor().participante.fornecedor
            tabela[chave]['pedidos'].append(pedido)
            valor = tabela[chave]['total']
            valor = valor + (pedido.resultado.valor*pedido.quantidade)
            tabela[chave]['total'] = valor


    resultado = collections.OrderedDict(sorted(tabela.items()))

    data = {'configuracao': configuracao, 'logo': logo, 'resultado': resultado, 'data_emissao': data_emissao, 'eh_lote': eh_lote}

    template = get_template('gerar_pedido_fornecedores.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def apagar_lote(request, item_id, pregao_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    itens_do_lote = ItemLote.objects.filter(lote=item)
    PropostaItemPregao.objects.filter(item__in=itens_do_lote.values_list('item', flat=True)).delete()
    ItemLote.objects.filter(lote=item).delete()
    item.delete()
    return HttpResponseRedirect(u'/base/pregao/%s/#lotes' % pregao_id)


@login_required()
def informar_valor_final_item_lote(request, item_id, pregao_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    lote =ItemLote.objects.filter(item=item)[0].lote.get_empresa_vencedora()
    tite=u'Informar Valor do %s - %s' % (item, lote)
    form = ValorFinalItemLoteForm(request.POST or None)
    if form.is_valid():
        PropostaItemPregao.objects.filter(participante=lote, item=item).update(valor_item_lote=form.cleaned_data.get('valor'))

        messages.success(request, u'Valor cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % pregao_id)
    return render(request, 'informar_valor_final_item_lote.html', locals(), RequestContext(request))


@login_required()
def gerar_ordem_compra(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    id_sessao = "%s_solicitacao" % (request.user.pessoafisica.id)
    request.session[id_sessao] = solicitacao.id
    title = u'Gerar Ordem de Compra/Serviço - %s' % solicitacao
    form = CriarOrdemForm(request.POST or None)
    if form.is_valid():
        o = form.save(False)
        o.solicitacao = solicitacao
        o.save()
        messages.success(request, u'Ordem de Compra/Serviço gerada com sucesso.')
        return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao_id)
    return render(request, 'gerar_ordem_compra.html', locals(), RequestContext(request))


@login_required()
def ver_ordem_compra(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)

    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/ordens_compra/%s.pdf' % solicitacao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/ordens_compra')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/ordens_compra'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    ordem = OrdemCompra.objects.get(solicitacao=solicitacao)
    pedidos = PedidoItem.objects.filter(solicitacao=solicitacao).order_by('item')
    pregao = pedidos[0].item.solicitacao.get_pregao()
    eh_lote = Pregao.objects.filter(solicitacao=pedidos[0].item.solicitacao)[0].criterio == CriterioPregao.LOTE

    tabela = {}

    if eh_lote:
        fornecedor = pedidos[0].item.get_empresa_item_lote().fornecedor
        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_empresa_item_lote().fornecedor
            tabela[chave] = dict(pedidos = list(), total = 0)

        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_empresa_item_lote().fornecedor
            tabela[chave]['pedidos'].append(pedido)
            valor = tabela[chave]['total']
            valor = valor + (pedido.item.get_valor_item_lote()*pedido.quantidade)
            tabela[chave]['total'] = valor

    else:
        fornecedor = pedidos[0].item.get_vencedor().participante.fornecedor
        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_vencedor().participante.fornecedor
            tabela[chave] = dict(pedidos = list(), total = 0)

        for pedido in pedidos:
            chave = u'%s' % pedido.item.get_vencedor().participante.fornecedor
            tabela[chave]['pedidos'].append(pedido)
            valor = tabela[chave]['total']
            valor = valor + (pedido.resultado.valor*pedido.quantidade)
            tabela[chave]['total'] = valor


    resultado = collections.OrderedDict(sorted(tabela.items()))

    data = {'solicitacao': solicitacao, 'pregao': pregao, 'configuracao': configuracao, 'logo': logo, 'fornecedor': fornecedor, 'resultado': resultado, 'data_emissao': data_emissao, 'eh_lote': eh_lote, 'ordem': ordem}

    template = get_template('ver_ordem_compra.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def ver_ordem_compra_dispensa(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)


    destino_arquivo = u'upload/ordens_compra/%s.pdf' % solicitacao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/ordens_compra')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/ordens_compra'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()
    ordem = OrdemCompra.objects.get(solicitacao=solicitacao)

    lista = list()
    dicionario = {}
    for pesquisa in PesquisaMercadologica.objects.filter(solicitacao=solicitacao):
        total = ItemPesquisaMercadologica.objects.filter(pesquisa=pesquisa, ativo=True).aggregate(soma=Sum('valor_maximo'))['soma']
        if total:
            lista.append([pesquisa.id, total])
            dicionario[pesquisa.id] = total
    resultado = sorted(dicionario.items(), key=lambda x: x[1])
    fornecedor = PesquisaMercadologica.objects.get(id=resultado[0][0])
    itens = ItemPesquisaMercadologica.objects.filter(pesquisa=resultado[0][0]).order_by('item')
    total = 0

    for item in itens:
        total += item.get_total()

    data = {'solicitacao': solicitacao, 'pregao': pregao, 'total':total, 'itens': itens, 'fornecedor': fornecedor,  'data_emissao': data_emissao, 'ordem': ordem}

    template = get_template('ver_ordem_compra_dispensa.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def registrar_adjudicacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title=u'Registrar Adjudicação'
    form = RegistrarAdjudicacaoForm(request.POST or None, instance=pregao)
    if form.is_valid():
        form.save()
        messages.success(request, u'Data de adjudicação registrada com sucesso.')
        return HttpResponseRedirect(u'/base/pregao/%s/#homologacao' % pregao.id)
    return render(request, 'cadastrar_anexo_pregao.html', locals(), RequestContext(request))

@login_required()
def registrar_homologacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title=u'Registrar Homologação'
    form = RegistrarHomologacaoForm(request.POST or None, instance=pregao)
    if form.is_valid():
        o = form.save(False)
        o.ordenador_despesa = request.user.pessoafisica
        o.situacao = Pregao.CONCLUIDO
        o.save()

        # novo_contrato = Contrato()
        # novo_contrato.solicitacao = pregao.solicitacao
        # novo_contrato.pregao = pregao
        # novo_contrato.numero = pregao.num_pregao
        # novo_contrato.valor = pregao.get_valor_total()
        # novo_contrato.data_inicio = o.data_homologacao
        # novo_contrato.save()

        messages.success(request, u'Data de homologação registrada com sucesso. Prossiga com o envio do termo assinado')
        return HttpResponseRedirect(u'/base/upload_termo_homologacao/%s/' % pregao.id)
    return render(request, 'cadastrar_anexo_pregao.html', locals(), RequestContext(request))



@login_required()
def termo_homologacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/extratos/%s.pdf' % pregao.id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/extratos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/extratos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)


    tabela = {}

    eh_lote = pregao.criterio.id == CriterioPregao.LOTE

    if eh_lote:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=True, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    else:
        itens_pregao = ItemSolicitacaoLicitacao.objects.filter(solicitacao=pregao.solicitacao, eh_lote=False, situacao__in=[ItemSolicitacaoLicitacao.CADASTRADO, ItemSolicitacaoLicitacao.CONCLUIDO])
    resultado = ResultadoItemPregao.objects.filter(ordem=1, item__solicitacao=pregao.solicitacao, situacao=ResultadoItemPregao.CLASSIFICADO)
    chaves =  resultado.values('participante__fornecedor').order_by('participante__fornecedor').distinct('participante__fornecedor')
    for num in chaves:
        fornecedor = get_object_or_404(Fornecedor, pk=num['participante__fornecedor'])
        chave = u'%s' % fornecedor
        tabela[chave] = dict(itens = list(), total = 0)
    total_geral = 0
    for item in itens_pregao.order_by('item'):

        if item.get_vencedor():
            chave = u'%s' % item.get_vencedor().participante.fornecedor
            tabela[chave]['itens'].append(item.item)
            valor = tabela[chave]['total']
            valor = valor + item.get_total_lance_ganhador()
            tabela[chave]['total'] = valor


    for item in tabela:
        total_geral = total_geral + tabela[item]['total']

    fracassados = list()
    for item in itens_pregao.filter(situacao=ItemSolicitacaoLicitacao.FRACASSADO):
        fracassados.append(item.item)

    resultado = collections.OrderedDict(sorted(tabela.items()))



    data = {'pregao': pregao, 'configuracao': configuracao, 'logo': logo, 'resultado': resultado, 'total_geral': total_geral, 'fracassados': fracassados}
    if pregao.eh_pregao():
        template = get_template('termo_homologacao.html')
    else:
        template = get_template('termo_homologacao_e_adjudicacao.html')


    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()


    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def visualizar_contrato(request, solicitacao_id):
    contrato = get_object_or_404(Contrato, pk=solicitacao_id)
    title = u'Contrato %s' % contrato.numero
    eh_ata = contrato.pregao.eh_ata_registro_preco

    return render(request, 'visualizar_contrato.html', locals(), RequestContext(request))

@login_required()
def liberar_solicitacao_contrato(request, solicitacao_id, origem):
    contrato = get_object_or_404(Contrato, pk=solicitacao_id)

    if origem == u'1':
        contrato.solicitacao.liberada_compra = True
        contrato.suspenso = False
    elif origem == u'2':
        contrato.solicitacao.liberada_compra = False
        contrato.suspenso = True
    contrato.solicitacao.save()
    contrato.save()
    return HttpResponseRedirect(u'/base/visualizar_contrato/%s/' % contrato.id)

@login_required()
def definir_vigencia_contrato(request, contrato_id):
    title=u'Definir Vigência do Contrato'
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    form = DefinirVigenciaContratoForm(request.POST or None, instance=contrato)
    if form.is_valid():
        form.save()
        messages.success(request, u'Data de Vigência registrada com sucesso.')
        return HttpResponseRedirect(u'/base/visualizar_contrato/%s/' % contrato.id)

    return render(request, 'definir_vigencia_contrato.html', locals(), RequestContext(request))

@login_required()
def aditivar_contrato(request, contrato_id):
    contrato = get_object_or_404(Contrato, pk=contrato_id)
    title=u'Aditivar Contrato'
    form = AditivarContratoForm(request.POST or None, contrato=contrato)
    if form.is_valid():
        aditivo = Aditivo()
        aditivo.data_inicio = form.cleaned_data.get('data_inicio')
        aditivo.data_fim = form.cleaned_data.get('data_fim')
        aditivo.contrato = contrato
        aditivo.ordem = contrato.get_proximo_aditivo()
        aditivo.numero = contrato.get_proximo_aditivo()
        aditivo.save()


        messages.success(request, u'Contrato aditivado com sucesso.')
        return HttpResponseRedirect(u'/base/visualizar_contrato/%s/' % contrato.id)

    return render(request, 'definir_vigencia_contrato.html', locals(), RequestContext(request))


@login_required()
def cancelar_pedido_compra(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    PedidoItem.objects.filter(solicitacao=solicitacao).update(ativo=False)
    messages.success(request, u'Solicitação cancelada com sucesso.')
    return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)


@login_required()
def lista_documentos(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    title = u'Lista de Documentos'
    documentos = DocumentoSolicitacao.objects.filter(solicitacao=solicitacao)

    return render(request, 'lista_documentos.html', locals(), RequestContext(request))


def libreoffice_new_line(tokens, align_center='', font_size=17):
    if len(tokens)>1:
        if align_center:
            align_center = '<w:jc w:val="center"/>'
        out = ['</w:t></w:r></w:p>']
        for token in tokens:
            out.append('<w:p><w:pPr><w:spacing w:after="0"/>%s</w:pPr><w:r><w:rPr><w:sz w:val="%s"/></w:rPr><w:t>%s' % (align_center, font_size, token))
            out.append('</w:t></w:r></w:p>')
        del(out[-1])
        return ''.join(out)
    return tokens[0]


@login_required()
def memorando(request, solicitacao_id):
    import tempfile
    import zipfile
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)

    municipio = None
    if get_config():
        municipio = get_config().municipio

    itens = []
    quantidades = []
    unidades  = []
    descricoes = []

    for item in solicitacao.itemsolicitacaolicitacao_set.all():
        itens.append(item)
        quantidades.append(item.quantidade)
        unidades.append(item.unidade)
        descricoes.append(item.material.nome)

    dicionario = {
        '#NUM#' : solicitacao.num_memorando,
        '#MUNICIPIO#' : municipio or u'-',
        '#DATA#': datetime.date.today(),
        '#OBJETIVO#': solicitacao.objetivo,
        '#OBJETO#': solicitacao.objeto,
        '#IT#': libreoffice_new_line(itens or '-'),
        '#QUANT#': libreoffice_new_line(quantidades or '-'),
        '#UN#': libreoffice_new_line(unidades or '-'),
        '#DES#': libreoffice_new_line(descricoes or '-'),

    }
    template_docx = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/memorando.docx'))
    new_docx = zipfile.ZipFile('%s.docx' % tempfile.mktemp(), "a")

    tmp_xml_file = open(template_docx.extract("word/document.xml", tempfile.mkdtemp()))
    tempXmlStr = tmp_xml_file.read()
    tmp_xml_file.close()
    os.unlink(tmp_xml_file.name)

    for key in dicionario.keys():
        value = unicode(dicionario.get(key)).encode("utf8")
        tempXmlStr = tempXmlStr.replace(key, value)

    tmp_xml_file =  open(tempfile.mktemp(), "w+")
    tmp_xml_file.write(tempXmlStr)
    tmp_xml_file.close()

    for arquivo in template_docx.filelist:
        if not arquivo.filename == "word/document.xml":
            new_docx.writestr(arquivo.filename, template_docx.read(arquivo))

    new_docx.write(tmp_xml_file.name, "word/document.xml")

    template_docx.close()
    new_docx.close()
    os.unlink(tmp_xml_file.name)


    # Caso não seja informado, deverá retornar o caminho para o arquivo DOCX processado.
    caminho_arquivo =  new_docx.filename
    nome_arquivo = caminho_arquivo.split('/')[-1]
    extensao = nome_arquivo.split('.')[-1]
    arquivo = open(caminho_arquivo, "rb")


    content_type = caminho_arquivo.endswith('.pdf') and 'application/pdf' or 'application/vnd.ms-word'
    response = HttpResponse(arquivo.read(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % nome_arquivo
    arquivo.close()
    os.unlink(caminho_arquivo)
    return response


@login_required()
def termo_referencia(request, solicitacao_id):
    import tempfile
    import zipfile
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)

    municipio = None
    if get_config():
        municipio = get_config().municipio

    itens = []
    quantidades = []
    unidades  = []
    descricoes = []

    for item in solicitacao.itemsolicitacaolicitacao_set.all():
        itens.append(item)
        quantidades.append(item.quantidade)
        unidades.append(item.unidade)
        descricoes.append(item.material.nome)

    dicionario = {
        '#NUM#' : solicitacao.num_memorando,
        '#MUNICIPIO#' : municipio or u'-',
        '#DATA#': datetime.date.today(),
        '#OBJETIVO#': solicitacao.objetivo,
        '#OBJETO#': solicitacao.objeto,
        '#JUST#': solicitacao.justificativa,
        '#IT#': libreoffice_new_line(itens or '-'),
        '#QUANT#': libreoffice_new_line(quantidades or '-'),
        '#UN#': libreoffice_new_line(unidades or '-'),
        '#DES#': libreoffice_new_line(descricoes or '-'),

    }
    template_docx = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, 'upload/modelos/termo_referencia.docx'))
    new_docx = zipfile.ZipFile('%s.docx' % tempfile.mktemp(), "a")

    tmp_xml_file = open(template_docx.extract("word/document.xml", tempfile.mkdtemp()))
    tempXmlStr = tmp_xml_file.read()
    tmp_xml_file.close()
    os.unlink(tmp_xml_file.name)

    for key in dicionario.keys():
        value = unicode(dicionario.get(key)).encode("utf8")
        tempXmlStr = tempXmlStr.replace(key, value)

    tmp_xml_file =  open(tempfile.mktemp(), "w+")
    tmp_xml_file.write(tempXmlStr)
    tmp_xml_file.close()

    for arquivo in template_docx.filelist:
        if not arquivo.filename == "word/document.xml":
            new_docx.writestr(arquivo.filename, template_docx.read(arquivo))

    new_docx.write(tmp_xml_file.name, "word/document.xml")

    template_docx.close()
    new_docx.close()
    os.unlink(tmp_xml_file.name)


    # Caso não seja informado, deverá retornar o caminho para o arquivo DOCX processado.
    caminho_arquivo =  new_docx.filename
    nome_arquivo = caminho_arquivo.split('/')[-1]
    extensao = nome_arquivo.split('.')[-1]
    arquivo = open(caminho_arquivo, "rb")


    content_type = caminho_arquivo.endswith('.pdf') and 'application/pdf' or 'application/vnd.ms-word'
    response = HttpResponse(arquivo.read(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % nome_arquivo
    arquivo.close()
    os.unlink(caminho_arquivo)
    return response

@login_required()
def apagar_documento(request, documento_id):
    documento = get_object_or_404(DocumentoSolicitacao, pk=documento_id)
    solicitacao = documento.solicitacao.id
    if request.user == documento.cadastrado_por:
        documento.delete()

        messages.success(request, u'Documento apagado com sucesso.')
    return HttpResponseRedirect(u'/base/lista_documentos/%s/' % solicitacao)

@login_required()
def editar_fornecedor(request, fornecedor_id):
    fornecedor = get_object_or_404(Fornecedor, pk=fornecedor_id)
    title=u'Editar Fornecedor - %s' % fornecedor
    form = FornecedorForm(request.POST or None, instance=fornecedor)
    if form.is_valid():
        form.save()
        messages.success(request, u'Fornecedor editado com sucesso.')
        return HttpResponseRedirect(u'/base/ver_fornecedores/')

    return render(request, 'editar_fornecedor.html', locals(), RequestContext(request))

@login_required()
def cadastrar_fornecedor(request, opcao):
    title=u'Cadastrar Fornecedor'
    form = FornecedorForm(request.POST or None)
    if form.is_valid():
        form.save()

        messages.success(request, u'Fornecedor cadastrado com sucesso.')
        if opcao == u'0':
            return HttpResponseRedirect(u'/base/ver_fornecedores/')
        else:
            return HttpResponseRedirect(u'/base/cadastra_participante_pregao/%s/' % int(opcao))


    return render(request, 'editar_fornecedor.html', locals(), RequestContext(request))


@login_required()
def remover_participante_pregao(request, participante_id):
    participante = get_object_or_404(ParticipantePregao, pk=participante_id)
    pregao = participante.pregao.id
    participante.delete()
    messages.success(request, u'Participante removido com sucesso.')
    return HttpResponseRedirect(u'/base/pregao/%s/' % pregao)

@login_required()
def editar_pregao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    title = u'Editar %s' % pregao.modalidade
    form = PregaoForm(request.POST or None, instance=pregao)
    if form.is_valid():
        form.save()
        messages.success(request, u'Licitação editada com sucesso.')
        return HttpResponseRedirect(u'/base/ver_pregoes/')

    return render(request, 'editar_pregao.html', locals(), RequestContext(request))

@login_required()
def upload_termo_homologacao(request, pregao_id):
    title=u'Enviar Termo de Homologação'
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    form = UploadTermoHomologacaoForm(request.POST or None, request.FILES or None, instance=pregao)
    if form.is_valid():
        form.save()
        messages.success(request, u'Termo de Homologação cadastrado com sucesso.')
        return HttpResponseRedirect(u'/base/ver_pregoes/')

    return render(request, 'upload_termo_homologacao.html', locals(), RequestContext(request))


@login_required()
def gerar_resultado_licitacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
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
    # print resultado
    # tem_empate_ficto = False
    # total_global_vencedor = 0
    # ganhador_eh_beneficiario = False
    while indice < total:
        fornecedor = ParticipantePregao.objects.get(id=resultado[indice][0])
        # if indice == 0:
        #     total_global_vencedor = resultado[indice][0]
        #     ganhador_eh_beneficiario = fornecedor.me_epp
        #
        # elif not tem_empate_ficto and not ganhador_eh_beneficiario:
        #     if fornecedor.me_epp:
        #         limite_lance = total_global_vencedor + (total_global_vencedor*10)/100
        #         if resultado[indice][0] < limite_lance:
        #             tem_empate_ficto = True

        itens = PropostaItemPregao.objects.filter(pregao=pregao, participante=fornecedor)

        for item in itens:
            if ResultadoItemPregao.objects.filter(item=item.item, participante=fornecedor).exists():
                ResultadoItemPregao.objects.filter(item=item.item, participante=fornecedor).update(valor=item.valor, ordem=indice+1)
            else:
                novo_resultado = ResultadoItemPregao()
                novo_resultado.item = item.item
                novo_resultado.participante = fornecedor
                novo_resultado.valor = item.valor
                novo_resultado.marca = item.marca
                novo_resultado.ordem = indice+1
                novo_resultado.situacao = ResultadoItemPregao.CLASSIFICADO
                novo_resultado.save()

        indice += 1


    messages.success(request, u'Resultado gerado com sucesso.')
    return HttpResponseRedirect(u'/base/pregao/%s/#classificacao' % pregao.id)


@login_required()
def lista_materiais(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)

    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/pesquisas/rascunhos/%s.pdf' % solicitacao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()

    pode_ver_preco = request.user.groups.filter(name=u'Compras').exists()
    itens = solicitacao.itemsolicitacaolicitacao_set.all()
    total = 0
    if pode_ver_preco:
        for item in itens:
            if item.valor_medio:
                total += item.quantidade * item.valor_medio

    data = {'solicitacao': solicitacao,'configuracao': configuracao, 'logo': logo, 'data_emissao':data_emissao, 'pode_ver_preco': pode_ver_preco, 'total': total}

    template = get_template('lista_materiais.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def lista_materiais_por_secretaria(request, solicitacao_id, secretaria_id):
    solicitacao = get_object_or_404(SolicitacaoLicitacao, pk=solicitacao_id)
    secretaria = get_object_or_404(Secretaria, pk=secretaria_id)

    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/pesquisas/rascunhos/%s.pdf' % solicitacao_id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()

    pode_ver_preco = request.user.groups.filter(name=u'Compras').exists()
    itens = ItemQuantidadeSecretaria.objects.filter(item__solicitacao=solicitacao, secretaria=secretaria).order_by('item')
    total = 0
    if pode_ver_preco:
        for item in itens:
            if item.item.valor_medio:
                total += item.quantidade * item.item.valor_medio

    data = {'itens': itens, 'solicitacao': solicitacao,'configuracao': configuracao, 'logo': logo, 'data_emissao':data_emissao, 'pode_ver_preco': pode_ver_preco, 'total': total}

    template = get_template('lista_materiais_por_secretaria.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')


@login_required()
def documentos_atas(request, solicitacao_id):
    contrato = Contrato.objects.filter(solicitacao=solicitacao_id)

    if contrato.exists():
        contrato = contrato.latest('id')
    title= u'Documentos - %s' % contrato
    return render(request, 'documentos_atas.html', locals(), RequestContext(request))

@login_required()
def rejeitar_pesquisa(request, item_pesquisa_id):
    item = get_object_or_404(ItemPesquisaMercadologica, pk=item_pesquisa_id)
    title=u'Rejeitar Proposta'
    form = RejeitarPesquisaForm(request.POST or None, instance=item)
    if form.is_valid():
        o = form.save(False)
        o.ativo = False
        o.rejeitado_em = datetime.datetime.now()
        o.rejeitado_por = request.user
        o.save()
        messages.success(request, u'Proposta rejeitada com sucesso.')
        return HttpResponseRedirect(u'/base/ver_pesquisa_mercadologica/%s/' % item.item.id)
    return render(request, 'rejeitar_pesquisa.html', locals(), RequestContext(request))


@login_required()
def relatorio_lista_download_licitacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)

    configuracao = None
    logo = None
    if get_config():
        configuracao = get_config()
        if get_config().logo:
            logo = os.path.join(settings.MEDIA_ROOT, get_config().logo.name)

    destino_arquivo = u'upload/pesquisas/rascunhos/%s.pdf' % pregao.id
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'upload/pesquisas/rascunhos'))
    caminho_arquivo = os.path.join(settings.MEDIA_ROOT,destino_arquivo)
    data_emissao = datetime.date.today()


    itens = LogDownloadArquivo.objects.filter(arquivo__pregao=pregao)
    total_downloads = itens.count()
    total_empresas = itens.distinct('cnpj').count()


    data = {'itens': itens, 'pregao': pregao,'configuracao': configuracao, 'logo': logo, 'data_emissao':data_emissao, 'total_downloads': total_downloads, 'total_empresas': total_empresas}

    template = get_template('relatorio_lista_download_licitacao.html')

    html  = template.render(Context(data))

    pdf_file = open(caminho_arquivo, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file,
            encoding='utf-8')
    pdf_file.close()
    file = open(caminho_arquivo, "r")
    pdf = file.read()
    file.close()
    return HttpResponse(pdf, 'application/pdf')

@login_required()
def apagar_item(request, item_id):
    item = get_object_or_404(ItemSolicitacaoLicitacao, pk=item_id)
    solicitacao = item.solicitacao
    item.delete()
    messages.success(request, u'Item apagado com sucesso.')
    return HttpResponseRedirect(u'/base/itens_solicitacao/%s/' % solicitacao.id)

@login_required()
def liberar_licitacao_homologacao(request, pregao_id):
    pregao = get_object_or_404(Pregao, pk=pregao_id)
    pregao.pode_homologar = True
    pregao.save()
    return HttpResponseRedirect(u'/base/pregao/%s/' % pregao.id)