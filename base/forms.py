# -*- coding: utf-8 -*-

from django import forms
from newadmin import utils
from base.models import *
from django.contrib.admin.widgets import AdminDateWidget
from dal import autocomplete
from django.contrib.auth.models import Group
from localflavor.br.forms import BRCNPJField
from form_utils.forms import BetterForm
from dateutil.relativedelta import relativedelta
from newadmin.utils import to_ascii
import datetime
class CadastraParticipantePregaoForm(forms.ModelForm):
    sem_representante = forms.BooleanField(label=u'Representante Ausente', initial=False, required=False)
    obs_ausencia_participante = forms.CharField(label=u'Motivo da Ausência do Representante', widget=forms.Textarea, required=False)
    fornecedor = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True, widget=autocomplete.ModelSelect2(url='participantepregao-autocomplete'))
    cpf_representante = utils.CpfFormField(label=u'CPF', required=False)

    class Meta:
        model = ParticipantePregao
        fields = ['fornecedor','nome_representante','rg_representante', 'cpf_representante', 'sem_representante', 'obs_ausencia_participante', 'me_epp']


    class Media:
            js = ['/static/base/js/participantepregao.js']

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        super(CadastraParticipantePregaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('fornecedor'):
            if ParticipantePregao.objects.filter(pregao=self.pregao, fornecedor=self.cleaned_data.get('fornecedor')).exists():
                raise forms.ValidationError(u'Este fornecedor já é participante do pregão.')

        if not self.cleaned_data.get('sem_representante') and not self.cleaned_data.get('cpf_representante'):
            self.add_error('cpf_representante', u'Informe o CPF.')




class CadastraPrecoRodadaPregaoForm(forms.ModelForm):
    METHOD = 'POST'

    class Meta:
        model = LanceItemRodadaPregao
        fields = ['participante','valor', 'declinio']

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        self.item = kwargs.pop('item',None)
        self.rodada = kwargs.pop('rodada',None)
        super(CadastraPrecoRodadaPregaoForm, self).__init__(*args, **kwargs)
        ja_deu_lance=LanceItemRodadaPregao.objects.filter(declinio=False, rodada=self.rodada, item=self.item).values_list('participante',flat=True)
        if int(self.rodada.rodada) > 1:
            rodada_anterior = int(self.rodada.rodada) - 1
            participantes_por_ordem = LanceItemRodadaPregao.objects.filter(declinio=False, item=self.item, rodada__rodada=rodada_anterior).order_by('-valor').values_list('participante',flat=True)
        else:
            participantes_por_ordem = PropostaItemPregao.objects.filter(item=self.item).order_by('-valor').values_list('participante',flat=True)
        deu_preco = PropostaItemPregao.objects.filter(item=self.item).values_list('participante',flat=True)
        declinados = LanceItemRodadaPregao.objects.filter(item=self.item, declinio=True).values_list('participante',flat=True)
        self.fields['participante'] = forms.ModelChoiceField(label=u'Participante',queryset = ParticipantePregao.objects.filter(id__in=deu_preco).exclude(id__in=ja_deu_lance).exclude(id__in=declinados), initial=participantes_por_ordem[0])

    def clean(self):
        if self.cleaned_data.get('valor') and self.cleaned_data.get('valor') > self.item.valor_medio:
            self.add_error('valor', u'O valor não pode ser maior do que o valor máximo')

class SoliticarTrocarSenhaForm(forms.Form):
    username = forms.CharField(label=u'Usuário',
                               help_text=u'Informe o seu CPF sem pontos e traços.')
    cpf = utils.CpfFormField(label=u'CPF', required=True)

    def clean(self):
        if 'username' not in self.cleaned_data or \
                        'cpf' not in self.cleaned_data:
            return self.cleaned_data

        try:
            pf = PessoaFisica.objects.get(user__username=self.cleaned_data['username'])
        except PessoaFisica.DoesNotExist:
            raise forms.ValidationError(u'Nenhum usuário encontrado com os dados especificados.')

        return self.cleaned_data

class ChangePasswordForm(forms.Form):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput,
                               label=u'Senha')
    password_confirm = forms.CharField(max_length=100, widget=forms.PasswordInput,
                                       label=u'Confirmação de senha')

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password_confirm(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password_confirm'):
            raise forms.ValidationError(u'A confirmação de senha não é igual à senha.')
        if self.cleaned_data.get('password') != to_ascii(self.cleaned_data.get('password')):
            raise forms.ValidationError(u'A senha não pode ter caracteres com acentuação.')

        return self.cleaned_data['password']

class PessoaFisicaForm(forms.ModelForm):
    METHOD = 'POST'

    
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )

    grupo = forms.ModelChoiceField(Group.objects, label=u'Grupo de Acesso', required=True)
    email = forms.EmailField(label=u'Email', required=True)
    cpf = utils.CpfFormField(label=u'CPF', required=True)
    #data_nascimento = forms.DateField(label=u'Data de Nascimento', widget=forms.widgets.DateInput(format="%d/%m/%Y", attrs={'type':'date'}))
    class Meta:
        model = PessoaFisica
        fields = ['nome', 'cpf', 'matricula', 'vinculo', 'sexo', 'data_nascimento', 'telefones', 'celulares', 'email', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'estado', 'municipio', 'setor', 'grupo']
        # widgets = {
        #     'data_nascimento' : forms.DateInput(attrs={'type':'date'})
        # }


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.edicao = kwargs.pop('edicao', None)
        super(PessoaFisicaForm, self).__init__(*args, **kwargs)
        #self.fields[ 'data_nascimento' ].input_formats = [ '%d-%m-%Y' ]
        self.fields['data_nascimento'].widget.attrs = {'class': 'vDateField'}
        if not self.request.user.is_superuser:
            self.fields['setor'].queryset = Setor.objects.filter(secretaria=self.request.user.pessoafisica.setor.secretaria)

        if self.instance.pk:


            if self.instance.municipio:
                self.fields['estado'].initial = self.instance.municipio.estado

            if self.instance.user.groups.exists():
                self.fields['grupo'].initial = self.instance.user.groups.all()[0]



    def clean(self):

        if self.instance.pk:
            if self.cleaned_data.get('cpf') and PessoaFisica.objects.exclude(id=self.instance.pk).filter(cpf=self.cleaned_data.get('cpf').replace('-','').replace('.','')).exists():
                self.add_error('cpf', u'Já existe um usuário cadastro com este CPF.')
        else:
            if self.cleaned_data.get('cpf') and PessoaFisica.objects.filter(cpf=self.cleaned_data.get('cpf').replace('-','').replace('.','')).exists():
                self.add_error('cpf', u'Já existe um usuário cadastro com este CPF.')


class CadastrarItemSolicitacaoForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))

    class Meta:
        model = ItemSolicitacaoLicitacao
        fields = ['material', 'unidade', 'quantidade']
    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao',None)
        super(CadastrarItemSolicitacaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('material') and ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, material=self.cleaned_data.get('material')).exists():
            self.add_error('material', u'Este material já foi cadastrado.')


class AlterarItemSolicitacaoForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))

    class Meta:
        model = ItemSolicitacaoLicitacao
        fields = ['material', 'unidade', 'quantidade', 'situacao']
    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao',None)
        super(AlterarItemSolicitacaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('material') and ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.solicitacao, material=self.cleaned_data.get('material')).exists():
            self.add_error('material', u'Este material já foi cadastrado.')


class AlterarItemARPForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))

    class Meta:
        model = ItemAtaRegistroPreco
        fields = ['marca', 'valor', 'quantidade', 'unidade', 'fornecedor', 'participante', 'ativo']

    def __init__(self, *args, **kwargs):
        super(AlterarItemARPForm, self).__init__(*args, **kwargs)
        if self.instance.ata.pregao:
            self.fields['participante'].queryset = ParticipantePregao.objects.filter(id__in=self.instance.ata.pregao.participantepregao_set.values_list('id', flat=True))




class AlterarItemContratoForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))

    class Meta:
        model = ItemContrato
        fields = ['marca', 'valor', 'quantidade']




