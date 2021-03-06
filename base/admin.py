# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import *
from .forms import *
from newadmin.admin import NewModelAdmin
from django.http import HttpResponseRedirect
import datetime
from django.contrib.auth.models import Group
from django.contrib import messages

admin.site.register(PropostaItemPregao)


class ItemSolicitacaoLicitacaoAdmin(NewModelAdmin):
    list_display = ('material', 'solicitacao', 'unidade', 'quantidade')
    search_fields = ('solicitacao__num_memorando', )
    form = AlterarItemSolicitacaoForm

    def response_change(self, request, obj):
        self.message_user(request, u'Item alterado com sucesso.')
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.solicitacao.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Item cadastrado com sucesso.')
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.solicitacao.pk))

admin.site.register(ItemSolicitacaoLicitacao, ItemSolicitacaoLicitacaoAdmin)


class ItemAtaRegistroPrecoAdmin(NewModelAdmin):
    list_display = ('ata', 'item', 'get_descricao', 'marca', 'quantidade', 'valor')
    search_fields = ('ata__numero', )
    form = AlterarItemARPForm

    def get_descricao(self, obj):
        return obj.material
    get_descricao.short_description = u'Item'
admin.site.register(ItemAtaRegistroPreco, ItemAtaRegistroPrecoAdmin)

class ItemContratoAdmin(NewModelAdmin):
    list_display = ('contrato', 'item', 'marca', 'quantidade', 'valor')
    search_fields = ('contrato__numero', )
    form = AlterarItemContratoForm


admin.site.register(ItemContrato, ItemContratoAdmin)

class FornecedorAdmin(NewModelAdmin):

    list_display = ('get_opcoes', 'cnpj', 'razao_social','telefones', 'email')

    def get_opcoes(self, obj):
        return u'<a href="/admin/base/fornecedor/%s/">Visualizar </a>' % obj.id
    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True

    def response_change(self, request, obj):
        self.message_user(request, u'Fornecedor alterado com sucesso.')
        return HttpResponseRedirect('/base/ver_fornecedores/')

    def response_add(self, request, obj):
        id_sessao = "%s_fornecedor" % (request.user.pessoafisica.id)

        if request.session.get(id_sessao):
            self.message_user(request, u'Fornecedor %s cadastrado com sucesso.' % obj, level=messages.SUCCESS)
            return HttpResponseRedirect('/base/cadastra_participante_pregao/%s/' % request.session.get(id_sessao))
        return super(FornecedorAdmin, self).response_add(request, obj)

admin.site.register(Fornecedor, FornecedorAdmin)

