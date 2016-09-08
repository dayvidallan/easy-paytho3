# -*- coding: utf-8 -*-
from django.forms.widgets import HiddenInput, SelectMultiple, TextInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from newadmin.utils import ChainedMultipleSelectWidget, randomic, dumps_qs_query
import json

class TransferSelectWidget(SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        options = []
        for choice in self.choices:
            options.append('{value:"%s", content:"%s"}' % (choice[0], choice[1]))
        selected = []
        if value:
            for pk in value:
                selected.append('"%s"' % pk)
        s = u'''
        <div id="__%s"></div>
        <script>
            $(function() {
                var t = $('#__%s').bootstrapTransfer(
                    {'target_id': '%s',
                     'height': '15em',
                     'hilite_selection': true});
                t.populate([%s]);
                t.set_values([%s]);
                //console.log(t.get_values());
            });
        </script>
        ''' % (name, name, name, ', '.join(options), ', '.join(selected))
        return mark_safe(s)


class ChainedTransferSelectWidget(ChainedMultipleSelectWidget):

    def render(self, name, value, attrs=None, choices=()):
        context = self.get_context(name, value, attrs, choices)
        context['name'] = name
        html = '<div id="__%s"></div>' % name
        output = [html, render_to_string('transferselect_widget.html', context)]
        return mark_safe('\n'.join(output))


class PhotoCaptureInput(HiddenInput):
    def render(self, name, value, attrs=None):
        s = u"""

        <div align="center">
            <video autoplay style="display:none;"></video>
            <canvas id="canvas" width="300" height="400"></canvas>
            <br>
            <input type="button" id="cancel" value="Cancelar" class="btn default">
            &nbsp;&nbsp;
            <input type="button" id="snapshot" value="Fotografar" class="btn primary">
        </div>

	<script language='javascript'>
		var video = document.querySelector("video");
		var canvas = document.querySelector("canvas");
		var canvas_visible = canvas.offsetParent != null;
		var ctx = canvas.getContext('2d');
		var t;
		var c = 0;

        if (canvas_visible){
		    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;

    		if (navigator.getUserMedia) {
	    		navigator.getUserMedia({video: true}, handleVideo, videoError);
		    }
        }

		function handleVideo(stream) {
		    var createObjectURL = (window.URL || window.webkitURL || {}).createObjectURL || function(){};
			video.src = createObjectURL(stream);
		}

		function videoError(e) {
			ctx.font="20px Georgia";
			ctx.fillText("Nenhuma camera encontrada!",10,50);
		}
		function crop(){
			var sourceX = 200;
			var sourceY = 0;
			var sourceWidth = 300;
			var sourceHeight = 400;
			var destWidth = sourceWidth;
			var destHeight = sourceHeight;
			var destX = canvas.width / 2 - destWidth / 2;
			var destY = canvas.height / 2 - destHeight / 2;

			ctx.drawImage(video, sourceX, sourceY, sourceWidth, sourceHeight, destX, destY, destWidth, destHeight);
		}
		function snapshot() {
			if(c == 0){
				crop();
				t = setTimeout("snapshot()", 100);
			}
		}

		if (canvas_visible){
            document.querySelector('#snapshot').onclick = function() {
                if(c == 0){
                    c = 1;
                    crop();
                    clearTimeout(t);
                    var dataURL = canvas.toDataURL();
                    hidden = document.querySelector("#id_%s");
                    hidden.value=dataURL;
                }
            }
            document.querySelector('#cancel').onclick = function() {
                if(c == 1){
                    c = 0;
                    hidden = document.querySelector("#id_%s");
                    hidden.value='';
                    snapshot();
                }
            }
		    snapshot();
		}
	</script>
        """ % (name, name)
        return mark_safe(s) + super(PhotoCaptureInput, self).render(name, value, attrs)


BASE_SEARCH_URL = 'autocompletar'
def get_search_url(cls):
    data = dict(base_search_url=BASE_SEARCH_URL, app_label=cls._meta.app_label,
                model_label=cls.__name__.lower())
    return '/%(base_search_url)s/%(app_label)s/%(model_label)s/' % data

def get_change_list_url(cls):
    data = dict(app_label=cls._meta.app_label, model_name=cls.__name__.lower())
    return '/admin/%(app_label)s/%(model_name)s/' % data

def get_add_another_url(cls):
    data = dict(app_label=cls._meta.app_label, model_name=cls.__name__.lower())
    return '/admin/%(app_label)s/%(model_name)s/add/' % data


ALL_AUTOCOMPLETE_OPTIONS = (
    'matchCase',
    'matchContains',
    'mustMatch',
    'minChars',
    'selectFirst',
    'extraParams',
    'formatItem',
    'formatMatch',
    'formatResult',
    'multiple',
    'multipleSeparator',
    'width',
    'autoFill',
    'max',
    'highlight',
    'scroll',
    'scrollHeight'
)

DEFAULT_AUTOCOMPLETE_OPTIONS = dict(autoFill=True, minChars=2, scroll=False, extraParams=dict())

def set_autocomplete_options(obj, options):
    options = options or dict()
    for option in options.keys():
        if option not in ALL_AUTOCOMPLETE_OPTIONS:
            raise ValueError(u'Autocomplete option error: "%s" not in %s' \
                % (option, ALL_AUTOCOMPLETE_OPTIONS))
    new_options = DEFAULT_AUTOCOMPLETE_OPTIONS.copy()
    new_options.update(options)
    obj.options = json.dumps(new_options)

class AutocompleteWidget(TextInput):
    """
    Widget desenvolvido para ser utilizado com field ``forms.ModelChoiceField``.
    View Ajax default: djtools.utils.autocomplete_view
    """
    # TODO: mover scripts do template ``autocomplete_widget.html`` para arquivo js.
    class Media:
        js = (
            "/static/base/js/jquery.autocomplete.js",
            "/static/base/js/jquery.bgiframe.min.js",
            "/static/admin/js/admin/RelatedObjectLookups.js",
        )
        css = {'all': ("/static/base/js/jquery.autocomplete.css",)}

    def __init__(self, url=None, id_=None, attrs=None, show=True, help_text=None,
                 readonly=False, side_html=None, label_value=None, form_filters=None,
                 search_fields=None, manager_name=None, qs_filter=None, can_add_related=True,
                 submit_on_select=False, **options):
        self.can_add_related = can_add_related
        self.help_text = help_text
        self.show = show
        self.attrs = attrs and attrs.copy() or {}
        self.id_ = id_ or randomic()
        self.url = url
        self.readonly = readonly
        self.side_html = side_html
        self.form_filters = form_filters
        self.submit_on_select = submit_on_select

        options['extraParams'] = options.get('extraParams', {})

        if readonly:
            options['extraParams']['readonly'] = 1

        if label_value:
            options['extraParams']['label_value'] = label_value
        if form_filters:
            if not isinstance(form_filters, (tuple, list)):
                raise ValueError('`form_filters` deve ser lista ou tupla')
            options['extraParams']['form_parameter_names'] = u','.join([i[0] for i in form_filters])
            options['extraParams']['django_filter_names'] = u','.join([i[1] for i in form_filters])

        if search_fields:
            if not isinstance(search_fields, (tuple, list)):
                raise ValueError('`search_fields` deve ser lista ou tupla')
            options['extraParams']['search_fields'] = u','.join(search_fields)
        if manager_name:
            if not isinstance(manager_name, basestring):
                raise ValueError('`manager_name` deve ser basestring')
            options['extraParams']['manager_name'] = manager_name
        if qs_filter:
            if not isinstance(qs_filter, basestring):
                raise ValueError('`qs_filter` deve ser basestring')
            options['extraParams']['qs_filter'] = qs_filter
        if 'ext_combo_template' in options['extraParams']:
            #http://stackoverflow.com/questions/1253528/is-there-an-easy-way-to-pickle-a-python-function-or-otherwise-serialize-its-cod#answers-header
            #serializa a função
            import marshal
            code_string = marshal.dumps(options['extraParams'].pop('ext_combo_template').func_code)
            code_string = dumps_qs_query(code_string)
            options['extraParams']['ext_combo_template'] = code_string

        set_autocomplete_options(self, options)
        super(AutocompleteWidget, self).__init__(self.attrs)


    def render(self, name, value=None, attrs={}):
        model_cls = self.choices.queryset.model
        value = value or ''
        if not isinstance(value, (basestring, int, model_cls)):
            raise ValueError('value must be basestring, int or a models.Model instance. Got %s.' % value)
        if isinstance(value, model_cls):
            value = value.pk
        self.url = self.url or get_search_url(model_cls)

        context = dict(id                    = self.id_,
                       value                 = value,
                       options               = self.options,
                       form_filters          = self.form_filters,
                       name                  = name,
                       url                   = self.url,
                       change_list_url       = get_change_list_url(model_cls),
                       add_another_url       = get_add_another_url(model_cls),
                       # has_change_permission = has_change_permission(model_cls),
                       # has_add_permission    = has_add_permission(model_cls),
                       has_change_permission = False,
                       has_add_permission    = False,
                       side_html             = self.side_html,
                       readonly              = self.readonly,
                       attrs                 = self.attrs,
                       show                  = self.show,
                       control               = dumps_qs_query(self.choices.queryset.all().query),
                       help_text             = self.help_text,
                       submit_on_select      = self.submit_on_select,
                       can_add_related       = self.can_add_related,
        )

        output = render_to_string('base/templates/autocomplete_widget.html',
                                  context)
        return mark_safe(output)