class GestaoPedidoForm(forms.Form):
    METHOD = 'GET'
    info = forms.CharField(label=u'Digite o número de identificação', required=False)
    ano = forms.ChoiceField([],
                            required=False,
                            label=u'Filtrar por Ano:',
                            )
    vigentes = forms.ChoiceField([(u'', u'Todos'), (u'Vigentes', u'Vigentes')],
                            required=False,
                            label=u'Filtrar por Situação:',
                            )

    def __init__(self, *args, **kwargs):
        super(GestaoPedidoForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year

        ANO_CHOICES = []

        ANO_CHOICES.append([u'Todos', u'Todos'])
        ano_inicio = 2015
        ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        self.fields['ano'].choices = ANO_CHOICES


class AnoForm(forms.Form):
    METHOD = 'GET'
    ano = forms.ChoiceField([],
                            required=False,
                            label=u'Filtrar por Ano:',
                            )

    def __init__(self, *args, **kwargs):
        super(AnoForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year

        ANO_CHOICES = []

        ANO_CHOICES.append([u'Todos', u'Todos'])
        ano_inicio = 2015
        ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        self.fields['ano'].choices = ANO_CHOICES

class AnoMesForm(forms.Form):
    METHOD = 'GET'
    ano = forms.ChoiceField([],
                            required=False,
                            label=u'Filtrar por Ano:',
                            )
    mes = forms.ChoiceField([],
                            required=False,
                            label=u'Filtrar por Mês:',
                            )

    def __init__(self, *args, **kwargs):
        super(AnoMesForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year

        ANO_CHOICES = []


        ano_inicio = 2015
        ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        self.fields['ano'].choices = ANO_CHOICES

        MESES = (
            (1, u'Janeiro'),
            (2, u'Fevereiro'),
            (3, u'Março'),
            (4,  u'Abril'),
            (5, u'Maio' ),
            (6, u'Junho'),
            (7,  u'Julho'),
            (8, u'Agosto'),
            (9, u'Setembro'),
            (10,  u'Outubro'),
            (11, u'Novembro' ),
            (12,u'Dezembro' ),
        )
        self.fields['mes'].choices = MESES

class UploadPropostaPesquisaForm(forms.Form):
    arquivo = forms.FileField(label=u'Arquivo com as Propostas', required=False)

class CadastraPrecoParticipantePregaoForm(forms.Form):
    fornecedor = forms.ModelChoiceField(ParticipantePregao.objects, label=u'Fornecedor', widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    preencher = forms.BooleanField(label=u'Preencher Manualmente', initial=False, required=False)
    arquivo = forms.FileField(label=u'Arquivo com as Propostas', required=False)

    class Media:
            js = ['/static/base/js/propostapregao.js']

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        self.preencher_box = kwargs.pop('preencher_box',None)
        super(CadastraPrecoParticipantePregaoForm, self).__init__(*args, **kwargs)
        ja_cadastrou = PropostaItemPregao.objects.filter(pregao=self.pregao).values_list('participante', flat=True)
        #self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False).exclude(id__in=ja_cadastrou).order_by('id')
        self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False, excluido_dos_itens=False).order_by('id')
        if self.preencher_box:
            self.fields['preencher'].initial=True


class PregaoForm(forms.ModelForm):
    num_processo = forms.CharField(label=u'Número do Processo', required=True)

    fieldsets = (
        (u'Dados Gerais', {
            'fields': ('solicitacao', 'num_processo', 'num_pregao', 'comissao', 'modalidade', 'fundamento_legal', 'tipo', 'criterio', 'aplicacao_lcn_123_06', 'objeto_tipo')
        }),
        (u'Valores da Licitação', {
            'fields': ('valor_total', 'recurso_proprio', 'recurso_federal', 'recurso_estadual', 'recurso_municipal', )
        }),
        (u'Cronograma', {
            'fields': ('data_inicio', 'data_termino', 'data_abertura', 'hora_abertura', 'local', 'responsavel')
        }),
    )
    class Meta:
        model = Pregao
        fields = ['solicitacao', 'num_processo', 'num_pregao', 'objeto', 'comissao', 'modalidade', 'fundamento_legal', 'tipo', 'tipo_desconto', 'criterio', 'aplicacao_lcn_123_06', 'objeto_tipo', 'valor_total', 'recurso_proprio', 'recurso_federal', 'recurso_estadual', 'recurso_municipal', 'data_inicio', 'data_termino', 'data_abertura', 'hora_abertura', 'local', 'responsavel', 'situacao']


    class Media:
            js = ['/static/base/js/pregao.js']


    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        self.request = kwargs.pop('request', None)
        super(PregaoForm, self).__init__(*args, **kwargs)
        self.fields['aplicacao_lcn_123_06'].label = u'MPE – Aplicação Da LCN 123/06'
        self.fields['aplicacao_lcn_123_06'].help_text = u'<a href="http://www.planalto.gov.br/ccivil_03/leis/LCP/Lcp123.htm" target="_blank">De acordo com a Lei 123/06</a>'
        if self.solicitacao and self.solicitacao.numero_meses_contratacao_global:

            self.initial['valor_total'] = format_money(self.solicitacao.get_valor_da_solicitacao()*self.solicitacao.numero_meses_contratacao_global)
        else:
            self.initial['valor_total'] = format_money(self.solicitacao.get_valor_da_solicitacao())
        self.fields['valor_total'].widget.attrs = {'readonly': 'True'}
        self.fields['objeto'].initial = self.solicitacao.objeto
        self.fields['num_pregao'].label = u'Número da Licitação/Procedimento'

        if not self.request.user.is_superuser:
            del self.fields['situacao']
        if not self.instance.id:
            self.fields['solicitacao'] = forms.ModelChoiceField(label=u'Solicitação', queryset=SolicitacaoLicitacao.objects.filter(id=self.solicitacao.id), initial=0)
            self.fields['solicitacao'].widget.attrs = {'readonly': 'True'}

        else:
            del self.fields['solicitacao']
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_termino'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_abertura'].widget.attrs = {'class': 'vDateField'}

        if not self.instance.pk:
            self.fields['num_pregao'].initial = self.solicitacao.get_proximo_pregao()

        if self.solicitacao.processo:
            self.fields['num_processo'].initial = self.solicitacao.processo
            self.fields['num_processo'].widget.attrs = {'readonly': 'True'}
        if self.solicitacao.tipo_aquisicao == self.solicitacao.CREDENCIAMENTO:
            self.fields['num_pregao'].label = u'Número do Credenciamento'
            self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CREDENCIAMENTO)
            self.fields['modalidade'].initial = ModalidadePregao.CREDENCIAMENTO

        elif self.solicitacao.tipo_aquisicao in [self.solicitacao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, self.solicitacao.CHAMADA_PUBLICA_OUTROS, self.solicitacao.CHAMADA_PUBLICA_PRONATER]:
            self.fields['num_pregao'].label = u'Número da Chamada Pública'
            if self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR
            elif self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_OUTROS:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_OUTROS)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_OUTROS
            elif self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_PRONATER:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_PRONATER)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_PRONATER

        if self.solicitacao.eh_credenciamento():

            del self.fields['tipo']
            del self.fields['aplicacao_lcn_123_06']



    def clean(self):
        if not self.instance.pk and Pregao.objects.filter(solicitacao=self.solicitacao).exists():
            self.add_error('solicitacao', u'Já existe um pregão para esta solicitação.')

        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino') and self.cleaned_data.get('data_termino') < self.cleaned_data.get('data_inicio'):
            self.add_error('data_termino', u'A data de término não pode ser menor do que a data de início.')

        if not self.cleaned_data.get('objeto_tipo'):
            self.add_error('objeto_tipo', u'Informe o tipo do objeto.')

        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino'):
            teste = self.cleaned_data.get('data_termino')- self.cleaned_data.get('data_inicio')
            if self.cleaned_data.get('modalidade').nome in [u'Pregão Presencial', u'Pregão Presencial - Sistema de Registro de Preços (SRP)'] and teste.days < 8:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 8 dias úteis de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Carta Convite' and teste.days < 5:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 5 dias corridos de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Tomada de Preço' and teste.days < 15:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 15 dias corridos de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Concorrência Pública' and teste.days < 30:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 30 dias corridos de acordo com a legislação atual.')
        numero_repetido = False
        if self.cleaned_data.get('num_pregao'):
            if self.cleaned_data.get('modalidade') and self.cleaned_data.get('modalidade').nome in [u'Pregão Presencial', u'Pregão Presencial - Sistema de Registro de Preços (SRP)']:
                if self.instance.pk and Pregao.objects.filter(modalidade__nome__in=[u'Pregão Presencial', u'Pregão Presencial - Sistema de Registro de Preços (SRP)'], num_pregao=self.cleaned_data.get('num_pregao')).exclude(id=self.instance.pk).exists():
                    numero_repetido = True

                elif not self.instance.pk and Pregao.objects.filter(modalidade__nome__in=[u'Pregão Presencial', u'Pregão Presencial - Sistema de Registro de Preços (SRP)'], num_pregao=self.cleaned_data.get('num_pregao')).exists():
                    numero_repetido = True

            if self.cleaned_data.get('modalidade') and self.cleaned_data.get('modalidade').nome in [u'Pregão Eletrônico',
                                                            u'Pregão Eletrônico - Sistema de Registro de Preços (SRP)']:
                if self.instance.pk and Pregao.objects.filter(modalidade__nome__in=[u'Pregão Eletrônico',
                                                                                    u'Pregão Eletrônico - Sistema de Registro de Preços (SRP)'],
                                                              num_pregao=self.cleaned_data.get('num_pregao')).exclude(
                        id=self.instance.pk).exists():
                    numero_repetido = True

                elif not self.instance.pk and Pregao.objects.filter(modalidade__nome__in=[u'Pregão Eletrônico',
                                                                                          u'Pregão Eletrônico - Sistema de Registro de Preços (SRP)'],
                                                                    num_pregao=self.cleaned_data.get(
                                                                            'num_pregao')).exists():
                    numero_repetido = True

        if numero_repetido:
            self.add_error('num_pregao', u'Já existe um pregão desta modalidade com este número.')

        if self.cleaned_data.get('data_abertura') and self.cleaned_data.get('data_termino') and self.cleaned_data.get('data_abertura') < self.cleaned_data.get('data_termino'):
            self.add_error('data_abertura', u'A data de abertura deve ser maior do que a data de término.')



class EditarPregaoForm(forms.ModelForm):
    num_processo = forms.CharField(label=u'Número do Processo', required=True)

    fieldsets = (
        (u'Dados Gerais', {
            'fields': ('solicitacao', 'num_processo', 'num_pregao', 'comissao', 'modalidade', 'fundamento_legal', 'tipo', 'criterio', 'aplicacao_lcn_123_06', 'objeto_tipo')
        }),
        (u'Valores da Licitação', {
            'fields': ('valor_total', 'recurso_proprio', 'recurso_federal', 'recurso_estadual', 'recurso_municipal', )
        }),
        (u'Cronograma', {
            'fields': ('data_inicio', 'data_termino', 'data_abertura_original', 'hora_abertura_original', 'data_abertura', 'hora_abertura', 'local', 'responsavel')
        }),
    )
    class Meta:
        model = Pregao
        fields = ['solicitacao', 'num_processo', 'data_abertura_original', 'hora_abertura_original', 'num_pregao', 'objeto', 'comissao', 'modalidade', 'fundamento_legal', 'tipo', 'tipo_desconto', 'criterio', 'aplicacao_lcn_123_06', 'objeto_tipo', 'valor_total', 'recurso_proprio', 'recurso_federal', 'recurso_estadual', 'recurso_municipal', 'data_inicio', 'data_termino', 'data_abertura', 'hora_abertura', 'local', 'responsavel', 'situacao']


    class Media:
            js = ['/static/base/js/pregao.js']


    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        self.request = kwargs.pop('request', None)
        super(EditarPregaoForm, self).__init__(*args, **kwargs)
        self.fields['aplicacao_lcn_123_06'].label = u'MPE – Aplicação Da LCN 123/06'
        self.fields['aplicacao_lcn_123_06'].help_text = u'<a href="http://www.planalto.gov.br/ccivil_03/leis/LCP/Lcp123.htm" target="_blank">De acordo com a Lei 123/06</a>'
        if self.solicitacao and self.solicitacao.numero_meses_contratacao_global:

            self.initial['valor_total'] = format_money(self.solicitacao.get_valor_da_solicitacao()*self.solicitacao.numero_meses_contratacao_global)
        else:
            self.initial['valor_total'] = format_money(self.solicitacao.get_valor_da_solicitacao())
        self.fields['valor_total'].widget.attrs = {'readonly': 'True'}
        self.fields['objeto'].initial = self.solicitacao.objeto
        self.fields['num_pregao'].label = u'Número da Licitação/Procedimento'

        if not self.request.user.is_superuser:
            del self.fields['situacao']
        if not self.instance.id:
            self.fields['solicitacao'] = forms.ModelChoiceField(label=u'Solicitação', queryset=SolicitacaoLicitacao.objects.filter(id=self.solicitacao.id), initial=0)
            self.fields['solicitacao'].widget.attrs = {'readonly': 'True'}

        else:
            del self.fields['solicitacao']
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_termino'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_abertura'].widget.attrs = {'class': 'vDateField'}

        if not self.instance.pk:
            self.fields['num_pregao'].initial = self.solicitacao.get_proximo_pregao()

        if self.solicitacao.processo:
            self.fields['num_processo'].initial = self.solicitacao.processo
            self.fields['num_processo'].widget.attrs = {'readonly': 'True'}
        if self.solicitacao.tipo_aquisicao == self.solicitacao.CREDENCIAMENTO:
            self.fields['num_pregao'].label = u'Número do Credenciamento'
            self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CREDENCIAMENTO)
            self.fields['modalidade'].initial = ModalidadePregao.CREDENCIAMENTO

        elif self.solicitacao.tipo_aquisicao in [self.solicitacao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR, self.solicitacao.CHAMADA_PUBLICA_OUTROS, self.solicitacao.CHAMADA_PUBLICA_PRONATER]:
            self.fields['num_pregao'].label = u'Número da Chamada Pública'
            if self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_ALIMENTACAO_ESCOLAR
            elif self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_OUTROS:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_OUTROS)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_OUTROS
            elif self.solicitacao.tipo_aquisicao == self.solicitacao.CHAMADA_PUBLICA_PRONATER:
                self.fields['modalidade'].queryset = ModalidadePregao.objects.filter(id=ModalidadePregao.CHAMADA_PUBLICA_PRONATER)
                self.fields['modalidade'].initial = ModalidadePregao.CHAMADA_PUBLICA_PRONATER

        if self.solicitacao.eh_credenciamento():

            del self.fields['tipo']
            del self.fields['aplicacao_lcn_123_06']



    def clean(self):
        if not self.instance.pk and Pregao.objects.filter(solicitacao=self.solicitacao).exists():
            self.add_error('solicitacao', u'Já existe um pregão para esta solicitação.')

        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino') and self.cleaned_data.get('data_termino') < self.cleaned_data.get('data_inicio'):
            self.add_error('data_termino', u'A data de término não pode ser menor do que a data de início.')

        if not self.cleaned_data.get('objeto_tipo'):
            self.add_error('objeto_tipo', u'Informe o tipo do objeto.')

        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino'):
            teste = self.cleaned_data.get('data_termino')- self.cleaned_data.get('data_inicio')
            if self.cleaned_data.get('modalidade').nome in [u'Pregão Presencial', u'Pregão Presencial - Sistema de Registro de Preços (SRP)'] and teste.days < 8:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 8 dias úteis de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Carta Convite' and teste.days < 5:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 5 dias corridos de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Tomada de Preço' and teste.days < 15:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 15 dias corridos de acordo com a legislação atual.')
            elif self.cleaned_data.get('modalidade').nome == u'Concorrência Pública' and teste.days < 30:
                self.add_error('data_termino', u'A data de término deve ser de pelo menos 30 dias corridos de acordo com a legislação atual.')




        if self.cleaned_data.get('data_abertura') and self.cleaned_data.get('data_termino') and self.cleaned_data.get('data_abertura') < self.cleaned_data.get('data_termino'):
            self.add_error('data_abertura', u'A data de abertura deve ser maior do que a data de término.')


