# -*- coding: utf-8 -*-

from django import forms
from newadmin import utils
from base.models import *
from django.contrib.admin.widgets import AdminDateWidget
from dal import autocomplete
from django.contrib.auth.models import Group

class CadastraParticipantePregaoForm(forms.ModelForm):
    sem_representante = forms.BooleanField(label=u'Representante Ausente', initial=False, required=False)
    obs_ausencia_participante = forms.CharField(label=u'Motivo da Ausência do Representante', widget=forms.Textarea, required=False)
    fornecedor = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True, widget=autocomplete.ModelSelect2(url='participantepregao-autocomplete'))
    class Meta:
        model = ParticipantePregao
        fields = ['fornecedor','nome_representante','cpf_representante', 'sem_representante', 'obs_ausencia_participante', 'me_epp']


    class Media:
            js = ['/static/base/js/participantepregao.js']

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        super(CadastraParticipantePregaoForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.cleaned_data.get('fornecedor'):
            if ParticipantePregao.objects.filter(pregao=self.pregao, fornecedor=self.cleaned_data.get('fornecedor')).exists():
                raise forms.ValidationError(u'Este fornecedor já é participante do pregão.')



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


class PessoaFisicaForm(forms.ModelForm):
    METHOD = 'POST'

    data_nascimento = forms.DateTimeField(widget=AdminDateWidget())
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )

    grupo = forms.ModelChoiceField(Group.objects, label=u'Grupo de Acesso', required=True)

    class Meta:
        model = PessoaFisica
        fields = ['nome', 'cpf', 'sexo', 'data_nascimento', 'telefones', 'celulares', 'email', 'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'estado', 'municipio', 'setor', 'grupo']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PessoaFisicaForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            self.fields['setor'].queryset = Setor.objects.filter(secretaria=self.request.user.pessoafisica.setor.secretaria)

class CadastrarItemSolicitacaoForm(forms.ModelForm):
    codigo = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))
    especificacao = forms.CharField(label=u'Especificação', required=True, widget=forms.Textarea())

    class Meta:
        model = ItemSolicitacaoLicitacao
        exclude = ['item', 'solicitacao', 'total', 'valor_medio', 'data_inicio_pesquisa', 'data_fim_pesquisa', 'setor_origem', 'setor_atual', 'situacao', 'obs', 'ativo']


class CadastraPrecoParticipantePregaoForm(forms.Form):
    fornecedor = forms.ModelChoiceField(ParticipantePregao.objects, label=u'Fornecedor', widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    arquivo = forms.FileField(label=u'Arquivo com as Propostas', required=False)
    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        super(CadastraPrecoParticipantePregaoForm, self).__init__(*args, **kwargs)
        ja_cadastrou = PropostaItemPregao.objects.filter(pregao=self.pregao).values_list('participante', flat=True)
        #self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False).exclude(id__in=ja_cadastrou).order_by('id')
        self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False).order_by('id')

class PregaoForm(forms.ModelForm):

     class Meta:
        model = Pregao
        exclude = ['situacao', 'obs']

     def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(PregaoForm, self).__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['solicitacao'] = forms.ModelChoiceField(label=u'Solicitação', queryset=SolicitacaoLicitacao.objects.filter(id=self.solicitacao.id), initial=0)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_termino'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_abertura'].widget.attrs = {'class': 'vDateField'}

     def clean(self):
        if Pregao.objects.filter(solicitacao=self.solicitacao).exists():
            self.add_error('solicitacao', u'Já existe um pregão para esta solicitação.')

