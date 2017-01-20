# coding: utf-8
#
# from django.contrib.auth import get_permission_codename
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.models import Permission
#
# from django.db import DEFAULT_DB_ALIAS
# from django.db.models import signals
#
#
# def create_newadmin_permissions(app_config, verbosity=2, interactive=True, using=DEFAULT_DB_ALIAS, **kwargs):
#
#     for klass in app_config.get_models():
#         perm_label = 'view'
#         content_type = ContentType.objects.db_manager(using).get_for_model(klass)
#         codename = get_permission_codename(perm_label, klass._meta)
#         name = 'Can %s %s' % (perm_label, klass._meta.verbose_name_raw)
#         if not Permission.objects.filter(codename=codename, content_type=content_type).update(name=name):
#             Permission.objects.create(name=name, codename=codename, content_type=content_type)
#
# signals.post_migrate.connect(create_newadmin_permissions, dispatch_uid="newadmin.create_newadmin_permissions")