class SolicitacaoForm(forms.ModelForm):
    objeto = forms.CharField(label=u'Descrição do Objeto', widget=forms.Textarea(), required=True)
    objetivo = forms.CharField(label=u'Objetivo', widget=forms.Textarea(), required=True)
    justificativa = forms.CharField(label=u'Justificativa', widget=forms.Textarea(), required=True)
    outros_interessados = forms.BooleanField(label=u'Adicionar Outros Interessados', required=False)

    interessados = forms.ModelMultipleChoiceField(Secretaria.objects, label=u'Interessados', required=False, widget=autocomplete.ModelSelect2Multiple(url='secretaria-autocomplete'))
    todos_interessados = forms.BooleanField(label=u'Selecionar Todos como Interessados', initial=False, required=False)
    prazo_resposta_interessados = forms.DateField(label=u'Prazo para retorno dos interessados', widget=AdminDateWidget(), required=False)
    numero_meses_contratacao_global = forms.IntegerField(label=u'Informe o Número de Meses do Contrato', required=False)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['num_memorando', 'objeto','objetivo','justificativa', 'contratacao_global', 'numero_meses_contratacao_global', 'tipo_aquisicao', 'tipo', 'outros_interessados', 'interessados', 'todos_interessados',  'prazo_resposta_interessados']

    class Media:
            js = ['/static/base/js/solicitacao.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['prazo_resposta_interessados'].widget.attrs = {'class': 'vDateField'}
        if self.request:
            self.fields['interessados'].queryset = Secretaria.objects.exclude(id=self.request.user.pessoafisica.setor.secretaria.id)
            del self.fields['tipo']


        if (self.instance.tipo == SolicitacaoLicitacao.COMPRA or self.instance.tipo_aquisicao == SolicitacaoLicitacao.ADESAO_ARP) and self.request:
            del self.fields['justificativa']
            del self.fields['tipo_aquisicao']
            del self.fields['todos_interessados']
            del self.fields['outros_interessados']
            del self.fields['interessados']
            del self.fields['prazo_resposta_interessados']

    def clean(self):
        if not self.instance.pk and self.cleaned_data.get('num_memorando') and SolicitacaoLicitacao.objects.filter(num_memorando=self.cleaned_data.get('num_memorando'), setor_origem__secretaria=self.request.user.pessoafisica.setor.secretaria).exists():
            self.add_error('num_memorando', u'Já existe uma solicitação para este memorando.')

        if self.cleaned_data.get('contratacao_global') and not self.cleaned_data.get('numero_meses_contratacao_global'):
            self.add_error('numero_meses_contratacao_global', u'Informe o número de meses.')


class EditarItemSolicitacaoLicitacaoForm(forms.ModelForm):
    unidade = forms.ModelChoiceField(TipoUnidade.objects, label=u'Unidade')
    class Meta:
        model = ItemQuantidadeSecretaria
        fields = ['quantidade']

    def __init__(self, *args, **kwargs):
        self.unidade = kwargs.pop('unidade', None)
        super(EditarItemSolicitacaoLicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['unidade'].initial = self.unidade.id

class RejeitarSolicitacaoForm(forms.ModelForm):
    obs_negacao = forms.CharField(label=u'Justificativa da Negação', widget=forms.Textarea)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['obs_negacao',]


class LanceForm(forms.Form):
    lance = forms.DecimalField(required=True)

class RegistrarPrecoItemForm(forms.ModelForm):
    arquivo_referencia_valor_medio = forms.FileField(label=u'Arquivo com a Referência do Valor Médio', required=False)
    class Meta:
        model = ItemSolicitacaoLicitacao
        fields = ['valor_medio', 'arquivo_referencia_valor_medio']
    def __init__(self, *args, **kwargs):
        super(RegistrarPrecoItemForm, self).__init__(*args, **kwargs)
        self.fields['valor_medio'].required = True


class PesquisaMercadologicaForm(forms.Form):

    origem_opcao = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor'),(False, u'Ata de Registro de Preço')]))
    # ie = forms.CharField(label=u'Inscrição Estadual', required=False)
    # email = forms.EmailField(label=u'Email', required=False)
    # cpf_representante = utils.CpfFormField(label=u'CPF do Representante Legal', required=False)

    # class Meta:
    #     model = PesquisaMercadologica
    #     fields = ['origem_opcao', 'numero_ata','vigencia_ata', 'orgao_gerenciador_ata', 'razao_social', 'cnpj', 'endereco', 'ie', 'telefone', 'email', 'nome_representante', 'cpf_representante', 'rg_representante', 'endereco_representante']
    #
    # class Media:
    #         js = ['/static/base/js/pesquisa.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(PesquisaMercadologicaForm, self).__init__(*args, **kwargs)
        #self.fields['vigencia_ata'].widget.attrs = {'class': 'vDateField'}
        if not self.request.user.is_authenticated() or not (self.solicitacao.tipo_aquisicao == self.solicitacao.TIPO_AQUISICAO_LICITACAO):
            self.fields['origem_opcao'] = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor')]), initial=True)

    # def clean(self):
    #     if self.cleaned_data.get('origem_opcao') is False:
    #         if not self.cleaned_data.get('numero_ata'):
    #             self.add_error('numero_ata', u'Este campo é obrigatório')
    #
    #         if not self.cleaned_data.get('vigencia_ata'):
    #             self.add_error('vigencia_ata', u'Este campo é obrigatório')
    #
    #         if not self.cleaned_data.get('orgao_gerenciador_ata'):
    #             self.add_error('orgao_gerenciador_ata', u'Este campo é obrigatório')
    #
    #     elif self.cleaned_data.get('origem_opcao') is True:
    #         if not self.cleaned_data.get('razao_social'):
    #             self.add_error('razao_social', u'Este campo é obrigatório')


class ContinuaPesquisaMercadologicaForm(forms.ModelForm):

    #origem_opcao = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor'),(False, u'Ata de Registro de Preço')]))
    ie = forms.CharField(label=u'Inscrição Estadual', required=False)
    email = forms.EmailField(label=u'Email', required=False)
    cpf_representante = utils.CpfFormField(label=u'CPF do Representante Legal', required=False)
    #arquivo = forms.FileField(label=u'Arquivo com as Propostas', required=False)
    class Meta:
        model = PesquisaMercadologica
        fields = ['numero_ata','vigencia_ata', 'orgao_gerenciador_ata', 'razao_social', 'cnpj', 'endereco', 'ie', 'telefone', 'email', 'nome_representante', 'cpf_representante', 'rg_representante', 'endereco_representante']
    #
    # class Media:
    #         js = ['/static/base/js/pesquisa.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        #self.solicitacao = kwargs.pop('solicitacao', None)
        self.origem = kwargs.pop('origem', None)
        super(ContinuaPesquisaMercadologicaForm, self).__init__(*args, **kwargs)
        if self.origem == u'2':
            del self.fields['numero_ata']
            del self.fields['vigencia_ata']
            del self.fields['orgao_gerenciador_ata']
            self.fields['razao_social'].required = True
            self.fields['cnpj'].required = True
            self.fields['endereco'].required = True
            self.fields['telefone'].required = True
            self.fields['email'].required = True
            self.fields['razao_social'].label = u'Nome/Razão Social*'
            self.fields['cnpj'].label = u'CPF/CNPJ*'
            self.fields['cnpj'].help_text = u'Preencha com números, traços e barras'
            self.fields['endereco'].label = u'Endereço*'
            self.fields['telefone'].label = u'Telefone*'
            self.fields['email'].label = u'Email*'

        else:
            del self.fields['razao_social']
            del self.fields['cnpj']
            del self.fields['endereco']
            del self.fields['ie']
            del self.fields['telefone']
            del self.fields['email']
            del self.fields['nome_representante']
            del self.fields['cpf_representante']
            del self.fields['rg_representante']
            del self.fields['endereco_representante']
            self.fields['numero_ata'].required = True
            self.fields['vigencia_ata'].required = True
            self.fields['orgao_gerenciador_ata'].required = True
            self.fields['vigencia_ata'].widget.attrs = {'class': 'vDateField'}
        # if not self.request.user.is_authenticated() or (self.solicitacao.tipo_aquisicao in [SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA, SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE]):
        #     self.fields['origem_opcao'] = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor')]), initial=True)


class DesclassificaParticipantePregao(forms.ModelForm):
    motivo_desclassificacao = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)
    class Meta:
        model = ParticipantePregao
        fields = ['motivo_desclassificacao', ]

class RemoverParticipanteForm(forms.Form):
    motivo = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)

