# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-20 15:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0024_estadodepaquete_paquete'),
    ]

    operations = [
        migrations.RenameField(
            model_name='perfil',
            old_name='grupo',
            new_name='group',
        ),
    ]
