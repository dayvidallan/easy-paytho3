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
    form = CadastrarItemSolicitacaoForm

    def response_change(self, request, obj):
        self.message_user(request, u'Item alterado com sucesso.')
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.solicitacao.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Item cadastrado com sucesso.')
        return HttpResponseRedirect('/itens_solicitacao/%s/' % str(obj.solicitacao.pk))

admin.site.register(ItemSolicitacaoLicitacao, ItemSolicitacaoLicitacaoAdmin)

class FornecedorAdmin(NewModelAdmin):

    list_display = ('get_opcoes', 'cnpj', 'razao_social','telefones', 'email')

    def get_opcoes(self, obj):
        return u'<a href="/base/fornecedor/%s/">Visualizar </a>' % obj.id
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
    form = PregaoForm
    list_display = ('solicitacao', 'modalidade', 'tipo','data_abertura', 'local', 'get_opcoes')
    ordering = ('solicitacao',)
    list_filter = ('solicitacao', 'modalidade', 'tipo')

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
    list_display = ('nome', 'secretaria', 'get_membros', 'get_opcoes')
    ordering = ('nome',)
    list_filter = ('nome',)

    def get_membros(self, obj):
        texto = u''
        for membro in MembroComissaoLicitacao.objects.filter(comissao=obj):
            texto = texto + u'<a href="/base/editar_membro_comissao/%s/">%s</a>, ' % (membro.membro.id, membro.membro.nome)

        return texto[:len(texto)-2]
    get_membros.short_description = u'Membros'
    get_membros.allow_tags = True

    def get_opcoes(self, obj):
        texto = u'<table><tr><td><a class="btn btn-info btn-sm href="/base/adicionar_membro_comissao/%s/" class="btn-sm btn-primary">Adicionar Membro</a>' % obj.id
        texto += u'<br><br><a class="btn btn-danger btn-sm href="/base/remover_membro_comissao/%s/" class="btn-sm btn-danger">Remover Membro</a></td></tr></table>' % obj.id
        return texto

    def save_model(self, request, obj, form, change):
        obj.secretaria = request.user.pessoafisica.setor.secretaria
        obj.save()

    def get_queryset(self, request):
        qs = super(ComissaoLicitacaoAdmin, self).get_queryset(request)
        return qs.filter(secretaria=request.user.pessoafisica.setor.secretaria)

    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True


admin.site.register(ComissaoLicitacao, ComissaoLicitacaoAdmin)

class PessoaFisicaAdmin(NewModelAdmin):
    form = PessoaFisicaForm
    list_display = ('nome', 'setor', 'cpf', 'telefones', 'celulares', 'municipio')
    ordering = ('nome',)
    list_filter = ('nome',)

    def get_form(self, request, obj=None, **kwargs):

        AdminForm = super(PessoaFisicaAdmin, self).get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest

    def save_model(self, request, obj, form, change):
        obj.save()
        user_novo = User.objects.get_or_create(username=obj.cpf,is_active=True,is_superuser=False, is_staff=True,password=u'pbkdf2_sha256$20000$THrN7vMCbCch$hvQF8rxuA0EZ6A0Z/q2+izYd4u226ic/XaHXHQ/rJhg=', date_joined=u'2016-06-06T15:52:27.985')[0]
        obj.user = user_novo
        obj.save()
        user_novo.groups.add(form.cleaned_data.get('grupo'))

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
        if obj.situacao == SolicitacaoLicitacao.CADASTRADO:
            texto = texto + '''<a href="/enviar_para_licitacao/%s/" class="btn btn-success">Enviar para Licitação</a>
            ''' % obj.id

        return texto

    get_opcoes.short_description = u'Opções'
    get_opcoes.allow_tags = True


admin.site.register(SolicitacaoLicitacao,SolicitacaoLicitacaoAdmin)


class SecretariaAdmin(NewModelAdmin):
    list_display = ('nome','responsavel')
    ordering = ('nome',)
    list_filter = ('nome',)


admin.site.register(Secretaria, SecretariaAdmin)


class SetorAdmin(NewModelAdmin):
    list_display = ('nome', 'secretaria')
    ordering = ('nome',)
    list_filter = ('nome', 'secretaria')


admin.site.register(Setor, SetorAdmin)

class ModalidadePregaoAdmin(NewModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)


admin.site.register(ModalidadePregao, ModalidadePregaoAdmin)

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
        return HttpResponseRedirect('/base/pregao/%s/' % str(obj.pregao.pk))

    def response_add(self, request, obj):
        self.message_user(request, u'Participante cadastrado com sucesso.', level=messages.SUCCESS)
        return HttpResponseRedirect('/base/pregao/%s/' % str(obj.pregao.pk))

admin.site.register(ParticipantePregao, ParticipantePregaoAdmin)

class TipoUnidadeAdmin(NewModelAdmin):
    list_display = ('nome',)
    ordering = ('nome',)
    list_filter = ('nome',)

admin.site.register(TipoUnidade, TipoUnidadeAdmin)

class MaterialConsumoAdmin(NewModelAdmin):
    list_display = ('codigo', 'nome',)
    ordering = ('nome',)
    search_fields = ('nome', )
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
