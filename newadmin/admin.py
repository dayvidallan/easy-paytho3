# coding: utf-8

from functools import update_wrapper

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin, csrf_protect_m
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db import models
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
import xlwt

from newadmin.utils import DateTimeFormField, DateFormField


def XlsResponse(rows, filename='relatorio'):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % filename
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet(filename)
    for row_idx, row in enumerate(rows):
        for col_idx, col in enumerate(row):
            sheet.write(row_idx, col_idx, label=col)
    wb.save(response)
    return response


class NewModelAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.DateField: {'form_class': DateFormField},
        models.DateTimeField: {'form_class': DateTimeFormField},
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }

    def has_change_permission(self, request, obj=None):
        has_edit_perm = super(NewModelAdmin, self).has_change_permission(request, obj)
        if obj:  # Checando permissão default change_model
            return has_edit_perm
        else:  # Checando permissão view_model
            view_perm = '%s.view_%s' % (self.model._meta.app_label, self.model.__name__.lower())
            return has_edit_perm or request.user.has_perm(view_perm)

    def get_options(self, request):
        options = []
        if self.has_add_permission(request):
            icon = u'<span class="fa fa-plus"></span>'
            options.append(dict(label=u'%s Adicionar %s' % (icon, self.model._meta.verbose_name),
                                url=u'/admin/%s/%s/add/' % (self.model._meta.app_label,
                                                            self.model.__name__.lower())))
        return options

    def get_actions(self, request):
        actions = super(NewModelAdmin, self).get_actions(request)
        if not self.has_delete_permission(request, obj=None) and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def admin_view(self, view, cacheable=False, perm=None):
        """
        Adaptado de ``django.contrib.admin.sites.AdminSite.admin_view`` e adiciona o parâmetro
        ``perm``, que restringe o acesso por meio de ``user.has_perm(perm)``.
        """
        def inner(request, *args, **kwargs):
            if (not self.admin_site.has_permission(request)) or (perm and not request.user.has_perm(perm)):
                if request.path == reverse('admin:logout', current_app=self.admin_site.name):
                    index_path = reverse('admin:index', current_app=self.admin_site.name)
                    return HttpResponseRedirect(index_path)
                return self.admin_site.login(request)
            return view(request, *args, **kwargs)

        if not cacheable:
            inner = never_cache(inner)
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        extra_context['options'] = self.get_options(request)

        # Tratamento do as_xls
        if hasattr(self, 'as_xls'):
            as_xls_url = request.get_full_path()
            if '?' not in as_xls_url:
                as_xls_url += '?'
            if not as_xls_url.endswith('?'):
                as_xls_url += '&'
            extra_context['options'].append(dict(label=u'<i class="fa fa-file-excel-o"></i> Exportar', url=as_xls_url + 'as_xls=1'))
            if 'as_xls' in request.GET:
                request.GET._mutable = True
                del request.GET['as_xls']
                ctx = super(NewModelAdmin, self).changelist_view(request, extra_context).context_data
                return XlsResponse(rows=self.as_xls(request, ctx['cl'].get_queryset(request)), filename='sheet')

        # Retorno padrão
        return super(NewModelAdmin, self).changelist_view(request, extra_context)

    def get_changelist(self, request, **kwargs):
        """Torna o ``request`` disponível em métodos invocados no changelist."""
        self.request = request
        return super(NewModelAdmin, self).get_changelist(request, **kwargs)


class UserNewAdmin(UserAdmin, NewModelAdmin):

    def show_get_full_name(self, obj):
        return obj.get_full_name()
    show_get_full_name.admin_order_field = 'first_name'
    show_get_full_name.short_description = u'Nome'

    formfield_overrides = {
        models.DateTimeField: {'form_class': DateTimeFormField},
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }
    list_display = ('username', 'email', 'show_get_full_name', 'last_login', 'is_active', 'is_staff')
    list_editable = ('is_active', 'is_staff')
    filter_horizontal = ()

if admin.site.is_registered(get_user_model()):
    admin.site.unregister(get_user_model())

admin.site.register(get_user_model(), UserNewAdmin)


class GroupNewAdmin(GroupAdmin, NewModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
    }
    filter_horizontal = ()

if admin.site.is_registered(Group):
    admin.site.unregister(Group)

admin.site.register(Group, GroupNewAdmin)
