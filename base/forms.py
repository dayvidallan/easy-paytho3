# -*- coding: utf-8 -*-

from django import forms
from newadmin import utils
from base.models import *
from django.contrib.admin.widgets import AdminDateWidget
from dal import autocomplete
from django.contrib.auth.models import Group
from localflavor.br.forms import BRCNPJField
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


class PessoaFisicaForm(forms.ModelForm):
    METHOD = 'POST'

    data_nascimento = forms.DateField(widget=AdminDateWidget())
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

    class Meta:
        model = PessoaFisica
        fields = ['nome', 'cpf', 'sexo', 'data_nascimento', 'telefones', 'celulares', 'email', 'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'estado', 'municipio', 'setor', 'grupo']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.edicao = kwargs.pop('edicao', None)
        super(PessoaFisicaForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            self.fields['setor'].queryset = Setor.objects.filter(secretaria=self.request.user.pessoafisica.setor.secretaria)

        if self.instance.pk:

            if self.instance.municipio:
                self.fields['estado'].initial = self.instance.municipio.estado

            self.fields['grupo'].initial = self.instance.user.groups.all()[0]



    def clean(self):
        if PessoaFisica.objects.filter(cpf=self.cleaned_data.get('cpf')).exists() and not self.edicao:
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

class CadastraPrecoParticipantePregaoForm(forms.Form):
    fornecedor = forms.ModelChoiceField(ParticipantePregao.objects, label=u'Fornecedor', widget=forms.Select(attrs={'onchange':'submeter_form(this)'}))
    preencher = forms.BooleanField(label=u'Preencher Manualmente', initial=False, required=False)
    arquivo = forms.FileField(label=u'Arquivo com as Propostas', required=False)

    class Media:
            js = ['/static/base/js/propostapregao.js']

    def __init__(self, *args, **kwargs):
        self.pregao = kwargs.pop('pregao',None)
        super(CadastraPrecoParticipantePregaoForm, self).__init__(*args, **kwargs)
        ja_cadastrou = PropostaItemPregao.objects.filter(pregao=self.pregao).values_list('participante', flat=True)
        #self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False).exclude(id__in=ja_cadastrou).order_by('id')
        self.fields['fornecedor'].queryset = ParticipantePregao.objects.filter(pregao = self.pregao, desclassificado=False).order_by('id')


class PregaoForm(forms.ModelForm):
    num_processo = forms.CharField(label=u'Número do Processo', required=True)
    class Meta:
        model = Pregao
        fields = ['solicitacao', 'num_processo', 'num_pregao', 'comissao', 'modalidade', 'tipo', 'criterio', 'objeto_tipo', 'eh_ata_registro_preco', 'data_inicio', 'data_termino', 'data_abertura', 'hora_abertura', 'local', 'responsavel']

    def __init__(self, *args, **kwargs):
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(PregaoForm, self).__init__(*args, **kwargs)
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

    def clean(self):
        if not self.instance.pk and Pregao.objects.filter(solicitacao=self.solicitacao).exists():
            self.add_error('solicitacao', u'Já existe um pregão para esta solicitação.')

        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino') and self.cleaned_data.get('data_termino') < self.cleaned_data.get('data_inicio'):
            self.add_error('data_termino', u'A data de término não pode ser menor do que a data de início.')


        if self.cleaned_data.get('data_inicio') and self.cleaned_data.get('data_termino'):
            teste = self.cleaned_data.get('data_termino')- self.cleaned_data.get('data_inicio')
            if self.cleaned_data.get('modalidade').nome == u'Pregão Presencial' and teste.days < 10:
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
    class Meta:
        model = SolicitacaoLicitacao
        fields = ['num_memorando', 'objeto','objetivo','justificativa', 'tipo_aquisicao', 'outros_interessados', 'interessados', 'todos_interessados',  'prazo_resposta_interessados']

    class Media:
            js = ['/static/base/js/solicitacao.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SolicitacaoForm, self).__init__(*args, **kwargs)
        self.fields['prazo_resposta_interessados'].widget.attrs = {'class': 'vDateField'}
        self.fields['interessados'].queryset = Secretaria.objects.exclude(id=self.request.user.pessoafisica.setor.secretaria.id)
        if self.instance.tipo == SolicitacaoLicitacao.COMPRA:
            del self.fields['justificativa']
            del self.fields['tipo_aquisicao']
            del self.fields['todos_interessados']
            del self.fields['outros_interessados']
            del self.fields['interessados']
            del self.fields['prazo_resposta_interessados']

    def clean(self):
        if not self.instance.pk and self.cleaned_data.get('num_memorando') and SolicitacaoLicitacao.objects.filter(num_memorando=self.cleaned_data.get('num_memorando'), setor_origem__secretaria=self.request.user.pessoafisica.setor.secretaria).exists():
            self.add_error('num_memorando', u'Já existe uma solicitação para este memorando.')


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


class PesquisaMercadologicaForm(forms.ModelForm):

    origem_opcao = forms.NullBooleanField(required=False, label=u'Origem da Pesquisa', widget=forms.widgets.RadioSelect(choices=[(True, u'Fornecedor'),(False, u'Ata de Registro de Preço')]))
    ie = forms.CharField(label=u'Inscrição Estadual', required=False)
    email = forms.EmailField(label=u'Email', required=False)
    cpf_representante = utils.CpfFormField(label=u'CPF do Representante Legal', required=False)

    class Meta:
        model = PesquisaMercadologica
        fields = ['origem_opcao', 'numero_ata','vigencia_ata', 'orgao_gerenciador_ata', 'razao_social', 'cnpj', 'endereco', 'ie', 'telefone', 'email', 'nome_representante', 'cpf_representante', 'rg_representante', 'endereco_representante']

    class Media:
            js = ['/static/base/js/pesquisa.js']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.solicitacao = kwargs.pop('solicitacao', None)
        super(PesquisaMercadologicaForm, self).__init__(*args, **kwargs)
        self.fields['vigencia_ata'].widget.attrs = {'class': 'vDateField'}
        if not self.request.user.is_authenticated() or (self.solicitacao.tipo_aquisicao in [SolicitacaoLicitacao.TIPO_AQUISICAO_DISPENSA, SolicitacaoLicitacao.TIPO_AQUISICAO_INEXIGIBILIDADE]):
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





class DesclassificaParticipantePregao(forms.ModelForm):
    motivo_desclassificacao = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)
    class Meta:
        model = ParticipantePregao
        fields = ['motivo_desclassificacao', ]

class RemoverParticipanteForm(forms.Form):
    motivo = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)

class SuspenderPregaoForm(forms.Form):
    motivo = forms.CharField(label=u'Motivo', required=True, widget=forms.Textarea)
    sine_die = forms.BooleanField(label=u'Sine die', required=False)
    data_retorno = forms.DateField(label=u'Data de Retorno', required=False)

    def __init__(self, *args, **kwargs):
        super(SuspenderPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data_retorno'].widget.attrs = {'class': 'vDateField'}

    def clean(self):
        if not self.cleaned_data.get('sine_die') and not self.cleaned_data.get('data_retorno'):
            self.add_error('data_retorno', u'Informe a data de retorno')

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
    class Meta:
        model = AnexoPregao
        fields = ['nome', 'data', 'arquivo', 'publico']

    def __init__(self, *args, **kwargs):
        super(AnexoPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}

class AnexoContratoForm(forms.ModelForm):
    class Meta:
        model = AnexoContrato
        fields = ['nome', 'data', 'arquivo', 'publico']

    def __init__(self, *args, **kwargs):
        super(AnexoContratoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if self.instance.pk:
            self.fields['arquivo'].required = False


class AnexoARPForm(forms.ModelForm):
    class Meta:
        model = AnexoAtaRegistroPreco
        fields = ['nome', 'data', 'arquivo', 'publico']

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
      required=False
    )
    cpf = utils.CpfFormField(label=u'CPF', required=True)
    cnpj = BRCNPJField(label=u'CNPJ', help_text=u'Informe apenas números.')
    class Meta:
        model = LogDownloadArquivo
        fields = ['cnpj', 'nome','responsavel', 'cpf', 'email', 'endereco', 'estado', 'municipio', 'telefone', 'interesse']

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
    info = forms.CharField(label=u'Digite o número do contrato ou do ata', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)

    def __init__(self, *args, **kwargs):
        super(GestaoContratoForm, self).__init__(*args, **kwargs)
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
    info = forms.CharField(label=u'Digite o número do pregão, processo ou do memorando', required=False)
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)

    def __init__(self, *args, **kwargs):
        super(BuscarSolicitacaoForm, self).__init__(*args, **kwargs)
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


class BuscarLicitacaoForm(forms.Form):
    METHOD = u'GET'
    ano = forms.ChoiceField([],
                required = False,
                label    = u'Filtrar por Ano:',
            )
    info = forms.CharField(label=u'Digite o número do pregão, processo ou do memorando', required=False)
    modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)

    situacao = forms.ChoiceField(label=u'Filtrar por situação', required=False, choices=(('', '---------'),) + Pregao.SITUACAO_CHOICES)
    secretaria = forms.ModelChoiceField(queryset=Secretaria.objects, label=u'Filtrar por Secretaria', required=False)

    def __init__(self, *args, **kwargs):
        super(BuscarLicitacaoForm, self).__init__(*args, **kwargs)
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