class PregaoAdmin(NewModelAdmin):
    #form = PregaoForm
    list_display = ('solicitacao', 'modalidade', 'tipo','data_abertura', 'local', 'get_opcoes')
    ordering = ('solicitacao',)
    list_filter = ('solicitacao', 'modalidade', 'tipo')
    search_fields = ('objeto',  )



    def response_change(self, request, obj):
        self.message_user(request, u'Pregão alterado com sucesso.')
        return HttpResponseRedirect('/pregao/%s/' % str(obj.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Pregão cadastrado com sucesso.', level=messages.SUCCESS)
        return HttpResponseRedirect('/pregao/%s/' % str(obj.pk))

    def get_opcoes(self, obj):
        return u'<a href="/base/pregao/%s/" class="btn btn-primary">Visualizar</a>' % obj.id
    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.solicitacao.situacao = SolicitacaoLicitacao.EM_LICITACAO
        obj.save()
        obj.solicitacao.save()


admin.site.register(Pregao, PregaoAdmin)


class ComissaoLicitacaoAdmin(NewModelAdmin):

    form = ComissaoLicitacaoForm
    list_display = ('get_nome', 'secretaria', 'tipo', 'data_designacao', 'get_membros', 'get_opcoes')
    ordering = ('nome',)
    list_filter = ('nome',)

    def get_membros(self, obj):
        texto = u''
        for membro in MembroComissaoLicitacao.objects.filter(comissao=obj):
            texto = texto + u'<a href="/base/editar_membro_comissao/%s/">%s</a>, ' % (membro.id, membro.membro.nome)

        return texto[:len(texto)-2]
    get_membros.short_description = u'Membros'
    get_membros.allow_tags = True

    def get_opcoes(self, obj):
        texto = u'<a class="btn btn-info btn-sm" href="/base/adicionar_membro_comissao/%s/" class="btn-sm btn-primary">Adicionar Membro</a>' % obj.id
        texto += u'<br><br><a class="btn btn-danger btn-sm" href="/base/remover_membro_comissao/%s/" class="btn-sm btn-danger">Remover Membro</a>' % obj.id
        return texto


    def get_queryset(self, request):
        qs = super(ComissaoLicitacaoAdmin, self).get_queryset(request)
        return qs.filter(secretaria=request.user.pessoafisica.setor.secretaria)

    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True

    def get_nome(self, obj):
        return u'%s - %s' % (obj.nome, obj.tipo)

    get_nome.short_description = u'Portaria'
    get_nome.allow_tags = True


admin.site.register(ComissaoLicitacao, ComissaoLicitacaoAdmin)

class PessoaFisicaAdmin(NewModelAdmin):
    form = PessoaFisicaForm
    list_display = ('nome', 'matricula', 'data_nascimento', 'setor', 'cpf', 'telefones', 'celulares', )
    ordering = ('nome',)
    list_filter = ('setor__secretaria', 'setor', 'vinculo')

    def get_form(self, request, obj=None, **kwargs):

        AdminForm = super(PessoaFisicaAdmin, self).get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest

    def save_model(self, request, obj, form, change):
        obj.save()
        if not change:
            user_novo = User.objects.get_or_create(username=obj.cpf,is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=datetime.datetime.now())[0]
            obj.user = user_novo
            obj.save()
            user_novo.groups.add(form.cleaned_data.get('grupo'))
        else:
            obj.user.groups.clear()
            obj.user.groups.add(form.cleaned_data.get('grupo'))


    def get_queryset(self, request):
        qs = super(PessoaFisicaAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(setor__secretaria=request.user.pessoafisica.setor.secretaria)

        return qs

admin.site.register(PessoaFisica, PessoaFisicaAdmin)

class SolicitacaoLicitacaoAdmin(NewModelAdmin):
    form = SolicitacaoForm
    list_display = ('num_memorando','objeto', 'objetivo', 'situacao','get_opcoes')
    ordering = ('num_memorando',)
    list_filter = ('num_memorando',)
    search_fields = ('objeto', 'objetivo', 'num_memorando')

    def get_form(self, request, obj=None, **kwargs):
        form = super(SolicitacaoLicitacaoAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        obj.data_cadastro = datetime.datetime.now()
        obj.cadastrado_por = request.user
        obj.setor_origem = request.user.pessoafisica.setor
        obj.save()

    def response_change(self, request, obj):
        self.message_user(request, u'Solicitação alterada com sucesso.')
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Solicitação cadastrada com sucesso.', level=messages.SUCCESS)
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.pk))


    def get_opcoes(self, obj):
        texto = '''
            <a href="/itens_solicitacao/%s/" class="btn btn-info">Ver Itens</a>
            ''' % obj.id

        return texto

    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True


admin.site.register(SolicitacaoLicitacao,SolicitacaoLicitacaoAdmin)


class SecretariaAdmin(NewModelAdmin):
    list_display = ('nome', 'sigla', 'responsavel')
    ordering = ('nome',)
    list_filter = ('nome',)
    search_fields = ('nome', )

admin.site.register(Secretaria, SecretariaAdmin)


class SetorAdmin(NewModelAdmin):
    list_display = ('nome', 'sigla', 'secretaria')
    ordering = ('nome',)
    list_filter = ('nome', 'secretaria')


admin.site.register(Setor, SetorAdmin)

# class ModalidadePregaoAdmin(NewModelAdmin):
#     list_display = ('nome',)
#     ordering = ('nome',)
#     list_filter = ('nome',)
#
#
# admin.site.register(ModalidadePregao, ModalidadePregaoAdmin)

# class TipoPregaoAdmin(NewModelAdmin):
#     list_display = ('nome',)
#     ordering = ('nome',)
#     list_filter = ('nome',)
#
#
# admin.site.register(TipoPregao, TipoPregaoAdmin)

class ParticipantePregaoAdmin(NewModelAdmin):
    form = CadastraParticipantePregaoForm
    list_display = ('fornecedor',)
    ordering = ('fornecedor',)
    list_filter = ('fornecedor',)

    def response_change(self, request, obj):
        self.message_user(request, u'Participante alterado com sucesso.')
        return HttpResponseRedirect('/base/pregao/%s/#fornecedores' % str(obj.pregao.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Participante cadastrado com sucesso.', level=messages.SUCCESS)
        return HttpResponseRedirect('/base/pregao/%s/#fornecedores' % str(obj.pregao.pk))

admin.site.register(ParticipantePregao, ParticipantePregaoAdmin)

class TipoUnidadeAdmin(NewModelAdmin):
    form = TipoUnidadeForm
    list_display = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)

admin.site.register(TipoUnidade, TipoUnidadeAdmin)


class AtaRegistroPrecoAdmin(NewModelAdmin):
    form = AtaRegistroPrecoForm
    list_display = ('numero',)
    ordering = ('numero',)

    def response_change(self, request, obj):
        self.message_user(request, u'ARP alterado com sucesso.')
        return HttpResponseRedirect('/base/visualizar_ata_registro_preco/%s/' % str(obj.pk))


admin.site.register(AtaRegistroPreco, AtaRegistroPrecoAdmin)


class ContratoAdmin(NewModelAdmin):
    form = ContratoForm
    list_display = ('numero',)
    ordering = ('numero',)

    def response_change(self, request, obj):
        self.message_user(request, u'Contrato alterado com sucesso.')
        return HttpResponseRedirect('/base/visualizar_contrato/%s/' % str(obj.pk))


admin.site.register(Contrato, ContratoAdmin)

class CredenciamentoAdmin(NewModelAdmin):
    form = CredenciamentoForm
    list_display = ('numero',)
    ordering = ('numero',)

    def response_change(self, request, obj):
        self.message_user(request, u'Credenciamento alterado com sucesso.')
        return HttpResponseRedirect('/base/visualizar_credenciamento/%s/' % str(obj.pk))


admin.site.register(Credenciamento, CredenciamentoAdmin)

class MaterialConsumoAdmin(NewModelAdmin):
    list_display = ('codigo', 'nome',)
    ordering = ('nome',)
    search_fields = ('nome', 'codigo', )
    form = MaterialConsumoForm

    def save_model(self, request, obj, form, change):
        if not change:
            if MaterialConsumo.objects.exists():
                id = MaterialConsumo.objects.latest('id')
                obj.id = id.pk+1
                obj.codigo = id.pk+1
            else:
                obj.id = 1
                obj.codigo = 1

        obj.save()

    def response_add(self, request, obj):
        self.message_user(request, u'Material %s cadastrado com sucesso.' % obj, level=messages.SUCCESS)
        tt = '%s' % request.user.pessoafisica.id
        if request.session.get(tt):
            return HttpResponseRedirect('/base/cadastrar_item_solicitacao/%s/' % request.session.get(tt))
        return super(MaterialConsumoAdmin, self).response_add(request, obj)

admin.site.register(MaterialConsumo, MaterialConsumoAdmin)

class ConfiguracaoAdmin(NewModelAdmin):
    form = ConfiguracaoForm
    list_display = ('nome', 'endereco', 'logo')
    ordering = ('nome',)
    list_filter = ('nome',)

admin.site.register(Configuracao, ConfiguracaoAdmin)

class OrdemCompraAdmin(NewModelAdmin):
    search_fields = ('numero', 'data', )
    list_display = ('numero', 'solicitacao',  'data')
    ordering = ('numero',)

admin.site.register(OrdemCompra, OrdemCompraAdmin)

class ProcessoAdmin(NewModelAdmin):
    list_display = ('numero', 'data_cadastro',  'pessoa_cadastro')
    ordering = ('numero',)
    search_fields = ('numero', 'objeto')

admin.site.register(Processo, ProcessoAdmin)


class LogDownloadArquivoAdmin(NewModelAdmin):
    list_display = ('nome', 'responsavel', 'email',  'cnpj', 'get_pregao')
    ordering = ('responsavel',)
    list_filter = ('arquivo__pregao', )
    search_fields = ('responsavel', 'email', 'cnpj', 'nome')

    def get_pregao(self, obj):
        return obj.arquivo.pregao
    get_pregao.short_description = u'Arquivo do Pregão'

admin.site.register(LogDownloadArquivo, LogDownloadArquivoAdmin)


class AnexoPregaoAdmin(NewModelAdmin):
    list_display = ('nome', 'data', )
    ordering = ('nome',)
    search_fields = ('nome',)

admin.site.register(AnexoPregao, AnexoPregaoAdmin)

class HistoricoPregaoAdmin(NewModelAdmin):
    form = HistoricoPregaoForm
    list_display = ('pregao', 'obs', 'data', )
    ordering = ('data',)
    list_filter = ('pregao', )
    search_fields = ('data',  )



admin.site.register(HistoricoPregao, HistoricoPregaoAdmin)

class DocumentoSolicitacaoAdmin(NewModelAdmin):
    list_display = ('nome', 'cadastrado_em', )
    ordering = ('nome',)
    search_fields = ('cadastrado_em',)

admin.site.register(DocumentoSolicitacao, DocumentoSolicitacaoAdmin)


class AnexoContratoAdmin(NewModelAdmin):
    list_display = ('nome', 'data', )
    ordering = ('nome',)
    search_fields = ('nome',)

admin.site.register(AnexoContrato, AnexoContratoAdmin)


class TipoModeloAdmin(NewModelAdmin):
    list_display = ('nome', 'ativo', )
    ordering = ('nome',)
    search_fields = ('nome',)

    def response_add(self, request, obj):
       return HttpResponseRedirect('/base/cadastrar_modelo_documento/')


admin.site.register(TipoModelo, TipoModeloAdmin)

class TipoObjetoModeloAdmin(NewModelAdmin):
    list_display = ('nome', 'ativo', )
    ordering = ('nome',)
    search_fields = ('nome',)

    def response_add(self, request, obj):
       return HttpResponseRedirect('/base/cadastrar_modelo_documento/')

admin.site.register(TipoObjetoModelo, TipoObjetoModeloAdmin)

class MotivoSuspensaoPregaoAdmin(NewModelAdmin):
    list_display = ('nome', 'ativo', )
    ordering = ('nome',)
    search_fields = ('nome',)

admin.site.register(MotivoSuspensaoPregao, MotivoSuspensaoPregaoAdmin)

class FeriadoAdmin(NewModelAdmin):
    form = FeriadoForm
    list_display = ('data', 'descricao', 'recorrente', 'cadastrado_por')
    ordering = ('data',)
    list_filter = ('recorrente', )
    search_fields = ('data',)

    def save_model(self, request, obj, form, change):
        obj.cadastrado_por = request.user
        obj.save()


admin.site.register(Feriado, FeriadoAdmin)



