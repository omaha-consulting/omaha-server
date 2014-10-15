#!/usr/bin/env python
# coding: utf8

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if User.objects.count() == 0:
    admin = User.objects.create(username='admin', email='admin@example.com',
                                first_name='Admin', last_name='Admin')
    admin.set_password('admin')
    admin.is_superuser = True
    admin.is_staff = True
    admin.save()