class MaterialConsumoForm(forms.ModelForm):
    class Meta:
        model = MaterialConsumo
        fields = ('nome', 'observacao',)


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
    class Meta:
        model = AtaRegistroPreco
        fields = ('numero', 'data_inicio', 'data_fim')

    def __init__(self, *args, **kwargs):
        super(AtaRegistroPrecoForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}
        ultima = AtaRegistroPreco.objects.latest('id')
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
        ultima = Contrato.objects.latest('id')
        if ultima.numero:
            lista = ultima.numero.split('/')
            if len(lista) > 1:
                self.fields['numero'].initial = u'%s/%s' % (int(lista[0])+1, lista[1])

    def clean(self):
        if self.cleaned_data.get('garantia_execucao_objeto'):
            if self.cleaned_data.get('garantia_execucao_objeto') > 5:
                raise forms.ValidationError(u'O limite máximo é de 5%.')


class CriarContratoForm(forms.Form):
    # class Meta:
    #     model = Contrato
    #     fields = ('numero', 'data_inicio', 'data_fim')

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
            valor_contrato = int(lista[0])+1

        for i in self.pregao.get_vencedores():
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
        for i in self.pregao.get_vencedores():
            nome_campo = u'garantia_%d' %  i.id
            if self.cleaned_data.get(nome_campo):
                if self.cleaned_data.get(nome_campo) > 5:
                    raise forms.ValidationError(u'O limite máximo é de 5%.')



class NovoPedidoCompraForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoLicitacao
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
    valor = forms.DecimalField(label=u'Valor')
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
        super(CriarOrdemForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}
        if OrdemCompra.objects.all().exists():
            tt = OrdemCompra.objects.latest('id')
            self.fields['numero'].initial = tt.id + 1
        else:
            self.fields['numero'].initial = 1


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

class DefinirVigenciaContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ('data_fim',)

    def __init__(self, *args, **kwargs):
        super(DefinirVigenciaContratoForm, self).__init__(*args, **kwargs)
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}


class AditivarContratoForm(forms.Form):
    data_inicio = forms.DateField(label=u'Data Inicial', widget=AdminDateWidget())
    data_fim = forms.DateField(label=u'Data Final', widget=AdminDateWidget())

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super(AditivarContratoForm, self).__init__(*args, **kwargs)

        self.fields['data_inicio'].initial = self.contrato.get_data_fim()



class DocumentoSolicitacaoForm(forms.ModelForm):
    class Meta:
        model = DocumentoSolicitacao
        fields = ('nome', 'documento')


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ('__all__')


class UploadTermoHomologacaoForm(forms.ModelForm):
    class Meta:
        model = Pregao
        fields = ('arquivo_homologacao',)


class BaixarEditaisForm(forms.Form):
    modalidade = forms.ModelChoiceField(queryset=ModalidadePregao.objects, label=u'Filtrar por Modalidade', required=False)
    numero = forms.CharField(label=u'Filtrar por Número do Pregão', required=False)

class BaixarAtasForm(forms.Form):
    numero = forms.CharField(label=u'Filtrar por Número da Ata', required=False)

class BaixarContratoForm(forms.Form):
    numero = forms.CharField(label=u'Filtrar por Número do Contrato', required=False)

class HistoricoPregaoForm(forms.ModelForm):
    obs = forms.CharField(label=u'Descrição da Ocorrência', widget=forms.Textarea, required=True)
    class Meta:
        model = HistoricoPregao
        fields = ('data', 'obs')

    def __init__(self, *args, **kwargs):
        super(HistoricoPregaoForm, self).__init__(*args, **kwargs)
        self.fields['data'].widget.attrs = {'class': 'vDateField'}

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
        fields = ('nome', 'secretaria')


class AderirARPForm(forms.ModelForm):
    num_memorando = forms.CharField(label=u'Número do Memorando',required=True)
    objetivo = forms.CharField(label=u'Objetivo', widget=forms.Textarea(), required=True)
    justificativa = forms.CharField(label=u'Justificativa', widget=forms.Textarea(), required=True)
    numero = forms.CharField(label=u'Número da ARP',required=True)

    class Meta:
        model = AtaRegistroPreco
        fields = ('num_memorando', 'objeto', 'objetivo', 'justificativa', 'numero', 'orgao_origem', 'num_oficio',  'data_inicio', 'data_fim',)

    def __init__(self, *args, **kwargs):
        super(AderirARPForm, self).__init__(*args, **kwargs)
        self.fields['data_inicio'].widget.attrs = {'class': 'vDateField'}
        self.fields['data_fim'].widget.attrs = {'class': 'vDateField'}


class AdicionarItemAtaForm(forms.ModelForm):
    material = forms.ModelChoiceField(queryset=MaterialConsumo.objects, label=u'Material', required=False, widget=autocomplete.ModelSelect2(url='materialconsumo-autocomplete'))
    fornecedor = forms.ModelChoiceField(Fornecedor.objects, label=u'Fornecedor', required=True, widget=autocomplete.ModelSelect2(url='participantepregao-autocomplete'))
    class Meta:
        model = ItemAtaRegistroPreco
        fields = ('material', 'fornecedor', 'marca', 'unidade', 'quantidade', 'valor', )


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


class EditarPedidoARPForm(forms.ModelForm):
    class Meta:
        model = PedidoAtaRegistroPreco
        fields = ('quantidade',)

class VisitantePregaoForm(forms.ModelForm):
    class Meta:
        model = VisitantePregao
        fields = ('nome',  'cpf',)

class BuscaFornecedorForm(forms.Form):
    nome = forms.CharField(label=u'Digite a razão social ou o CNPJ:')

class LocalizarProcessoForm(forms.Form):
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