# -*- coding: utf-8 -*-
import base64
from django.forms import fields
from django.forms.models import ModelMultipleChoiceField

from base.formwidgets import PhotoCaptureInput, TransferSelectWidget, ChainedTransferSelectWidget
from newadmin.utils import ChainedModelMultipleChoiceField


class TransferSelectField(ModelMultipleChoiceField):
    widget = TransferSelectWidget


class ChainedTransferSelectField(ChainedModelMultipleChoiceField):
    widget = ChainedTransferSelectWidget


class PhotoCaptureField(fields.Field):
    widget = PhotoCaptureInput

    def to_python(self, value):
        if value:
            return base64.b64decode(value.split(',')[1])
        else:
            return None
