# -*- coding: utf-8 -*-

from rest_framework import serializers
from base.models import Pregao


class PregaoSerializer(serializers.ModelSerializer):
  modalidade = serializers.CharField(source='modalidade.nome')
  class Meta:
        model = Pregao
        fields = ('id', 'modalidade', 'objeto', 'num_pregao')