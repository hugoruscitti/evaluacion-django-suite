# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-22 16:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0027_auto_20170622_1315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='perfil',
            old_name='programa',
            new_name='Contrato',
        ),
    ]
