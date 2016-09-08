# coding: utf-8

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
import magic


class FileValidator(object):
    def __init__(self, mimetypes=None, max_size=None):
        self.mimetypes = mimetypes
        self.max_size = max_size

    def get_mimetype_erro_msg(self, mimetype):
        msg_singular = u'Por favor, anexe um arquivo no formato %s (o formato recebido foi %s).'
        msg_plural = u'Por favor, anexe um arquivo num dos formatos: %s (o formato recebido foi %s).'
        if len(self.mimetypes) == 1:
            return msg_singular % (self.mimetypes[0], mimetype)
        else:
            return msg_plural % (u', '.join(self.mimetypes), mimetype)

    def __call__(self, value):
        if self.mimetypes:
            mimetype = magic.from_buffer(value.read(1024), mime=True)
            if mimetype not in self.mimetypes:
                raise ValidationError(self.get_mimetype_erro_msg(mimetype))

        if self.max_size:
            filesize = len(value)
            if filesize > self.max_size:
                raise ValidationError(u'Por favor, anexe um arquivo com até %s (o arquivo recebido tem %s)'
                                      % (filesizeformat(self.max_size), filesizeformat(filesize)))
