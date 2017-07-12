# -*- coding: utf-8 -*-
from django.db.models.deletion import Collector
from django.core import serializers
from django.core.management.base import BaseCommand
import pdb

def dump(qs):
    l = []
    c = []
    collector = Collector('default')
    def dump_related_objects(instance):
        if instance.__class__.__name__ not in ['Log', 'RegistroDiferenca'] and instance not in l:
            l.append(instance)
            if instance.__class__.__name__ not in c:
                c.append(instance.__class__.__name__)

            related_fields = [
                f for f in instance.__class__._meta.get_fields(include_hidden=True)
                if (f.one_to_many or f.one_to_one)
                and f.auto_created and not f.concrete
            ]

            qs = instance.__class__.objects.filter(pk=instance.pk)
            for related_field in related_fields:
                objs = collector.related_objects(related_field, qs)
                for obj in objs:
                    if obj not in l:
                        dump_related_objects(obj)
    for instance in qs:
        print 'carregando', instance.pk, instance
        dump_related_objects(instance)
    return c, l

class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = None
        print u'\nPor favor, instancie o queryset que você deseja salvar e em seguida digite a tecla "c".\nÉ necessário importar os modelos necessários.\n\tEx: from edu.models import Aluno\n\tqueryset = Aluno.objects.filter(ano_letivo__ano=2015)\n\n'
        pdb.set_trace()
        c, l = dump(queryset)
        print u'Um arquivo "backup.json" foi salvo no diretório corrente contendo %s objetos. Para restaurá-los, digite o seguinte comando:\n\n\tpython manage.py restore %s < backup.json\n\nÉ necessário ordenar as classes corretamente de acordo com as dependências entre elas.\n\n' % (len(l) , ' '.join(c))
        f = open('backup.json', 'w')
        f.write(serializers.serialize("json", l))
        f.close()