class SuspenderPregaoForm(forms.Form):
    motivo = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)
    categoria_suspensao = forms.ModelChoiceField(MotivoSuspensaoPregao.objects, label=u'Categoria da Suspensão', required=False)
    sine_die = forms.BooleanField(label=u'Sine die', required=False)
    data_retorno = forms.DateField(label=u'Data de Retorno', required=False)
    hora_retorno = forms.CharField(label=u'Hora de Retorno', required=False)

    def __init__(self, *args, **kwargs):
        super(SuspenderPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data_retorno'].widget.attrs = {'class': 'vDateField'}

    def clean(self):
        if not self.cleaned_data.get('sine_die') and not self.cleaned_data.get('data_retorno'):
            self.add_error('data_retorno', u'Informe a data de retorno')

        if self.cleaned_data.get('data_retorno') and not self.cleaned_data.get('hora_retorno'):
            self.add_error('hora_retorno', u'Informe a hora de retorno')

    class Media:
        js = ['/static/base/js/suspenderpregao.js']

class ResultadoObsForm(forms.ModelForm):
    observacoes = forms.CharField(label=u'Observações', widget=forms.Textarea)
    class Meta:
        model = ResultadoItemPregao
        fields = ['observacoes', ]

class ResultadoAjustePrecoForm(forms.ModelForm):
    observacoes = forms.CharField(label=u'Observações', widget=forms.Textarea)
    class Meta:
        model = ResultadoItemPregao
        fields = ['valor', 'observacoes',]

class DefinirColocacaoForm(forms.ModelForm):
    class Meta:
        model = ResultadoItemPregao
        fields = ['ordem']

class AnexoPregaoForm(forms.ModelForm):
    enviar_email = forms.BooleanField(label=u'Enviar email para fornecedores informando que um novo arquivo foi anexado?', help_text=u'O email só será enviado se o documento também for marcado como público', required=False)
    enviar_email_participantes = forms.BooleanField(label=u'Enviar email apenas para os participantes da licitação?', required=False)
    class Meta:
        model = AnexoPregao
        fields = ['nome', 'data', 'arquivo', 'publico']

    def __init__(self, *args, **kwargs):
        super(AnexoPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}

class AnexoContratoForm(forms.ModelForm):
    enviar_email = forms.BooleanField(
        label=u'Enviar email para fornecedores informando que um novo arquivo foi anexado?',
        help_text=u'O email só será enviado se o documento também for marcado como público', required=False)
    class Meta:
        model = AnexoContrato
        fields = ['nome', 'data', 'arquivo', 'publico', 'enviar_email']

    def __init__(self, *args, **kwargs):
        super(AnexoContratoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if self.instance.pk:
            self.fields['arquivo'].required = False

class AnexoCredenciamentoForm(forms.ModelForm):
    class Meta:
        model = AnexoCredenciamento
        fields = ['nome', 'data', 'arquivo', 'publico']

    def __init__(self, *args, **kwargs):
        super(AnexoCredenciamentoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if self.instance.pk:
            self.fields['arquivo'].required = False

class AnexoARPForm(forms.ModelForm):
    enviar_email = forms.BooleanField(
        label=u'Enviar email para fornecedores informando que um novo arquivo foi anexado?',
        help_text=u'O email só será enviado se o documento também for marcado como público', required=False)
    class Meta:
        model = AnexoAtaRegistroPreco
        fields = ['nome', 'data', 'arquivo', 'publico', 'enviar_email']

    def __init__(self, *args, **kwargs):
        super(AnexoARPForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if self.instance.pk:
            self.fields['arquivo'].required = False

class LogDownloadArquivoForm(forms.ModelForm):
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=True
    )
    cpf = utils.CpfFormField(label=u'CPF', required=True)
    cnpj = BRCNPJField(label=u'CNPJ')
    email = forms.EmailField(label=u'Email')
    class Meta:
        model = LogDownloadArquivo
        fields = ['cnpj', 'nome','responsavel', 'cpf', 'email', 'endereco', 'estado', 'municipio', 'telefone', 'interesse']

    class Media:
            js = ['/static/base/js/baixar_editais.js']

    def __init__(self, *args, **kwargs):
        super(LogDownloadArquivoForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = u'Digite um email válido. O link para download do arquivo será enviado para este email.'

class UploadPesquisaForm(forms.ModelForm):
    arquivo = forms.FileField(label=u'Importar Planilha Preenchida', required=False, help_text=u'O formato do arquivo deve ser XLS ou XLSX.')
    class Meta:
        model = PesquisaMercadologica
        fields = ['arquivo']

    def clean(self):
        if self.cleaned_data.get('arquivo') and (not self.cleaned_data.get('arquivo').name.lower().endswith('.xls') and not self.cleaned_data.get('arquivo').name.lower().endswith('.xlsx')):
            self.add_error(u'arquivo', u'Formato de arquivo não aceito (utilize somente arquivos XLS ou XLSX).')
        return self.cleaned_data

class AlteraLanceForm(forms.ModelForm):
    class Meta:
        model = LanceItemRodadaPregao
        fields = ['valor']

class EditarPropostaForm(forms.ModelForm):
    class Meta:
        model = PropostaItemPregao
        fields = ['marca', 'valor']
    def __init__(self, *args, **kwargs):
        super(EditarPropostaForm, self).__init__(*args, **kwargs)
        self.fields['marca'].required = False

class EncerrarPregaoForm(forms.ModelForm):
    obs = forms.CharField(label=u'Observações', widget=forms.Textarea)
    class Meta:
        model = Pregao
        fields = ['obs']


    class Media:
            js = ['/static/base/js/deserta.js']

    def __init__(self, *args, **kwargs):
        self.deserta = kwargs.pop('deserta', None)
        super(EncerrarPregaoForm, self).__init__(*args, **kwargs)
        if self.deserta:
            self.fields['republicar'] = forms.BooleanField(label=u'Republicar Licitação', required=False)
            self.fields['data'] = forms.DateField(label=u'Data da Nova Sessão', required=False)
            self.fields['hora'] = forms.TimeField(label=u'Hora da Nova Sessão', required=False)
            self.fields['data'].widget.attrs = {'class': 'vDateField'}

    def clean(self):
        if self.cleaned_data.get('republicar') and not self.cleaned_data.get('data'):
            self.add_error('data', u'Informe a data.')

        if self.cleaned_data.get('republicar') and not self.cleaned_data.get('hora'):
            self.add_error('hora', u'Informe a hora.')

class EncerrarItemPregaoForm(forms.ModelForm):
    obs = forms.CharField(label=u'Observações', widget=forms.Textarea)
    class Meta:
        model = ItemSolicitacaoLicitacao
        fields = ['obs']

class PrazoPesquisaForm(forms.ModelForm):
    data_inicio_pesquisa = forms.DateField(label=u'Data Inicial', required=True)
    data_fim_pesquisa = forms.DateField(label=u'Data Final', required=True)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['data_inicio_pesquisa', 'data_fim_pesquisa']

    def __init__(self, *args, **kwargs):
        super(PrazoPesquisaForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio_pesquisa'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim_pesquisa'].widget.attrs = {'class': 'vDateField'}

    def clean(self):
        if self.cleaned_data.get('data_inicio_pesquisa') and self.cleaned_data.get('data_fim_pesquisa') and self.cleaned_data.get('data_fim_pesquisa') < self.cleaned_data.get('data_inicio_pesquisa'):
            self.add_error('data_fim_pesquisa', u'A data final deve ser maior do que a data inicial')


class SetorEnvioForm(forms.Form):
    secretaria = forms.ModelChoiceField(Secretaria.objects.order_by('nome'), label=u'Filtrar por Secretaria', required=True)

    setor = utils.ChainedModelChoiceField(Setor.objects.order_by('nome'),
      label                = u'Setor de Destino',
      empty_label          = u'Selecione a Secretaria',
      obj_label            = 'nome',
      form_filters         = [('secretaria', 'secretaria_id')],
      required=True
    )

    obs = forms.CharField(label=u'Observações', widget=forms.Textarea, required=False)
    def __init__(self, *args, **kwargs):
        self.devolve = kwargs.pop('devolve', None)
        self.setor_atual = kwargs.pop('setor_atual', None)
        super(SetorEnvioForm, self).__init__(*args, **kwargs)
        if self.devolve:
            del self.fields['setor']

    def clean(self):
        if self.cleaned_data.get('setor') and self.cleaned_data.get('setor') == self.setor_atual:
            raise forms.ValidationError(u'A solicitação já está no setor selecionado.')


class GanhadoresForm(forms.Form):
    ganhador = forms.ModelChoiceField(ParticipantePregao.objects, required=False, label=u'Filtrar por ganhador', widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    def __init__(self, *args, **kwargs):
        self.participantes = kwargs.pop('participantes', None)
        super(GanhadoresForm, self).__init__(*args, **kwargs)
        self.fields['ganhador'].queryset = ParticipantePregao.objects.filter(id__in=self.participantes.values_list('id', flat=True))

class CadastroMinutaForm(forms.ModelForm):
    arquivo_minuta = forms.FileField(label=u'Arquivo da Minuta', required=True)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['arquivo_minuta']

class CadastroTermoInexigibilidadeForm(forms.ModelForm):
    termo_inexigibilidade = forms.FileField(label=u'Termo de Inexigibilidade', required=True)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['termo_inexigibilidade']


class ObsForm(forms.Form):
    obs = forms.CharField(label=u'Observação', required=False, widget=forms.Textarea)
    arquivo = forms.FileField(label=u'Parecer Jurídico', required=False)

class ImportarItensForm(forms.Form):
    arquivo = forms.FileField(label=u'Arquivo com os Itens', required=True)

class BuscaPessoaForm(forms.Form):
    pessoa = forms.ModelChoiceField(PessoaFisica.objects, label=u'Pessoa', required=True, widget=autocomplete.ModelSelect2(url='pessoafisica-autocomplete'))

class AbrirProcessoForm(forms.ModelForm):
    objeto = forms.CharField(label=u'Objeto', widget=forms.Textarea())
    palavras_chave = forms.CharField(label=u'Palavras-chave', help_text=u'Separe com ;', required=False)
    class Meta:
        model = Processo
        fields = ('numero', 'objeto', 'tipo', 'palavras_chave')

    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(AbrirProcessoForm, self).__init__(*args, **kwargs)
        self.fields['objeto'].initial = self.solicitacao.objeto


class GestaoContratoForm(forms.Form):
    METHOD = u'GET'
    info = forms.CharField(label=u'Digite o número de identificação', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Filtrar por Fornecedor', required=False)

    def __init__(self, *args, **kwargs):
        self.tipo = kwargs.pop('tipo', None)
        super(GestaoContratoForm, self).__init__(*args, **kwargs)
        if not (self.tipo == u'1'):
            del self.fields['fornecedor']
        ano_limite = datetime.date.today().year
        pregoes = Pregao.objects.all().order_by('data_abertura')
        ANO_CHOICES = []
        if pregoes.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = pregoes[0].data_abertura.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhuma solicitação encontrada'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class BuscarSolicitacaoForm(forms.Form):
    METHOD = u'GET'
    info = forms.CharField(label=u'Número', required=False, help_text='Digite o número da licitação/procedimento, processo ou do memorando')
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Ano',
            )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Secretaria de Origem', required=False)
    tipo = forms.ChoiceField(label=u'Tipo', required=False, choices=SolicitacaoLicitacao.TIPO_AQUISICAO_E_COMPRAS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(BuscarSolicitacaoForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        pregoes = SolicitacaoLicitacao.objects.all().order_by('data_cadastro')
        ANO_CHOICES = []
        if pregoes.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = pregoes[0].data_cadastro.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhuma solicitação encontrada'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite


class BuscarLicitacaoForm(forms.Form):
    METHOD = u'GET'

    data_inicial = forms.DateField(label=u'Data Inicial do Certame', required=False)
    data_final = forms.DateField(label=u'Data Final do Certame', required=False)
    info = forms.CharField(label=u'Digite o número da licitação/procedimento, processo ou do memorando', required=False)
    modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)

    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=(('', '---------'),) + Pregao.SITUACAO_CHOICES)
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)

    def __init__(self, *args, **kwargs):
        super(BuscarLicitacaoForm, self).__init__(*args, **kwargs)


        self.fields['data_inicial'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_final'].widget.attrs = {'class': 'vDateField'}
    def clean(self):

         if self.cleaned_data.get('data_final') and self.cleaned_data.get('data_inicial') and self.cleaned_data.get('data_final') < self.cleaned_data.get('data_inicial'):
             self.add_error('data_final', u'A data final não pode ser menor do que a data inicial.')

class MaterialConsumoForm(forms.ModelForm):
    class Meta:
        model = MaterialConsumo
        fields = ('nome', 'observacao',)

from django.db.models.functions import Lower

class TipoUnidadeForm(forms.ModelForm):
    class Meta:
        model = TipoUnidade
        fields = ('nome', )


    def clean(self):
     if self.cleaned_data.get('nome'):
         nome = self.cleaned_data.get('nome').lower()
         if not self.instance.pk:
            if TipoUnidade.objects.annotate(minusculo=Lower('nome')).filter(minusculo=nome).exists():
                self.add_error('nome', u'Esta unidade já existe.')
         else:
             if TipoUnidade.objects.annotate(minusculo=Lower('nome')).filter(minusculo=nome).exclude(id=self.instance.pk).exists():
                self.add_error('nome', u'Esta unidade já existe.')

class CriarLoteForm(forms.Form):
    solicitacoes = forms.ModelMultipleChoiceField(queryset=ItemSolicitacaoLicitacao.objects, label=u'Selecione os Itens', widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao', None)
        super(CriarLoteForm, self).__init__(*args, **kwargs)
        itens_em_lotes = ItemLote.objects.filter(item__solicitacao=self.pregao.solicitacao)
        self.fields['solicitacoes'].queryset = ItemSolicitacaoLicitacao.objects.filter(solicitacao=self.pregao.solicitacao, eh_lote=False).exclude(id__in=itens_em_lotes.values_list('item', flat=True))

class ConfiguracaoForm(forms.ModelForm):
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )

    class Meta:
        model = Configuracao
        fields = ('nome', 'cnpj', 'endereco', 'estado', 'municipio', 'email', 'telefones', 'logo', 'url', 'ordenador_despesa', 'cpf_ordenador_despesa')

    def __init__(self, *args, **kwargs):
        super(ConfiguracaoForm, self).__init__(*args, **kwargs)
        if self.instance.municipio:
            self.fields['estado'].initial = self.instance.municipio.estado

class DotacaoOrcamentariaForm(forms.ModelForm):
    projeto_atividade_num = forms.IntegerField(label=u'Número do Projeto de Atividade')
    programa_num = forms.IntegerField(label=u'Número do Programa')
    fonte_num = forms.IntegerField(label=u'Número da Fonte')
    elemento_despesa_num = forms.IntegerField(label=u'Número do Elemento de Despesa')

    class Meta:
        model = DotacaoOrcamentaria
        exclude = ()



class EditarPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemQuantidadeSecretaria
        fields = ('quantidade', )

class AtaRegistroPrecoForm(forms.ModelForm):
    #fornecedor_adesao_arp = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True)
    class Meta:
        model = AtaRegistroPreco
        exclude = ('dh_cancelamento', )

    def __init__(self, *args, **kwargs):
        super(AtaRegistroPrecoForm, self).__init__(*args, **kwargs)
        self.fields['pregao'].required = False
        self.fields['data_esgotamento'].required = False



class AtaRegistroPrecoCadastroForm(forms.ModelForm):
    #fornecedor_adesao_arp = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True)
    class Meta:
        model = AtaRegistroPreco
        fields = ('numero', 'data_inicio', 'data_fim', )

    def __init__(self, *args, **kwargs):
        super(AtaRegistroPrecoCadastroForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        if AtaRegistroPreco.objects.exists():
            ultima = AtaRegistroPreco.objects.filter(adesao=False).latest('id')
            if ultima.numero:
                lista = ultima.numero.split('/')
                if len(lista) > 1:
                    self.fields['numero'].initial = u'%s/%s' % (int(lista[0])+1, lista[1])

        #if not self.instance.pk or not self.instance.adesao:
         #   self.fields['fornecedor_adesao_arp'].required=False


class CredenciamentoForm(forms.ModelForm):
    class Meta:
        model = Credenciamento
        fields = ('numero', 'data_inicio', 'data_fim')


    def __init__(self, *args, **kwargs):
        super(CredenciamentoForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        if Credenciamento.objects.exists():
            ultima = Credenciamento.objects.all().latest('id')
            if ultima.numero:
                lista = ultima.numero.split('/')
                if len(lista) > 1:
                    self.fields['numero'].initial = u'%s/%s' % (int(lista[0])+1, lista[1])


class ContratoForm(forms.ModelForm):
    garantia_execucao_objeto = forms.IntegerField(label=u'Garantia de Execução do Objeto (%)', required=False, help_text=u'Limitado a 5%. Deixar em branco caso não se aplique.')
    class Meta:
        model = Contrato
        fields = ('numero', 'aplicacao_artigo_57', 'garantia_execucao_objeto', 'data_inicio', 'data_fim')

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao', None)
        super(ContratoForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        if Contrato.objects.exists():
            ultima = Contrato.objects.latest('id')
            if ultima.numero:
                lista = ultima.numero.split('/')
                if len(lista) > 1:
                    try:
                        int(lista[0])
                        self.fields['numero'].initial = u'%s/%s' % (int(lista[0])+1, lista[1])
                    except:
                        pass

    def clean(self):
        if self.cleaned_data.get('garantia_execucao_objeto'):
            if self.cleaned_data.get('garantia_execucao_objeto') > 5:
                raise forms.ValidationError(u'O limite máximo é de 5%.')
        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_fim') and self.cleaned_data.get('data_fim') < self.cleaned_data.get('data_inicio'):
            self.add_error(u'data_fim', u'A data final não pode ser menor do que a data inicial.')


class CriarContratoForm(BetterForm):

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao', None)
        super(CriarContratoForm, self).__init__(*args, **kwargs)
        # self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        # self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}

        ultima = Contrato.objects.latest('id')
        if ultima.numero:
            lista = ultima.numero.split('/')
        valor_contrato = None
        nome_campos = u''
        if len(lista) > 1:
            try:
                int(lista[0])
                valor_contrato = int(lista[0])+1
            except:
                valor_contrato = 0
        for i in self.pregao.get_vencedores():
            label = u'************** Número do Contrato - Fornecedor: %s' % (i)
            self.fields["contrato_%d" % i.id] = forms.CharField(label=label, required=True)
            if valor_contrato:
                self.fields["contrato_%d" % i.id].initial = u'%s/%s' % (valor_contrato, lista[1])
                valor_contrato += 1
            nome_campos = nome_campos + '%s, ' % i.id
            label = u'Aplicação do Art. 57 da Lei 8666/93(Art. 57. - A duração dos contratos regidos por esta Lei ficará adstrita à vigência dos respectivos créditos orçamentários, exceto quanto aos relativos:)'
            self.fields["aplicacao_artigo_57_%d" % i.id] = forms.ChoiceField(label=label, required=False, choices=Contrato.INCISOS_ARTIGO_57_CHOICES)
            label = u'Garantia de Execução do Objeto (%)'
            self.fields["garantia_%d" % i.id] = forms.IntegerField(label=label, required=False, help_text=u'Limitado a 5%. Deixar em branco caso não se aplique.')

            label = u'Data Inicial'
            self.fields["data_inicial_%d" % i.id] = forms.DateField(label=label, required=True)
            self.fields["data_inicial_%d" % i.id].widget.attrs = {'class': 'vDateField'}
            nome_campos = nome_campos + '%s, ' % i.id
            label = u'Data Final'
            self.fields["data_final_%d" % i.id] = forms.DateField(label=label, required=True)
            self.fields["data_final_%d" % i.id].widget.attrs = {'class': 'vDateField'}
            nome_campos = nome_campos + '%s, ' % i.id

    def clean(self):
        for i in self.pregao.get_vencedores():
            nome_campo = u'garantia_%d' %  i.id
            if self.cleaned_data.get(nome_campo):
                if self.cleaned_data.get(nome_campo) > 5:
                    raise forms.ValidationError(u'O limite máximo é de 5%.')



class NovoPedidoCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoLicitacaoTmp
        fields = ('num_memorando', 'objeto', 'objetivo')

class RejeitarPesquisaForm(forms.ModelForm):
    motivo_rejeicao = forms.CharField(label=u'Motivo da Rejeição', required=True, widget=forms.Textarea())
    class Meta:
        model = ItemPesquisaMercadologica
        fields = ('motivo_rejeicao', )

class FiltrarSecretariaForm(forms.Form):
    secretaria = forms.ModelChoiceField(Secretaria.objects, label=u'Filtrar por Secretaria',  widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    def __init__(self, *args, **kwargs):
        self.pedidos = kwargs.pop('pedidos', None)
        super(FiltrarSecretariaForm, self).__init__(*args, **kwargs)
        self.fields['secretaria'].queryset = Secretaria.objects.filter(id__in=self.pedidos.values_list('secretaria', flat=True))


class FiltraVencedorPedidoForm(forms.Form):
    vencedor = forms.ModelChoiceField(ParticipantePregao.objects, required=False, label=u'Fornecedor')
    def __init__(self, *args, **kwargs):
        self.participantes = kwargs.pop('participantes', None)
        super(FiltraVencedorPedidoForm, self).__init__(*args, **kwargs)
        self.fields['vencedor'].queryset = ParticipantePregao.objects.filter(id__in=self.participantes)



class FiltraFornecedorPedidoForm(forms.Form):
    vencedor = forms.ModelChoiceField(Fornecedor.objects, required=False, label=u'Fornecedor')
    def __init__(self, *args, **kwargs):
        self.participantes = kwargs.pop('participantes', None)
        super(FiltraFornecedorPedidoForm, self).__init__(*args, **kwargs)
        self.fields['vencedor'].queryset = Fornecedor.objects.filter(id__in=self.participantes)

class ValorFinalItemLoteForm(forms.Form):
    valor = forms.DecimalField(label=u'Valor', max_digits=12, decimal_places=2)
    participante_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    def __init__(self, *args, **kwargs):
        self.participante_id = kwargs.pop('participante_id', None)
        super(ValorFinalItemLoteForm, self).__init__(*args, **kwargs)
        self.fields['participante_id'].initial = self.participante_id

class CriarOrdemForm(forms.ModelForm):
    dotacao = forms.BooleanField(label=u'Preencher Dotação', initial=False, required=False)
    class Meta:
        model = OrdemCompra
        fields = ('numero', 'data', 'dotacao', 'projeto_atividade_num', 'projeto_atividade_descricao', 'programa_num', 'programa_descricao', 'fonte_num', 'fonte_descricao', 'elemento_despesa_num', 'elemento_despesa_descricao')

    class Media:
            js = ['/static/base/js/ordem.js']

    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(CriarOrdemForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if OrdemCompra.objects.all().exists():
            tt = OrdemCompra.objects.latest('id')
            self.fields['numero'].initial = tt.id + 1
        else:
            self.fields['numero'].initial = 1


    def clean(self):
        if self.solicitacao.get_ata() and self.solicitacao.get_ata().data_fim < self.cleaned_data.get('data'):
            raise forms.ValidationError(u'A data da ordem não pode ser posterior a data de término da vigência da ata.')

class RegistrarAdjudicacaoForm(forms.ModelForm):
    class Meta:
        model = Pregao
        fields = ('data_adjudicacao',)

    def __init__(self, *args, **kwargs):
        super(RegistrarAdjudicacaoForm, self).__init__(*args, **kwargs)
        self.fields['data_adjudicacao'].widget.attrs = {'class': 'vDateField'}

class RegistrarHomologacaoForm(forms.ModelForm):
    class Meta:
        model = Pregao
        fields = ('data_homologacao',)

    def __init__(self, *args, **kwargs):
        super(RegistrarHomologacaoForm, self).__init__(*args, **kwargs)
        self.fields['data_homologacao'].widget.attrs = {'class': 'vDateField'}
        if self.instance.eh_credenciamento():
            self.fields['data_homologacao'].label = u'Data do Credenciamento'

class DefinirVigenciaContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ('data_fim',)

    def __init__(self, *args, **kwargs):
        super(DefinirVigenciaContratoForm, self).__init__(*args, **kwargs)
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}



class DocumentoSolicitacaoForm(forms.ModelForm):
    documento = forms.FileField(label=u'Arquivo', required=True)
    enviar_email = forms.BooleanField(label=u'Enviar email para fornecedores informando que um novo arquivo foi anexado?', help_text=u'O email só será enviado se o documento também for marcado como público', required=False)
    class Meta:
        model = DocumentoSolicitacao
        fields = ('nome', 'documento', 'publico')


class FornecedorForm(forms.ModelForm):
    cnpj = forms.CharField(label=u'CNPJ/CPF', help_text=u'Utilize pontos e traços, no formato: XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX')
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )

    class Meta:
        model = Fornecedor
        fields = ('cnpj', 'razao_social', 'endereco', 'estado', 'municipio', 'telefones', 'email', 'suspenso', 'suspenso_ate', 'motivo_suspensao')

    class Media:
            js = ['/static/base/js/fornecedor.js']

    def __init__(self, *args, **kwargs):
        super(FornecedorForm, self).__init__(*args, **kwargs)
        self.fields['suspenso_ate'].widget.attrs = {'class': 'vDateField'}
        self.fields['suspenso_ate'].required=False
        self.fields['motivo_suspensao'].required=False


    def clean(self):

        if not self.instance.pk:
            if Fornecedor.objects.filter(cnpj=self.cleaned_data.get('cnpj')).exists():
                self.add_error('cnpj', u'Já existe um fornecedor cadastrado com esse CNPJ/CPF.')
        else:
            if Fornecedor.objects.filter(cnpj=self.cleaned_data.get('cnpj')).exclude(id=self.instance.pk).exists():
                self.add_error('cnpj', u'Já existe um fornecedor cadastrado com esse CNPJ/CPF.')

        if self.cleaned_data.get('suspenso') and not self.cleaned_data.get('suspenso_ate'):
            self.add_error('suspenso_ate', u'Informe até qual data o fornecedor ficará suspenso')


        if self.cleaned_data.get('cnpj'):
            cpf = self.cleaned_data.get('cnpj')
            cpf_valido = True
            import re

            if cpf_valido:
               cpf = ''.join(re.findall('\d', str(cpf)))

               if (not cpf) or (len(cpf) < 11):
                   return False

               # Pega apenas os 9 primeiros dígitos do CPF e gera os 2 dígitos que faltam
               inteiros = map(int, cpf)
               novo = inteiros[:9]

               while len(novo) < 11:
                   r = sum([(len(novo)+1-i)*v for i,v in enumerate(novo)]) % 11

                   if r > 1:
                       f = 11 - r
                   else:
                       f = 0
                   novo.append(f)

               # Se o número gerado coincidir com o número original, é válido
               if novo != inteiros:
                   cpf_valido = False


            if not cpf_valido:
                cnpj = ''.join(re.findall('\d', str(self.cleaned_data.get('cnpj'))))

                if (not cnpj) or (len(cnpj) < 14):
                   self.add_error('cnpj', u'CPF/CNPJ Valor Inválido.')

              # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
                inteiros = map(int, cnpj)
                novo = inteiros[:12]

                prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                while len(novo) < 14:
                    r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
                    if r > 1:
                        f = 11 - r
                    else:
                        f = 0
                    novo.append(f)
                    prod.insert(0, 6)

                # Se o número gerado coincidir com o número original, é válido
                if novo != inteiros:
                    self.add_error('cnpj', u'CPF/CNPJ Inválido.')



class UploadTermoHomologacaoForm(forms.ModelForm):
    class Meta:
        model = Pregao
        fields = ('arquivo_homologacao',)

    def __init__(self, *args, **kwargs):
        super(UploadTermoHomologacaoForm, self).__init__(*args, **kwargs)
        if self.instance.eh_credenciamento():
            self.fields['arquivo_homologacao'].label = u'Termo de Credenciamento'



class BaixarEditaisForm(forms.Form):
    METHOD = u'GET'

    numero = forms.CharField(label=u'Digite o termo da busca (número do procedimento, por exemplo):', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)
    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=(('', '---------'),) + Pregao.SITUACAO_CHOICES)
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    def __init__(self, *args, **kwargs):
        super(BaixarEditaisForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        contratos = Pregao.objects.all().order_by('data_inicio')
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data_inicio.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhuma licitação cadastrada'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite


class BaixarAtasForm(forms.Form):
    numero = forms.CharField(label=u'Digite o número, ano de vigência ou palavra-chave:', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )

    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=((1, 'Todos'), (2, u'Vigentes'), (3, u'Concluídos')) )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Filtrar por Fornecedor', required=False)


    def __init__(self, *args, **kwargs):
        super(BaixarAtasForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        contratos = Contrato.objects.all().order_by('data_inicio')
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data_inicio.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhum contrato cadastrado'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class BaixarContratoForm(forms.Form):
    numero = forms.CharField(label=u'Digite o número, nome do fornecedor, ano de vigência ou palavra-chave:', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )

    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=((1, 'Todos'), (2, u'Vigentes'), (3, u'Concluídos')) )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Filtrar por Fornecedor', required=False)


    def __init__(self, *args, **kwargs):
        super(BaixarContratoForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        contratos = Contrato.objects.all().order_by('data_inicio')
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data_inicio.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhum contrato cadastrado'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class BaixarDispensaForm(forms.Form):
    numero = forms.CharField(label=u'Digite o número, ano de vigência ou palavra-chave:', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )

    #situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=((1, 'Todos'), (2, u'Vigentes'), (3, u'Concluídos')) )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    #fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Filtrar por Fornecedor', required=False)
    tipo = forms.ChoiceField(label=u'Modalidade', choices=[(u'', u'-------------'),(SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA, SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA), (SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE, SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE)], required=False)

    def __init__(self, *args, **kwargs):
        super(BaixarDispensaForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        contratos = SolicitacaoLicitacao.objects.filter(tipo_aquisicao__in=[SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA, SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE])
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data_cadastro.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhum contrato cadastrado'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class HistoricoPregaoForm(forms.ModelForm):
    obs = forms.CharField(label=u'Descrição da Ocorrência', widget=forms.Textarea, required=True)

    class Meta:
        model = HistoricoPregao
        fields = ('obs', )

    # def __init__(self, *args, **kwargs):
    #     super(HistoricoPregaoForm, self).__init__(*args, **kwargs)
    #     self.fields['data'].widget.attrs = {'class': 'vDateField'}

class MembroComissaoLicitacaoForm(forms.ModelForm):
    membro = forms.ModelChoiceField(PessoaFisica.objects, label=u'Pessoa', required=True, widget=autocomplete.ModelSelect2(url='pessoafisica-autocomplete'))
    class Meta:
        model = MembroComissaoLicitacao
        fields = ('membro', 'matricula', 'funcao')

    def __init__(self, *args, **kwargs):
        self.comissao = kwargs.pop('comissao', None)
        super(MembroComissaoLicitacaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('membro'):
            if MembroComissaoLicitacao.objects.filter(comissao=self.comissao, membro=self.cleaned_data.get('membro')).exists():
                raise forms.ValidationError(u'Esta pessoa já é membro do pregão.')

class RemoverMembroComissaoLicitacaoForm(forms.Form):
    membro = forms.ModelChoiceField(PessoaFisica.objects, label=u'Pessoa', required=True)

    def __init__(self, *args, **kwargs):
        self.comissao = kwargs.pop('comissao', None)
        super(RemoverMembroComissaoLicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['membro'].queryset = PessoaFisica.objects.filter(id__in=MembroComissaoLicitacao.objects.filter(comissao=self.comissao).values_list('membro', flat=True))


class ComissaoLicitacaoForm(forms.ModelForm):
    class Meta:
        model = ComissaoLicitacao
        fields = ('nome', 'data_designacao', 'secretaria', 'tipo')

    def __init__(self, *args, **kwargs):
        super(ComissaoLicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['data_designacao'].required = True

class AderirARPForm(forms.ModelForm):
    num_memorando = forms.CharField(label=u'Número do Memorando',required=True)
    objetivo = forms.CharField(label=u'Objetivo', widget=forms.Textarea(), required=True)
    justificativa = forms.CharField(label=u'Justificativa', widget=forms.Textarea(), required=True)
    numero = forms.CharField(label=u'Número da ARP',required=True)
    fornecedor_adesao_arp = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Fornecedor', widget=autocomplete.ModelSelect2(url='fornecedor-autocomplete'))

    class Meta:
        model = AtaRegistroPreco
        fields = ('num_memorando', 'objeto', 'objetivo', 'justificativa', 'numero', 'orgao_origem', 'num_oficio',   'data_inicio', 'data_fim', 'fornecedor_adesao_arp')

    def __init__(self, *args, **kwargs):
        super(AderirARPForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_inicio'].label = u'Data Inicial da Vigência da ARP a Ser Aderida'
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].label = u'Data Final da Vigência da ARP a Ser Aderida'
        self.fields['num_oficio'].label = u'Número do Pregão Originário da ARP'


class AdicionarItemAtaForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))
    #fornecedor = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True, widget=autocomplete.ModelSelect2(url='participantepregao-autocomplete'))
    class Meta:
        model = ItemAtaRegistroPreco
        fields = ('material', 'marca', 'unidade', 'quantidade', 'valor', )


class RevogarPregaoForm(forms.ModelForm):
    class Meta:
        model = Pregao
        fields = ('data_revogacao',)

    def __init__(self, *args, **kwargs):
        super(RevogarPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data_revogacao'].widget.attrs = {'class': 'vDateField'}


class EditarPedidoContratoForm(forms.ModelForm):
    class Meta:
        model = PedidoContrato
        fields = ('quantidade',)

    def clean(self):
        if self.cleaned_data.get('quantidade'):
            quantidade_atual = self.instance.item.get_quantidade_disponivel() + self.instance.quantidade
            if quantidade_atual < self.cleaned_data.get('quantidade'):
                self.add_error('quantidade', u'A quantidade solicitada é maior do que a quantidade disponível do item (%s).' % quantidade_atual)
        return self.cleaned_data



class EditarPedidoARPForm(forms.ModelForm):
    class Meta:
        model = PedidoAtaRegistroPreco
        fields = ('quantidade',)

    def clean(self):
        if self.cleaned_data.get('quantidade'):
            quantidade_atual = self.instance.item.get_quantidade_disponivel() + self.instance.quantidade
            if quantidade_atual < self.cleaned_data.get('quantidade'):
                self.add_error('quantidade', u'A quantidade solicitada é maior do que a quantidade disponível do item (%s).' % quantidade_atual)
        return self.cleaned_data

class VisitantePregaoForm(forms.ModelForm):
    class Meta:
        model = VisitantePregao
        fields = ('nome',  'cpf',)

class BuscaFornecedorForm(forms.Form):
    nome = forms.CharField(label=u'Digite a razão social ou o CNPJ:', required=False)
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=False)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )

class LocalizarProcessoForm(forms.Form):
    METHOD = u'GET'
    numero = forms.CharField(label=u'Informe o Número do Processo', required=False)

class RelatoriosGerenciaisForm(forms.Form):
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    relatorio = forms.ChoiceField(label=u'Tipo de Relatório', choices=((u'Relatório de Situação', u'Relatório de Situação'),(u'Relatório de Economia', u'Relatório de Economia'),), required=False)

    modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)
    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=(('', '---------'),) + Pregao.SITUACAO_CHOICES)
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    visualizar = forms.ChoiceField(label=u'Modo de Visualização', required=False, choices=((u'1', u'Na Tela'),(u'2', u'Gerar PDF'),),)


    def __init__(self, *args, **kwargs):
        super(RelatoriosGerenciaisForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        pregoes = Pregao.objects.all().order_by('data_abertura')
        ANO_CHOICES = []
        if pregoes.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = pregoes[0].data_abertura.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhum pregão cadastrado'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class RelatoriosGerenciaisContratosForm(forms.Form):
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    #relatorio = forms.ChoiceField(label=u'Tipo de Relatório', choices=((u'Relatório de Situação', u'Relatório de Situação'),(u'Relatório de Economia', u'Relatório de Economia'),), required=False)

    #modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)
    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=((1, 'Todos'), (2, u'Vigentes'), (3, u'Concluídos')) )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    fornecedor = forms.ModelChoiceField(queryset=Fornecedor.objects, label=u'Filtrar por Fornecedor', required=False)
    visualizar = forms.ChoiceField(label=u'Modo de Visualização', required=False, choices=((u'1', u'Na Tela'),(u'2', u'Gerar PDF'),),)


    def __init__(self, *args, **kwargs):
        self.fornecedor = kwargs.pop('fornecedor', None)
        super(RelatoriosGerenciaisContratosForm, self).__init__(*args, **kwargs)
        if not self.fornecedor:
            del self.fields['fornecedor']
        ano_limite = datetime.date.today().year
        contratos = Contrato.objects.all().order_by('data_inicio')
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data_inicio.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhum contrato cadastrado'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite

class CriarContratoAdesaoAtaForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.ata = kwargs.pop('ata', None)
        super(CriarContratoAdesaoAtaForm, self).__init__(*args, **kwargs)
        if Contrato.objects.exists():
            ultima = Contrato.objects.latest('id')
            if ultima.numero:
                lista = ultima.numero.split('/')
        valor_contrato = None
        nome_campos = u''
        if len(lista) > 1:
            try:
                valor_contrato = int(lista[0])+1
            except:
                valor_contrato = 0

        i = self.ata.fornecedor_adesao_arp
        label = u'Número do Contrato - Fornecedor: %s' % (i)
        self.fields["contrato_%d" % i.id] = forms.CharField(label=label, required=True)
        if valor_contrato:
            self.fields["contrato_%d" % i.id].initial = u'%s/%s' % (valor_contrato, lista[1])
            valor_contrato += 1
        nome_campos = nome_campos + '%s, ' % i.id
        label = u'Aplicação do Art. 57 da Lei 8666/93(Art. 57. - A duração dos contratos regidos por esta Lei ficará adstrita à vigência dos respectivos créditos orçamentários, exceto quanto aos relativos:)'
        self.fields["aplicacao_artigo_57_%d" % i.id] = forms.ChoiceField(label=label, required=False, choices=Contrato.INCISOS_ARTIGO_57_CHOICES)
        label = u'Garantia de Execução do Objeto (%)'
        self.fields["garantia_%d" % i.id] = forms.IntegerField(label=label, required=False, help_text=u'Limitado a 5%. Deixar em branco caso não se aplique.')

        label = u'Data Inicial'
        self.fields["data_inicial_%d" % i.id] = forms.DateField(label=label, required=True)
        self.fields["data_inicial_%d" % i.id].widget.attrs = {'class': 'vDateField'}
        nome_campos = nome_campos + '%s, ' % i.id
        label = u'Data Final'
        self.fields["data_final_%d" % i.id] = forms.DateField(label=label, required=True)
        self.fields["data_final_%d" % i.id].widget.attrs = {'class': 'vDateField'}
        nome_campos = nome_campos + '%s, ' % i.id

    def clean(self):
        i = self.ata.fornecedor_adesao_arp
        nome_campo = u'garantia_%d' %  i.id
        if self.cleaned_data.get(nome_campo):
            if self.cleaned_data.get(nome_campo) > 5:
                self.add_error('%s' % nome_campo, u'O limite máximo é de 5%.')

        nome_data_inicio = "data_inicial_%d" % i.id
        nome_data_fim = "data_final_%d" % i.id
        if self.cleaned_data.get(nome_data_inicio) and self.cleaned_data.get(nome_data_fim) and  self.cleaned_data.get(nome_data_fim) < self.cleaned_data.get(nome_data_inicio):
            self.add_error(nome_data_fim, u'A data final não pode ser menor do que a data inicial.')


class EmpresaCredenciamentoForm(forms.Form):
    fornecedor = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True, widget=autocomplete.ModelSelect2(url='participantepregao-autocomplete'))
    me_epp = forms.BooleanField(label=u'Micro Empresa/Empresa de Peq.Porte', required=False)

class CRCForm(forms.ModelForm):

    class Meta:
        model = FornecedorCRC
        fields = ('porte_empresa', 'data_abertura', 'inscricao_estadual', 'inscricao_municipal', 'natureza_juridica', 'ramo_negocio', 'cnae_primario_codigo', 'cnae_primario_descricao', 'objetivo_social', 'capital_social', 'data_ultima_integralizacao', 'banco', 'agencia', 'conta', 'nome', 'cpf', 'rg', 'rg_emissor', 'data_nascimento')

    def __init__(self, *args, **kwargs):
        super(CRCForm, self).__init__(*args, **kwargs)
        self.fields['data_abertura'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_ultima_integralizacao'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_nascimento'].widget.attrs = {'class': 'vDateField'}


class CNAESForm(forms.ModelForm):
    class Meta:
        model = CnaeSecundario
        fields = ('codigo', 'descricao')


class SocioForm(forms.ModelForm):
    class Meta:
        model = SocioCRC
        fields = ('cpf', 'nome', 'rg', 'rg_emissor', 'data_expedicao', 'data_nascimento', 'email')

    def __init__(self, *args, **kwargs):
        super(SocioForm, self).__init__(*args, **kwargs)
        self.fields['data_expedicao'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_nascimento'].widget.attrs = {'class': 'vDateField'}


class AditivarContratoForm(BetterForm):
    tipo_aditivo = forms.ChoiceField(label=u'Selecione o Tipo do Aditivo', choices=((u'', u'Selecione o Tipo de Aditivo'), (u'Prazo', u'Prazo'), (u'Valor', u'Valor'), (u'Todos', u'Prazo e Valor'),))
    data_inicial = forms.DateField(label=u'Data Inicial', required=False)
    data_final = forms.DateField(label=u'Data Final', required=False)
    opcoes = forms.ChoiceField(label=u'Tipo', required=False, choices=Aditivo.TIPO_CHOICES)
    indice_reajuste = forms.DecimalField(label=u'Informe o Índice de Reajuste (%)', required=False)
    percentual_acrescimo_valor = forms.DecimalField(label=u'Percentual de Acréscimo Permitido (%)', help_text=u'O percentual máximo é 25%', required=False)
    percentual_acrescimo_quantitativos = forms.DecimalField(label=u'Percentual de Acréscimo Permitido (%)', help_text=u'O percentual máximo é 25%', required=False)

    class Meta:
        fieldsets = [
                    ('tipo', {'fields': ['tipo_aditivo', ], 'legend': 'Tipo do Aditivo'}),
                    ('main', {'fields': ['data_inicial', 'data_final'], 'legend': 'Aditivo de Prazo'}),
                     ('Advanced', {'fields': ['opcoes', 'indice_reajuste'], 'legend': 'Aditivo de Valor',
                                   'description': '',
                                   'classes': ['advanced',]})]

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super(AditivarContratoForm, self).__init__(*args, **kwargs)
        self.fields['data_inicial'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_final'].widget.attrs = {'class': 'vDateField'}
        self.total_acrescimo_quantitativos = 0
        for aditivo in Aditivo.objects.filter(contrato=self.contrato, de_valor=True, tipo=Aditivo.ACRESCIMO_QUANTITATIVOS):
            if aditivo.indice:
                self.total_acrescimo_quantitativos += aditivo.indice

        self.fields['percentual_acrescimo_quantitativos'].initial = 25 - self.total_acrescimo_quantitativos
        self.fields['percentual_acrescimo_quantitativos'].widget.attrs = {'readonly': 'True'}

        self.total_acrescimo_valor = 0
        for aditivo in Aditivo.objects.filter(contrato=self.contrato, de_valor=True, tipo=Aditivo.ACRESCIMO_VALOR):
            if aditivo.indice:
                self.total_acrescimo_valor += aditivo.indice

        self.fields['percentual_acrescimo_valor'].initial = 25 - self.total_acrescimo_valor
        self.fields['percentual_acrescimo_valor'].widget.attrs = {'readonly': 'True'}

    class Media:
            js = ['/static/base/js/aditivo.js']


    def clean(self):
        if self.cleaned_data.get('data_inicial') and not self.cleaned_data.get('data_final'):
            self.add_error('data_final' , u'Informe a data final.')

        if self.cleaned_data.get('data_inicial') and self.cleaned_data.get('data_final'):
            if self.contrato.aplicacao_artigo_57 == Contrato.INCISO_II and ((self.cleaned_data.get('data_final') - self.contrato.data_inicio).days / 5) > 365:
                self.add_error('data_final' , u'Este contrato não pode ser aditivado em mais de 60 meses, conforme o ART. 57 II. Prazo limite: %s.' %  (self.contrato.data_inicio + relativedelta(years=5)).strftime('%d/%m/%y'))



class RescindirContratoForm(forms.Form):

    opcao = forms.ChoiceField(required=False, label=u'Opções', choices=[(u'Arquivar Contrato', u'Arquivar Contrato'),(u'Contratar Remanescentes', u'Contratar Remanescentes')], widget=forms.widgets.RadioSelect())


class ContratoRemanescenteForm(forms.ModelForm):
    fornecedor = forms.ModelChoiceField(ParticipantePregao.objects, label=u'Fornecedor', required=True)
    garantia_execucao_objeto = forms.IntegerField(label=u'Garantia de Execução do Objeto (%)', required=False, help_text=u'Limitado a 5%. Deixar em branco caso não se aplique.')
    class Meta:
        model = Contrato
        fields = ('numero', 'aplicacao_artigo_57', 'garantia_execucao_objeto', 'data_inicio', 'data_fim')

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao', None)
        self.contrato = kwargs.pop('contrato', None)
        super(ContratoRemanescenteForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        if Contrato.objects.exists():
            ultima = Contrato.objects.latest('id')
            if ultima.numero:
                lista = ultima.numero.split('/')
                if len(lista) > 1:
                    self.fields['numero'].initial = u'%s/%s' % (int(lista[0])+1, lista[1])

        fornecedor_atual = ItemContrato.objects.filter(contrato=self.contrato)[0]
        busca = ParticipantePregao.objects.filter(id__in=ParticipantePregao.objects.filter(pregao=self.pregao, excluido_dos_itens=False, desclassificado=False))
        if fornecedor_atual.fornecedor:
            busca = busca.exclude(fornecedor__id=fornecedor_atual.fornecedor.id)
        else:
            busca = busca.exclude(id=fornecedor_atual.participante.id)

        self.fields['fornecedor'].queryset = busca

    def clean(self):
        if self.cleaned_data.get('garantia_execucao_objeto'):
            if self.cleaned_data.get('garantia_execucao_objeto') > 5:
                raise forms.ValidationError(u'O limite máximo é de 5%.')


class EditarItemARPForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))
    class Meta:
        model = ItemAtaRegistroPreco
        fields = ('marca', 'valor', 'quantidade', 'material', 'unidade')

class BuscarModeloAtaForm(forms.Form):
    METHOD = u'GET'
    nome = forms.CharField(label=u'Filtrar por Nome', required=False)
    palavra = forms.CharField(label=u'Filtrar por Plavra-chave', required=False)
    tipo = forms.ChoiceField(label=u'Filtrar por Tipo', required=False, choices=(('', '---------'),) + ModeloAta.TIPO_ATA_CHOICES)

class ModeloAtaForm(forms.ModelForm):

    class Meta:
        model = ModeloAta
        fields = ('nome', 'tipo', 'palavras_chaves', 'arquivo')

    def __init__(self, *args, **kwargs):
        super(ModeloAtaForm, self).__init__(*args, **kwargs)
        self.fields['palavras_chaves'].label = u'Palavras-chave (separe por ;)'
        self.fields['arquivo'].required = True

class BuscarModeloDocumentoForm(forms.Form):
    METHOD = u'GET'
    nome = forms.CharField(label=u'Filtrar por Nome', required=False)
    palavra = forms.CharField(label=u'Filtrar por Plavra-chave', required=False)
    tipo = forms.ModelChoiceField(TipoModelo.objects, label=u'Filtrar por Tipo', required=False)
    tipo_objeto = forms.ModelChoiceField(TipoObjetoModelo.objects, label=u'Filtrar por Tipo do Objeto', required=False)

class ModeloDocumentoForm(forms.ModelForm):

    class Meta:
        model = ModeloDocumento
        fields = ('nome', 'tipo', 'tipo_objeto', 'palavras_chaves', 'arquivo')

    def __init__(self, *args, **kwargs):
        super(ModeloDocumentoForm, self).__init__(*args, **kwargs)
        self.fields['palavras_chaves'].label = u'Palavras-chave (separe por ;)'

        self.fields['arquivo'].required = True
        self.fields['tipo'].queryset = TipoModelo.objects.filter(ativo=True)
        self.fields['tipo_objeto'].queryset = TipoObjetoModelo.objects.filter(ativo=True)


class RelatoriosGerenciaisComprasForm(forms.Form):
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    #relatorio = forms.ChoiceField(label=u'Tipo de Relatório', choices=((u'Relatório de Situação', u'Relatório de Situação'),(u'Relatório de Economia', u'Relatório de Economia'),), required=False)

    #modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)
    tipo_ordem = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=((1, 'Todos'), (2, u'Compras'), (3, u'Serviços')) )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    visualizar = forms.ChoiceField(label=u'Modo de Visualização', required=False, choices=((u'1', u'Na Tela'),(u'2', u'Gerar PDF'),),)


    def __init__(self, *args, **kwargs):
        super(RelatoriosGerenciaisComprasForm, self).__init__(*args, **kwargs)
        ano_limite = datetime.date.today().year
        contratos = OrdemCompra.objects.all().order_by('data')
        ANO_CHOICES = []
        if contratos.exists():
            ANO_CHOICES.append([u'', u'--------'])
            ano_inicio = contratos[0].data.year-1
            ANO_CHOICES += [(ano, unicode(ano)) for ano in range(ano_limite, ano_inicio, -1)]
        else:
            ANO_CHOICES.append([u'', u'Nenhuma ordem cadastrada'])
        self.fields['ano'].choices = ANO_CHOICES
        self.fields['ano'].initial = ano_limite
        self.fields['secretaria'].queryset = Secretaria.objects.filter(id__in=OrdemCompra.objects.values_list('solicitacao__setor_origem__secretaria', flat=True))

class DataRenovaCRCForm(forms.Form):
    data = forms.DateField(label=u'Informe a data da renovação')
    def __init__(self, *args, **kwargs):
        super(DataRenovaCRCForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}


class TransfereItemARPForm(forms.ModelForm):
    justificativa = forms.CharField(label=u'Justificativa', widget=forms.Textarea)
    quantidade_atual = forms.CharField(label=u'Saldo Atual')
    id_do_item = forms.CharField(label=u'Item', widget=forms.HiddenInput)

    class Meta:
        model = TransferenciaItemARP
        fields =('secretaria_origem','id_do_item', 'quantidade_atual', 'secretaria_destino', 'quantidade', 'justificativa')

    class Media:
            js = ['/static/base/js/transf_item_arp.js']


    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item', None)
        super(TransfereItemARPForm, self).__init__(*args, **kwargs)
        self.fields['id_do_item'].initial = self.item.id
        self.fields['secretaria_origem'].queryset = Secretaria.objects.all()
        self.fields['secretaria_destino'].queryset = Secretaria.objects.all()
        self.fields['quantidade_atual'].widget.attrs = {'readonly': 'True'}

    def clean(self):
        if self.cleaned_data.get('secretaria_origem') == self.cleaned_data.get('secretaria_destino'):
            raise forms.ValidationError(u'Selecione como destino uma secretaria diferente da origem.')

        if self.cleaned_data.get('quantidade') and self.cleaned_data.get('quantidade') > self.item.get_saldo_atual_secretaria(self.cleaned_data.get('secretaria_origem')):
            raise forms.ValidationError(u'A quantidade solicitada é maior do que a quantidade disponível: %s.' % self.item.get_saldo_atual_secretaria(self.cleaned_data.get('secretaria_origem')))

class CertidaoCRCForm(forms.ModelForm):

    class Meta:
        model = CertidaoCRC
        fields = ('nome', 'validade', 'arquivo')

    def __init__(self, *args, **kwargs):
        super(CertidaoCRCForm, self).__init__(*args, **kwargs)
        self.fields['validade'].widget.attrs = {'class': 'vDateField'}

class EditarProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        fields = ('numero', 'objeto', 'palavras_chave')


class PedidoSecretariaForm(forms.Form):
    METHOD = u'GET'
    secretaria = forms.ModelChoiceField(Secretaria.objects, label=u'Filtrar por Secretaria',  widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    def __init__(self, *args, **kwargs):
        self.pedidos = kwargs.pop('pedidos', None)
        super(PedidoSecretariaForm, self).__init__(*args, **kwargs)
        self.fields['secretaria'].queryset = Secretaria.objects.filter(id__in=self.pedidos.values_list('setor__secretaria', flat=True))


class FeriadoForm(forms.ModelForm):
     class Meta:
        model = Feriado
        fields = ('data', 'descricao', 'recorrente',)

from easyaudit.models import CRUDEvent
class AuditoriaForm(forms.Form):
    METHOD = u'GET'
    data_inicio = forms.DateField(label=u'Data Inicial')
    data_final = forms.DateField(label=u'Data Final')
    secretaria = forms.ModelChoiceField(Secretaria.objects, label=u'Filtrar por Secretaria', required=False)
    acao = forms.ChoiceField(label=u'Tipo de Ação', choices=[(u'', u'Todos'), (CRUDEvent.CREATE, u'CREATE'),(CRUDEvent.UPDATE, 'UPDATE'),(CRUDEvent.DELETE, U'DELETE'),], required=False)

    def __init__(self, *args, **kwargs):
        super(AuditoriaForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_final'].widget.attrs = {'class': 'vDateField'}

    def clean(self):
        if self.cleaned_data.get('data_final') and self.cleaned_data.get('data_inicio') and  self.cleaned_data.get('data_inicio')  > self.cleaned_data.get('data_final'):
            raise forms.ValidationError(u'A data inicial não pode ser maior do que a data final')



class CadastrarTermoReferenciaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoLicitacao
        fields = ('termo_referencia', )


class EnviarConviteForm(forms.Form):
    titulo = forms.CharField(label=u'Título do Email', max_length=100)
    destinatarios = forms.CharField(label=u'Emails dos Destinatários', help_text=u'Separe os emails com ponto-e-vírgula (;).', max_length=5000)
    mensagem = forms.CharField(label=u'Mensagem do Email', max_length=5000, widget=forms.Textarea())
