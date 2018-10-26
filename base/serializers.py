# -*- coding: utf-8 -*-

from rest_framework import serializers
from base.models import Pregao, AtaRegistroPreco


class PregaoSerializer(serializers.ModelSerializer):
  modalidade = serializers.CharField(source='modalidade.nome')


  class Meta:
        model = Pregao
        fields = ('id', 'modalidade', 'objeto', 'num_pregao', 'hora_abertura', 'data_abertura', 'local')


class ARPSerializer(serializers.ModelSerializer):


  class Meta:
        model = AtaRegistroPreco
        fields = ('id', 'numero', 'data_inicio', 'data_fim', )