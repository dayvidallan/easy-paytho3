# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from base.models import User
from django.contrib.auth.hashers import get_hasher, make_password

class Command(BaseCommand):
    def handle(self, *args, **options):
        updates = 0
        hasher=get_hasher('unsalted_md5')
        password =  make_password('456', '', hasher)
        updates = User.objects.update(password=password)
        print self.style.SQL_COLTYPE('%d passwords changed to "456"' % updates)
        self.stdout.write('Successfully %d passwords changed to 456"' % updates)
