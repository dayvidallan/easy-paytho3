import sys
from collections import OrderedDict

from django.core import serializers
from django.db.transaction import atomic

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='*', type=str)

    @atomic
    def handle(self, models, **options):
        data = OrderedDict()
        for arg in models:
            data[arg] = []
        s = sys.stdin.read()
        for obj in serializers.deserialize("json", s):
            data[obj.object.__class__.__name__].append(obj.object)

        for key in data:
            print(key, len(data[key]))
            for obj in data[key]:
                obj.save()
