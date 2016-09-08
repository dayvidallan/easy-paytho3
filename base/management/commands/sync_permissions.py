# -*- coding: utf-8 -*-

"""
``APP/permissions.xml`` template:

<groups>
    <group>
        <name>suap_operador</name>
        <models>
            <model>
                <app>comum</app>
                <name>sala</name>
                <permissions>
                    <permission>can_add_sala</permission>
                    <permission>can_change_sala</permission>
                    <permission>can_delete_sala</permission>
                </permissions>
            </model>
        </models>
    </group>
</groups>
"""
from os.path import isfile

from django.core.management.base import BaseCommand
from django.db.models.loading import get_app, get_models
from django.utils import termcolors
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from base.management.permission import GroupPermission


class Command(BaseCommand):
    
    """
    https://docs.djangoproject.com/en/1.3/ref/django-admin/#django-admin-option---verbosity
    Use --verbosity to specify the amount of notification and debug information that django-admin.py should print to the console.
        0 means no output.
        1 means normal output (default).
        2 means verbose output.
        3 means very verbose output.
    """
    grupos_no_permisions_xml = []

    def handle(self, *args, **options):
        # O trecho abaixo é necessário para funcionar no django 1.0.4
        options['verbosity'] = options.get('verbosity', '1')
        apps = []
        if len(args):
            for arg in args:
                if arg[0:3] == 'app':
                    apps = arg.split('=')[1].split(',')
        
        group_permission = GroupPermission()
        permissoes = []
        permissoes_list = []
        module_permissions = []
        for app in settings.INSTALLED_APPS:

            #recupera todas as permissões dos arquivos de permissions do app
            permissoes.append(self.processar_group_permission(app, apps, options, group_permission))

            #recupera todas as permissões dos modelos do app
            try:
                module = get_app(app)
                for model in get_models(module):
                    for permissao in model._meta.permissions:
                        module_permissions.append(u'%s.%s.%s' % (app, model.__name__.lower(), permissao[0]))
            except:
                pass

        #verfica se tem alguma permissao no xml mas não no modelo
        permissao_xml = False
        for grupo in permissoes:
            if grupo:
                for permissao in grupo:
                    permissoes_list.append(permissao)
                    if permissao not in module_permissions and '.add_' not in permissao and '.edit_' not in permissao and '.delete_' not in permissao and '.change_' not in permissao:
                        if not permissao_xml:
                            self.stderr.write(u'>>> Permissões no xml inexistentes no modelo:')
                            permissao_xml = True
                        self.stderr.write(permissao)

        #verifica se tem alguma permissao no modelo mas não no xml
        permissao_modelo = False
        for permissao in module_permissions:
            if permissao not in permissoes_list and '.add_' not in permissao and '.edit_' not in permissao and '.delete_' not in permissao and '.change_' not in permissao:
                if options['verbosity'] in ['2', '3']:
                    if not permissao_modelo:
                        self.stdout.write(termcolors.make_style(fg = 'yellow', opts = ('bold',))(u'>>> Permissões no modelo inexistentes no xml:'))
                        permissao_modelo = True
                    self.stdout.write(permissao)

        self.limpar_permissoes_dos_grupos(group_permission)
        self.sync_groups_and_permissions(group_permission.obter_dicionario())

        for nome_app, app in group_permission.apps.items():
            for nome_grupo in app.grupos:
                grupo = Group.objects.get(name=nome_grupo)
                self.grupos_no_permisions_xml.append(grupo.id)

        if options['verbosity'] != '0':
            if Group.objects.exclude(id__in=self.grupos_no_permisions_xml).exists():
                self.stdout.write(termcolors.make_style(fg = 'yellow')(u'[warning] grupos não existentes nos permissions.xml: %s' % list(Group.objects.exclude(id__in=self.grupos_no_permisions_xml).values_list('id', 'name'))))
            self.stdout.write(termcolors.make_style(fg = 'green')(u'[sync_permissions] finished'))
    
    def processar_group_permission(self, app, apps, options, groupPermission):
        permissoes = []
        if len(apps) == 0 or app in apps:
            permissionFileName = '%s/permissions.xml' % app
            if isfile(permissionFileName) and (len(apps) == 0 or app in apps):
                if options['verbosity'] in ('2', '3'):
                    self.stdout.write(termcolors.make_style(fg = 'yellow')(u'Processing %s' % permissionFileName))
                permissoes = groupPermission.processar(permissionFileName, app)
        return permissoes
            
    def limpar_permissoes_dos_grupos(self, group_permission):
        """
        Remove todas as permissões dos grupos para que após o processamento eles só tenham as permissões definidas nos permissions.xml
        """
        for grupo in group_permission.obter_grupos():
            nome_grupo = grupo.nome
            grupo = Group.objects.filter(name=nome_grupo)
            if grupo.exists():
                grupo = grupo[0]
                grupo.permissions.clear()

    def sync_groups_and_permissions(self, data):
        """
        Syncronize groups and permissions.
        Group is created if not exists. Permissions must already exists.

        ``data`` format:
        {'<group_name>': ['<ct_app_label>.<ct_model>.<p_codename>']}

        Example of ``data``:
        {'operators': [
            'blog.article.add_article', ''blog.article.change_article'],
         'admins':
            ['blog.article.add_article', 'blog.article.change_article', 'blog.article.delete_article']
        }
        """
        def get_perm(p):
            """
            ``p`` format: '<ct_app_label>.<ct_model>.<p_codename>'
            """
            try:
                ct_app_label, ct_model, p_codename = p.split('.')
            except ValueError:
                raise ValueError(u'Value must be in format "<ct_app_label>.<ct_model>.<p_codename>". Got "%s"' % p)
            try:
                return Permission.objects.get(content_type__app_label = ct_app_label,
                                              content_type__model     = ct_model,
                                              codename                = p_codename)
            except Permission.DoesNotExist:
                raise Permission.DoesNotExist(u'Permission "%s" does not exist.' % p)

        for group_name, perms in data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for p in perms:
                try:
                    perm = get_perm(p)
                    group.permissions.add(perm)
                except Permission.DoesNotExist, e:
                    print e