class SolicitacaoForm(forms.ModelForm):
    objeto = forms.CharField(label=u'Descrição do Objeto', widget=forms.Textarea(), required=True)
    objetivo = forms.CharField(label=u'Objetivo', widget=forms.Textarea(), required=True)
    justificativa = forms.CharField(label=u'Justificativa', widget=forms.Textarea(), required=True)
    outros_interessados = forms.BooleanField(label=u'Adicionar Outros Interessados', required=False)
    interessados = forms.ModelMultipleChoiceField(Secretaria.objects, label=u'Interessados', required=False, widget=autocomplete.ModelSelect2Multiple(url='secretaria-autocomplete'))
    prazo_resposta_interessados = forms.DateField(label=u'Prazo para retorno dos interessados', widget=AdminDateWidget(), required=False)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['num_memorando', 'objeto','objetivo','justificativa', 'outros_interessados', 'interessados', 'prazo_resposta_interessados']

    class Media:
            js = ['/static/base/js/solicitacao.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['prazo_resposta_interessados'].widget.attrs = {'class': 'vDateField'}
        self.fields['interessados'].queryset = Secretaria.objects.exclude(id=self.request.user.pessoafisica.setor.secretaria.id)

class ItemSolicitacaoLicitacaoForm(forms.ModelForm):
    class Meta:
        model = ItemSolicitacaoLicitacao
        exclude = ['solicitacao', 'item', 'total', 'valor_medio', 'situacao', 'obs']


class RejeitarSolicitacaoForm(forms.ModelForm):
    obs_negacao = forms.CharField(label=u'Justificativa da Negação', widget=forms.Textarea)
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['obs_negacao',]


class LanceForm(forms.Form):
    lance = forms.DecimalField(required=True)

class RegistrarPrecoItemForm(forms.ModelForm):
    class Meta:
        model = ItemSolicitacaoLicitacao
        fields = ['valor_medio',]


class PesquisaMercadologicaForm(forms.ModelForm):

    origem_opcao = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor'),(False, u'Ata de Registro de Preço')]))

    class Meta:
        model = PesquisaMercadologica
        fields = ['origem_opcao', 'numero_ata','vigencia_ata', 'orgao_gerenciador_ata', 'razao_social', 'cnpj', 'endereco', 'ie', 'telefone', 'email', 'nome_representante', 'cpf_representante', 'rg_representante', 'endereco_representante']

    class Media:
            js = ['/static/base/js/pesquisa.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PesquisaMercadologicaForm, self).__init__(*args, **kwargs)
        self.fields['vigencia_ata'].widget.attrs = {'class': 'vDateField'}
        if not self.request.user.is_authenticated():
            self.fields['origem_opcao'] = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor')]), initial=True)

    def clean(self):
        if self.cleaned_data.get('origem_opcao') is False:
            if not self.cleaned_data.get('numero_ata'):
                self.add_error('numero_ata', u'Este campo é obrigatório')

            if not self.cleaned_data.get('vigencia_ata'):
                self.add_error('vigencia_ata', u'Este campo é obrigatório')

            if not self.cleaned_data.get('orgao_gerenciador_ata'):
                self.add_error('orgao_gerenciador_ata', u'Este campo é obrigatório')

        elif self.cleaned_data.get('origem_opcao') is True:
            if not self.cleaned_data.get('razao_social'):
                self.add_error('razao_social', u'Este campo é obrigatório')

            if not self.cleaned_data.get('cnpj'):
                self.add_error('cnpj', u'Este campo é obrigatório')

            if not self.cleaned_data.get('ie'):
                self.add_error('ie', u'Este campo é obrigatório')

            if not self.cleaned_data.get('telefone'):
                self.add_error('telefone', u'Este campo é obrigatório')

            if not self.cleaned_data.get('email'):
                self.add_error('email', u'Este campo é obrigatório')

            if not self.cleaned_data.get('nome_representante'):
                self.add_error('nome_representante', u'Este campo é obrigatório')

            if not self.cleaned_data.get('cpf_representante'):
                self.add_error('cpf_representante', u'Este campo é obrigatório')

            if not self.cleaned_data.get('rg_representante'):
                self.add_error('rg_representante', u'Este campo é obrigatório')

            if not self.cleaned_data.get('endereco_representante'):
                self.add_error('endereco_representante', u'Este campo é obrigatório')




class DesclassificaParticipantePregao(forms.ModelForm):
    motivo_desclassificacao = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)
    class Meta:
        model = ParticipantePregao
        fields = ['motivo_desclassificacao', ]

class RemoverParticipanteForm(forms.Form):
    motivo = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)

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
    class Meta:
        model = AnexoPregao
        fields = ['nome', 'data', 'arquivo']

class LogDownloadArquivoForm(forms.ModelForm):
    estado = forms.ModelChoiceField(Estado.objects, label=u'Estado', required=True)
    municipio = utils.ChainedModelChoiceField(Municipio.objects,
      label                = u'Município',
      empty_label          = u'Selecione o Estado',
      obj_label            = 'nome',
      form_filters         = [('estado', 'estado_id')],
      required=False
    )
    class Meta:
        model = LogDownloadArquivo
        fields = ['nome', 'responsavel', 'cpf', 'cnpj', 'endereco', 'estado', 'municipio', 'telefone', 'interesse']

class UploadPesquisaForm(forms.ModelForm):
    class Meta:
        model = PesquisaMercadologica
        fields = ['arquivo']

class AlteraLanceForm(forms.ModelForm):
    class Meta:
        model = LanceItemRodadaPregao
        fields = ['valor']

class EditarPropostaForm(forms.ModelForm):
    class Meta:
        model = PropostaItemPregao
        fields = ['marca', 'valor']

class EncerrarPregaoForm(forms.ModelForm):
    obs = forms.CharField(label=u'Observações', widget=forms.Textarea)
    class Meta:
        model = Pregao
        fields = ['obs']

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
    setor = forms.ModelChoiceField(Setor.objects, label=u'Setor de Destino', required=True)
    obs = forms.CharField(label=u'Observações', widget=forms.Textarea, required=False)
    def __init__(self, *args, **kwargs):
        self.devolve = kwargs.pop('devolve', None)
        super(SetorEnvioForm, self).__init__(*args, **kwargs)
        if self.devolve:
            del self.fields['setor']


class GanhadoresForm(forms.Form):
    ganhador = forms.ModelChoiceField(ParticipantePregao.objects, required=False, label=u'Filtrar por ganhador', widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    def __init__(self, *args, **kwargs):
        self.participantes = kwargs.pop('participantes', None)
        super(GanhadoresForm, self).__init__(*args, **kwargs)
        self.fields['ganhador'].queryset = ParticipantePregao.objects.filter(id__in=self.participantes.values_list('id', flat=True))

class CadastroMinutaForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['arquivo_minuta']


class ObsForm(forms.Form):
    obs = forms.CharField(label=u'Observação', required=False, widget=forms.Textarea)
    arquivo = forms.FileField(label=u'Parecer Jurídico', required=False)

class ImportarItensForm(forms.Form):
    arquivo = forms.FileField(label=u'Arquivo com os Itens', required=True)

class BuscaPessoaForm(forms.Form):
    pessoa = forms.ModelChoiceField(PessoaFisica.objects, label=u'Pessoa', required=True, widget=autocomplete.ModelSelect2(url='pessoafisica-autocomplete'))

class AbrirProcessoForm(forms.ModelForm):
    objeto = forms.CharField(label=u'Objeto', widget=forms.Textarea())
    class Meta:
        model = Processo
        fields = ('numero', 'objeto', 'tipo', 'palavras_chave')

    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(AbrirProcessoForm, self).__init__(*args, **kwargs)
        self.fields['objeto'].initial = self.solicitacao.objeto

class BuscarSolicitacaoForm(forms.Form):
    info = forms.CharField(label=u'Digite o número do processo ou do memorando', required=False)