# coding: utf-8
import os

from django.apps import apps
from django.conf import settings
from django import forms
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

from newadmin.utils import loads_qs_query, JsonResponse


class UploadFileForm(forms.Form):
    file = forms.FileField(label=u'Adicionar arquivo')

    @staticmethod
    def handle_uploaded_file(f, path):
        with open(os.path.join(path, f.name), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


def media(request):
    path = request.GET.get('path', '')
    title = u'Arquivos em ' + path
    path = os.path.join(settings.MEDIA_ROOT, path)
    files = []
    for fname in os.listdir(path):
        if fname.startswith('.'):
            continue
        fpath = os.path.join(path, fname)
        is_file = os.path.isfile(fpath)
        if is_file:  # link para baixar arquivo
            url = settings.MEDIA_URL + fpath.replace(settings.MEDIA_ROOT, '')[1:]
        else:  # link para essa view
            url = u'/newadmin/media?path=' + fpath.replace(settings.MEDIA_ROOT, '')[1:]
        files.append(dict(label=fname, url=url, is_file=is_file))

    form = UploadFileForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        UploadFileForm.handle_uploaded_file(request.FILES['file'], path)
        messages.success(request, u'Arquivo adicionado com sucesso!')
        return HttpResponseRedirect(request.get_full_path())
    return render_to_response('media.html', locals(), RequestContext(request))


@csrf_exempt
def chained_select_view(request, app_name, class_name):
    """
    Gereric chained select view
    =========================
    `request.POST` expected args: 'chained_attr', 'id', 'label'
    """
    cls = apps.get_model(app_name, class_name)
    data = request.POST or request.GET
    label = data.get('label')
    control = data.get('control')

    qs = cls.objects.all()
    if control:
        qs.query = loads_qs_query(control)

    if 'django_filter_names' in data and 'filter_pks' in data:
        django_filter_names = data['django_filter_names'].split(',')
        filter_pks = data['filter_pks'].split(',')
        for i, elem in enumerate(filter_pks):
            if elem and django_filter_names[i].endswith('__in'):
                filter_pks[i] = elem.split(';')
    else:
        django_filter_names = None
        filter_pks = None

    depends = {}
    if( django_filter_names and filter_pks ):
        list_depends = zip(django_filter_names, filter_pks)
        for item in list_depends:
            if item[0] and item[1]:
                depends[item[0]] = item[1]
        if depends:
            qs = qs.filter(**depends).distinct()

    qs_filter = data.get('qs_filter', None)
    if qs_filter:
        filters = {}
        qs_filters = qs_filter.split(',')
        for qs_filter in qs_filters:
            k, v = qs_filter.split('=')
            k = k.strip()
            v = v.strip()
            if v == 'False':
                v = False
            elif v == 'True':
                v = True
            else:
                qs_filter_value = data.get('qs_filter_params_map[%s]'%v, None)
                if qs_filter_value:
                    v = qs_filter_value
            filters[k] = v

        qs = qs.filter(**filters)
    return JsonResponse(list(qs.distinct().values('id', label)))
