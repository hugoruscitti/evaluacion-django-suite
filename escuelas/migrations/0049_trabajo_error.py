# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-02-22 02:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0048_trabajo'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajo',
            name='error',
            field=models.CharField(default='', max_length=256),
        ),
    ]
